"""
Tests for the collapsed AI service.

Covers:
- Unit tests with a mocked Anthropic client (no network, always run)
- Opt-in integration tests against the real z.ai endpoint, gated on
  ZAI_API_KEY being set in the environment
"""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services import ai_service as ai_service_module
from app.services.ai_service import AIService


# ---------------------------------------------------------------------------
# Unit tests (mocked client)
# ---------------------------------------------------------------------------

def _make_fake_response(text: str) -> SimpleNamespace:
    """Build a minimal object that looks like an Anthropic Messages response."""
    block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[block])


@pytest.fixture
def svc_with_fake_client(monkeypatch):
    """Return an AIService whose _get_client returns a MagicMock."""
    svc = AIService()
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _make_fake_response("mock output")
    monkeypatch.setattr(svc, "_get_client", lambda: fake_client)
    return svc, fake_client


class TestTranslate:
    @pytest.mark.asyncio
    async def test_returns_text_from_anthropic_response(self, svc_with_fake_client):
        svc, _ = svc_with_fake_client
        result = await svc.translate_crochet_pattern("ch 4, sc in 2nd ch from hook")
        assert result == "mock output"

    @pytest.mark.asyncio
    async def test_uses_default_sonnet_model(self, svc_with_fake_client):
        svc, fake_client = svc_with_fake_client
        await svc.translate_crochet_pattern("ch 4")
        call_kwargs = fake_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-5-20250929"
        assert call_kwargs["system"].startswith(
            "You are an expert crochet and knitting instructor"
        )

    @pytest.mark.asyncio
    async def test_returns_config_error_when_no_api_key(self, monkeypatch):
        svc = AIService()
        monkeypatch.setattr(svc, "_get_client", lambda: None)
        result = await svc.translate_crochet_pattern("yo, sl st to close")
        assert "not configured" in result
        assert "ZAI_API_KEY" in result


class TestChat:
    @pytest.mark.asyncio
    async def test_returns_text_from_anthropic_response(self, svc_with_fake_client):
        svc, _ = svc_with_fake_client
        result = await svc.chat_about_pattern("What does sc2tog mean?")
        assert result == "mock output"

    @pytest.mark.asyncio
    async def test_includes_chat_history_and_context(self, svc_with_fake_client):
        svc, fake_client = svc_with_fake_client
        await svc.chat_about_pattern(
            message="What's next?",
            project_context="granny square blanket",
            chat_history="User: how do I start?\nAI: make a magic ring",
        )
        call_kwargs = fake_client.messages.create.call_args.kwargs
        content = call_kwargs["messages"][0]["content"]
        # content should be a list with a final text block holding prompt
        text_block = next(c for c in content if c["type"] == "text")
        assert "granny square blanket" in text_block["text"]
        assert "magic ring" in text_block["text"]
        assert "What's next?" in text_block["text"]

    @pytest.mark.asyncio
    async def test_reports_missing_api_key(self, monkeypatch):
        svc = AIService()
        monkeypatch.setattr(svc, "_get_client", lambda: None)
        result = await svc.chat_about_pattern("hi")
        assert "ZAI_API_KEY" in result

    @pytest.mark.asyncio
    async def test_image_data_produces_image_block(self, svc_with_fake_client):
        """Image data should be decoded into an Anthropic image content block."""
        svc, fake_client = svc_with_fake_client
        # 1x1 PNG (base64 of a minimal valid PNG)
        png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB"
            "0C8AAAAASUVORK5CYII="
        )
        import json

        await svc.chat_about_pattern(
            message="what is this?",
            image_data=json.dumps([png_b64]),
        )
        content = fake_client.messages.create.call_args.kwargs["messages"][0][
            "content"
        ]
        image_blocks = [c for c in content if c["type"] == "image"]
        assert len(image_blocks) == 1
        assert image_blocks[0]["source"]["media_type"] == "image/png"


class TestCompatShims:
    """The GraphQL surface expects usage/config/reset methods to keep working."""

    def test_usage_stats_has_default_model(self):
        svc = AIService()
        stats = svc.get_usage_stats()
        assert "claude-sonnet-4-5-20250929" in stats

    def test_provider_config_reports_zai(self):
        svc = AIService()
        config = svc.get_ai_provider_config()
        assert config["current_provider"] == "zai"
        assert config["selected_model"] == "claude-sonnet-4-5-20250929"

    def test_set_ai_model_is_noop_but_successful(self):
        svc = AIService()
        result = svc.set_ai_model(model_name="some-other-model")
        assert result["success"] is True
        # Model selection is disabled; we always report the default
        assert result["selected_model"] == "claude-sonnet-4-5-20250929"

    def test_reset_daily_usage_succeeds(self):
        svc = AIService()
        result = svc.reset_daily_usage()
        assert result["success"] is True


class TestExtractText:
    def test_concatenates_text_blocks(self):
        resp = SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text="Hello "),
                SimpleNamespace(type="text", text="world"),
            ]
        )
        assert ai_service_module._extract_text(resp) == "Hello world"

    def test_ignores_non_text_blocks(self):
        resp = SimpleNamespace(
            content=[
                SimpleNamespace(type="tool_use", text=None),
                SimpleNamespace(type="text", text="keep me"),
            ]
        )
        assert ai_service_module._extract_text(resp) == "keep me"


# ---------------------------------------------------------------------------
# Integration tests (real z.ai endpoint) — opt-in via ZAI_API_KEY
# ---------------------------------------------------------------------------

pytestmark_integration = pytest.mark.skipif(
    not os.getenv("ZAI_API_KEY"),
    reason="ZAI_API_KEY not set; skipping integration tests against z.ai",
)


@pytestmark_integration
@pytest.mark.asyncio
async def test_live_translate_crochet_pattern():
    """Smoke-test against the real z.ai endpoint."""
    svc = AIService()
    result = await svc.translate_crochet_pattern(
        "Round 1: Ch 4, sl st to join to form ring. Ch 3, 11 dc in ring, sl st to top of ch-3. (12 dc)",
        user_context="beginner",
    )
    # Sanity: response should be a non-trivial string referring to crochet terms
    assert isinstance(result, str)
    assert len(result) > 100
    # Should expand abbreviations or describe stitches somehow
    assert any(
        term in result.lower()
        for term in ("double crochet", "chain", "slip stitch", "round")
    )


@pytestmark_integration
@pytest.mark.asyncio
async def test_live_chat_about_pattern():
    svc = AIService()
    result = await svc.chat_about_pattern(
        message="What does sc2tog mean in crochet?",
    )
    assert isinstance(result, str)
    assert len(result) > 50
    assert "single crochet" in result.lower() or "decrease" in result.lower()
