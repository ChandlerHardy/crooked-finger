"""
AI service for Crooked Finger.

Uses a single Anthropic SDK client pointed at z.ai's Anthropic-compatible
proxy. Behind the scenes z.ai routes Anthropic model IDs to GLM models:
- claude-sonnet-4-5-20250929 -> GLM-4.7 (high quality, default)
- claude-haiku-4-5-20251001  -> GLM-4.5-Air (medium quality)

The previous Gemini/OpenRouter cascade (8 provider methods, smart routing,
fallback chains, per-model quota tracking) has been collapsed into a single
client because z.ai handles routing internally.

The GraphQL surface (usage dashboard, provider config, set-model, reset-usage)
is preserved as no-op / single-model stubs so the frontend does not need to
change in this phase.
"""
from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from app.core.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# z.ai exposes the Anthropic Messages API at this path. The `/v1/messages`
# suffix is appended by the Anthropic SDK itself, so we stop at `/anthropic`.
ZAI_BASE_URL = "https://api.z.ai/api/anthropic"

# Default model used for all calls. z.ai routes this to GLM-4.7 internally.
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

# Token budgets. Anthropic requires max_tokens; picking generous limits that
# match the old behavior (Gemini calls had no explicit cap and returned full
# long-form responses for pattern translation).
MAX_TOKENS_TRANSLATE = 4096
MAX_TOKENS_CHAT = 4096


# ---------------------------------------------------------------------------
# System prompts (preserved verbatim from the Gemini implementation so that
# output quality/voice does not regress).
# ---------------------------------------------------------------------------

TRANSLATE_SYSTEM_PROMPT = """You are an expert crochet and knitting instructor. Your job is to translate standard crochet and knitting notation into clear, easy-to-follow instructions for beginners and intermediate crafters.

Rules for translation:
- Expand all abbreviations (sc = single crochet, dc = double crochet, k = knit, p = purl, etc.)
- Break down complex instructions into numbered steps
- Explain stitch counts and placement clearly
- Add helpful tips for tricky techniques
- Use encouraging, friendly language
- Include warnings about common mistakes"""

CHAT_SYSTEM_PROMPT = """You are a friendly, expert crochet and knitting instructor and pattern designer. Help users with:
- Crochet and knitting technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn, fiber, and hook/needle recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments
- Converting between crochet and knitting patterns when possible

Format your responses with clear paragraph breaks for readability.

When users ask for visual diagrams or charts, provide a detailed written description of the pattern. The system will automatically generate a visual SVG diagram alongside your response when pattern data is detected.

Always be encouraging and provide practical, actionable advice."""

IMAGE_CHAT_SYSTEM_PROMPT = """You are an expert crochet and knitting instructor and pattern designer. Analyze the image and extract the crochet or knitting pattern.

Format your response EXACTLY like this example (do NOT use numbered lists):

NAME: Cat's Cradle Blanket
NOTATION: Foundation Chain: Ch 122. Row 1: Dc in 3rd ch from hook and in each ch across, ch 2, turn - 120 dc. Row 2: Dc in 1st st, *Fpdc around the next 2 sts, Bpdc around the next 2 sts; rep from * to last st, dc in last st, ch 2, turn.
INSTRUCTIONS:
Round 1: Make a magic ring. Chain 2, work 12 double crochet into the ring. Pull the ring tight and slip stitch to join.

Round 2: Chain 2. Work 2 double crochet in each stitch around (24 stitches total). Slip stitch to join.

Round 3: Chain 2. *Work 1 double crochet in the next stitch, then 2 double crochet in the following stitch.* Repeat from * to * around (36 stitches total). Slip stitch to join.

DIFFICULTY: beginner
MATERIALS: Worsted weight yarn (4), 5.5mm (I) crochet hook
TIME: 2-3 hours

CRITICAL FORMATTING RULES:
- Do NOT number your response (no "1.", "2.", "3.")
- Do NOT use markdown bold (**text**)
- Put TWO line breaks between each round in INSTRUCTIONS
- Write INSTRUCTIONS as complete sentences, not abbreviated notation
- Separate each major section with blank lines
- Use the exact header format: "NAME:", "NOTATION:", "INSTRUCTIONS:", etc."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_mime_type(data: bytes) -> str:
    """Detect an image mime type from its magic bytes.

    Anthropic image blocks only accept image/* types. PDFs are rejected;
    callers should convert to images beforehand. If we get a PDF here we
    return "image/jpeg" to let Anthropic produce a useful error rather than
    silently dropping the data.
    """
    if data[:2] == b"\xff\xd8":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    logger.warning(
        "Unknown image type, defaulting to image/jpeg. First bytes: %s",
        data[:10].hex(),
    )
    return "image/jpeg"


def _build_image_blocks(image_data: Optional[str]) -> List[Dict[str, Any]]:
    """Turn a JSON array of base64 image strings into Anthropic image blocks."""
    if not image_data:
        return []
    try:
        image_list = json.loads(image_data)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse image_data JSON: %s", exc)
        return []

    blocks: List[Dict[str, Any]] = []
    for img_b64 in image_list:
        try:
            img_bytes = base64.b64decode(img_b64)
        except (base64.binascii.Error, ValueError) as exc:
            logger.warning("Failed to decode base64 image: %s", exc)
            continue
        blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": _detect_mime_type(img_bytes),
                    "data": img_b64,
                },
            }
        )
    return blocks


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AIService:
    """Thin wrapper around the Anthropic SDK pointed at z.ai.

    Retains the old public surface that GraphQL resolvers depend on, but the
    AI work is now a single code path.
    """

    def __init__(self) -> None:
        self._client: Optional[Anthropic] = None
        self._default_model = DEFAULT_MODEL

    # -- client ----------------------------------------------------------------

    def _get_client(self) -> Optional[Anthropic]:
        """Lazy-initialize the Anthropic client."""
        if self._client is not None:
            return self._client
        api_key = settings.zai_api_key
        if not api_key:
            logger.error("ZAI_API_KEY is not configured; AI calls will fail.")
            return None
        self._client = Anthropic(api_key=api_key, base_url=ZAI_BASE_URL)
        return self._client

    # -- public: translation ---------------------------------------------------

    async def translate_crochet_pattern(
        self, pattern_text: str, user_context: str = ""
    ) -> str:
        """Translate crochet/knitting notation into readable instructions."""
        client = self._get_client()
        if client is None:
            return _fallback_translation(pattern_text)

        user_prompt = (
            "Please translate this crochet or knitting pattern into clear, "
            "step-by-step instructions:\n\n"
            f"PATTERN:\n{pattern_text}\n\n"
            f"{f'CONTEXT: {user_context}' if user_context else ''}\n\n"
            "Provide detailed, beginner-friendly instructions."
        )

        try:
            response = client.messages.create(
                model=self._default_model,
                max_tokens=MAX_TOKENS_TRANSLATE,
                system=TRANSLATE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return _extract_text(response)
        except Exception as exc:  # noqa: BLE001 — surface error to UI
            logger.exception("z.ai translate call failed")
            return f"Error translating pattern: {exc}"

    # -- public: chat ----------------------------------------------------------

    async def chat_about_pattern(
        self,
        message: str,
        project_context: str = "",
        chat_history: str = "",
        image_data: Optional[str] = None,
    ) -> str:
        """Chat with AI about crochet/knitting patterns and techniques.

        Supports image analysis when `image_data` is a JSON array of base64
        strings.
        """
        client = self._get_client()
        if client is None:
            return "AI service not configured. Please set ZAI_API_KEY."

        user_analysis = rag_service.analyze_user_request(message)

        # Switch to the image-tuned system prompt when we're analyzing images.
        system_prompt = IMAGE_CHAT_SYSTEM_PROMPT if image_data else CHAT_SYSTEM_PROMPT

        context_info = ""
        if project_context:
            context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
        if chat_history:
            context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

        # RAG enhancement for diagram requests (unchanged from old behavior).
        if user_analysis.get("requests_diagram"):
            pattern_text = (
                message
                if any(pe in message.lower() for pe in ["round", "row", "chain", "dc", "sc"])
                else ""
            )
            if pattern_text:
                rag_enhancement = rag_service.enhance_pattern_context(
                    pattern_text, message
                )
                context_info += f"\n{rag_enhancement}\n"

        user_prompt = f"{context_info}\nUSER QUESTION: {message}"

        # Build content blocks: one text block plus any image blocks.
        content: List[Dict[str, Any]] = _build_image_blocks(image_data)
        content.append({"type": "text", "text": user_prompt})

        try:
            response = client.messages.create(
                model=self._default_model,
                max_tokens=MAX_TOKENS_CHAT,
                system=system_prompt,
                messages=[{"role": "user", "content": content}],
            )
            return _extract_text(response)
        except Exception as exc:  # noqa: BLE001
            logger.exception("z.ai chat call failed")
            return f"Sorry, I'm having trouble responding right now: {exc}"

    # -- public: GraphQL compatibility stubs -----------------------------------
    # These are called from queries.py / mutations.py. The cascade/quota
    # machinery is gone, but the GraphQL shape is preserved so the frontend
    # keeps working until Phase 3 housekeeping tears out the UI.

    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Return a single-model usage stat block.

        z.ai does not expose per-request quota headers through this endpoint,
        so we report effectively-unlimited and zero usage. The dashboard UI
        still renders cleanly.
        """
        return {
            self._default_model: {
                "current_usage": 0,
                "daily_limit": 999_999,
                "remaining": 999_999,
                "percentage_used": 0,
                "priority": 1,
                "use_case": "z.ai (GLM-4.7)",
                "total_input_characters": 0,
                "total_output_characters": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            }
        }

    def reset_daily_usage(self) -> Dict[str, Any]:
        """No-op: z.ai manages its own quotas."""
        from datetime import date

        return {
            "success": True,
            "message": "Usage tracking is managed by z.ai; nothing to reset.",
            "reset_date": date.today().isoformat(),
        }

    def get_ai_provider_config(self) -> Dict[str, Any]:
        """Return a single-model config payload."""
        return {
            "use_openrouter": False,
            "current_provider": "zai",
            "selected_model": self._default_model,
            "available_models": [self._default_model],
            "model_priority_order": [],
        }

    def set_ai_model(
        self,
        model_name: Optional[str] = None,
        priority_order: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """No-op: model is fixed to the z.ai default.

        Returns success with the single available model so frontend UX that
        POSTs updates does not error. Silently ignores input.
        """
        return {
            "success": True,
            "message": (
                "Model selection is disabled; z.ai routes all requests "
                f"through {self._default_model}."
            ),
            "use_openrouter": False,
            "current_provider": "zai",
            "selected_model": self._default_model,
            "model_priority_order": [],
        }


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _extract_text(response: Any) -> str:
    """Pull the text out of an Anthropic Messages response.

    Anthropic responses come back as a list of content blocks. We return the
    concatenation of all text blocks (usually just one).
    """
    parts: List[str] = []
    for block in getattr(response, "content", []) or []:
        # SDK returns objects with .type/.text; fall back to dict access for
        # anything returned by test fakes.
        block_type = getattr(block, "type", None) or (
            block.get("type") if isinstance(block, dict) else None
        )
        if block_type == "text":
            text = getattr(block, "text", None) or (
                block.get("text") if isinstance(block, dict) else None
            )
            if text:
                parts.append(text)
    return "".join(parts)


def _fallback_translation(pattern_text: str) -> str:
    """Basic abbreviation expansion used when ZAI_API_KEY is missing."""
    abbreviations = {
        "sc": "single crochet",
        "dc": "double crochet",
        "hdc": "half double crochet",
        "tc": "treble crochet",
        "sl st": "slip stitch",
        "ch": "chain",
        "st": "stitch",
        "sts": "stitches",
        "inc": "increase",
        "dec": "decrease",
        "yo": "yarn over",
        "sk": "skip",
        "rep": "repeat",
        "rnd": "round",
        "beg": "beginning",
        "sp": "space",
        "tog": "together",
    }
    translated = pattern_text
    for abbrev, full_form in abbreviations.items():
        translated = translated.replace(abbrev, full_form)
    return (
        "Basic translation (AI not available):\n\n"
        f"{translated}\n\n"
        "Note: This is a simple translation. For detailed instructions, "
        "please configure ZAI_API_KEY."
    )


# Global instance (maintained so existing imports keep working).
ai_service = AIService()
