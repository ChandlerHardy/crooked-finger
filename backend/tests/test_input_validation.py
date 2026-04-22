"""Tests for GraphQL input length validation.

Verifies that _validate_length rejects oversized payloads and that
every mutation with string inputs calls it before touching the database.
"""
import pytest
from unittest.mock import MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.schemas.mutations import (
    _validate_length,
    MAX_CHAT_MESSAGE_LENGTH,
    MAX_PATTERN_TEXT_LENGTH,
    MAX_SHORT_STRING_LENGTH,
    MAX_IMAGE_DATA_LENGTH,
)


# ---------------------------------------------------------------------------
# _validate_length unit tests
# ---------------------------------------------------------------------------

class TestValidateLength:
    """Unit tests for the _validate_length helper."""

    def test_none_value_passes(self):
        """None inputs should be accepted (field is optional)."""
        _validate_length(None, 10, "field")  # should not raise

    def test_empty_string_passes(self):
        """Empty string is under any positive limit."""
        _validate_length("", 10, "field")

    def test_string_at_limit_passes(self):
        """A string exactly at the limit should be accepted."""
        _validate_length("a" * 100, 100, "field")

    def test_string_under_limit_passes(self):
        """A string under the limit should be accepted."""
        _validate_length("hello", 100, "field")

    def test_string_over_limit_raises(self):
        """A string exceeding the limit must raise with the field name."""
        with pytest.raises(Exception, match="field_name exceeds maximum length"):
            _validate_length("a" * 101, 100, "field_name")

    def test_error_message_includes_limit(self):
        """Error message should contain the numeric limit."""
        with pytest.raises(Exception, match="100"):
            _validate_length("a" * 101, 100, "x")

    def test_one_over_limit_raises(self):
        """One character over the limit should still be rejected."""
        with pytest.raises(Exception):
            _validate_length("a" * 11, 10, "f")


# ---------------------------------------------------------------------------
# Constant sanity checks
# ---------------------------------------------------------------------------

class TestLengthConstants:
    """Ensure length constants are set to intended values."""

    def test_chat_message_limit(self):
        assert MAX_CHAT_MESSAGE_LENGTH == 50_000

    def test_pattern_text_limit(self):
        assert MAX_PATTERN_TEXT_LENGTH == 100_000

    def test_short_string_limit(self):
        assert MAX_SHORT_STRING_LENGTH == 1_000

    def test_image_data_limit(self):
        assert MAX_IMAGE_DATA_LENGTH == 10_000_000


# ---------------------------------------------------------------------------
# Coverage audit — verify every mutation's string fields are validated
# ---------------------------------------------------------------------------

class TestValidationCoverage:
    """
    Read mutations.py source and assert that every mutation with string
    input fields calls _validate_length before proceeding.  This is a
    static analysis test — it catches regressions where someone adds a
    new string field but forgets validation.
    """

    @pytest.fixture(autouse=True)
    def _load_source(self):
        src_path = os.path.join(
            os.path.dirname(__file__), '..', 'app', 'schemas', 'mutations.py'
        )
        with open(src_path) as f:
            self.source = f.read()

    # -- create_project -------------------------------------------------------

    def test_create_project_validates_name(self):
        assert '_validate_length(input.name,' in self.source

    def test_create_project_validates_pattern_text(self):
        assert '_validate_length(input.pattern_text,' in self.source

    def test_create_project_validates_notes(self):
        assert '_validate_length(input.notes,' in self.source

    def test_create_project_validates_image_data(self):
        assert '_validate_length(input.image_data,' in self.source

    def test_create_project_validates_estimated_time(self):
        assert '_validate_length(input.estimated_time,' in self.source

    def test_create_project_validates_difficulty_level(self):
        assert '_validate_length(input.difficulty_level,' in self.source

    def test_create_project_validates_yarn_weight(self):
        assert '_validate_length(input.yarn_weight,' in self.source

    def test_create_project_validates_hook_size(self):
        assert '_validate_length(input.hook_size,' in self.source

    # -- auth -----------------------------------------------------------------

    def test_register_validates_email(self):
        # Both register and login validate email
        lines = [l for l in self.source.splitlines() if '_validate_length(input.email,' in l]
        assert len(lines) >= 2, "register and login should both validate email"

    def test_register_validates_password(self):
        lines = [l for l in self.source.splitlines() if '_validate_length(input.password,' in l]
        assert len(lines) >= 2

    # -- chat -----------------------------------------------------------------

    def test_chat_validates_message(self):
        assert '_validate_length(message, MAX_CHAT_MESSAGE_LENGTH,' in self.source

    def test_chat_validates_context(self):
        assert '_validate_length(context, MAX_CHAT_MESSAGE_LENGTH,' in self.source

    # -- conversations --------------------------------------------------------

    def test_conversation_validates_title(self):
        lines = [l for l in self.source.splitlines() if '_validate_length(input.title,' in l]
        assert len(lines) >= 2, "create and update conversation should both validate title"

    # -- ai model config ------------------------------------------------------

    def test_set_ai_model_validates_model_name(self):
        assert '_validate_length(model_name, MAX_SHORT_STRING_LENGTH,' in self.source
