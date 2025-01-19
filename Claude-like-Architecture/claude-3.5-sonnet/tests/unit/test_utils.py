# tests/unit/test_utils.py
import pytest
from datetime import datetime
from typing import Any
from utils.helpers import (
    retry_operation,
    safe_execute,
    chunks,
    truncate_text
)
from utils.formatters import (
    format_response,
    format_timestamp,
    format_size
)
from utils.validators import (
    validate_input,
    validate_email,
    validate_url
)

class TestHelpers:
    def test_retry_operation(self):
        """Test retry mechanism."""
        attempts = 0

        def failing_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Test error")
            return "success"

        result = retry_operation(failing_operation, max_retries=3)
        assert result == "success"
        assert attempts == 3

    def test_safe_execute(self):
        """Test safe execution."""
        def risky_operation():
            raise ValueError("Test error")

        # Should return default value
        result = safe_execute(risky_operation, default="default")
        assert result == "default"

    def test_chunks(self):
        """Test list chunking."""
        data = list(range(10))
        chunked = list(chunks(data, 3))
        assert len(chunked) == 4
        assert len(chunked[0]) == 3
        assert len(chunked[-1]) == 1

class TestFormatters:
    def test_response_formatting(self):
        """Test response formatting."""
        response = format_response(
            "test content",
            format_type="text",
            metadata={"test": True}
        )
        assert isinstance(response, str)
        assert "test content" in response

    def test_timestamp_formatting(self):
        """Test timestamp formatting."""
        now = datetime.now()
        formatted = format_timestamp(now)
        assert isinstance(formatted, str)
        assert str(now.year) in formatted

class TestValidators:
    def test_input_validation(self):
        """Test input validation."""
        assert validate_input("test@email.com", "email")
        assert not validate_input("invalid-email", "email")

    def test_url_validation(self):
        """Test URL validation."""
        assert validate_url("https://example.com")
        assert not validate_url("invalid-url")