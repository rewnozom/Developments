# tests/unit/test_exceptions.py
import pytest
from datetime import datetime
from uuid import UUID
from core.exceptions import (
    SystemError,
    ConfigurationError,
    ValidationError,
    ResourceError,
    StateError,
    ProcessingError,
    GenerationError
)
from typing import Dict, Any

class TestExceptions:
    def test_system_error(self):
        """Test SystemError handling."""
        with pytest.raises(SystemError) as exc_info:
            raise SystemError("Test system error")
        assert str(exc_info.value) == "Test system error"

    def test_configuration_error(self):
        """Test ConfigurationError handling."""
        error = ConfigurationError(
            message="Invalid config",
            config_key="test_key"
        )
        assert error.config_key == "test_key"
        assert "Invalid config" in str(error)

    def test_validation_error(self):
        """Test ValidationError handling."""
        validation_errors = ["Field required", "Invalid format"]
        error = ValidationError(
            message="Validation failed",
            validation_errors=validation_errors
        )
        assert len(error.validation_errors) == 2
        assert "Validation failed" in str(error)

    def test_resource_error(self):
        """Test ResourceError handling."""
        error = ResourceError(
            message="Resource not found",
            resource_id="test-resource"
        )
        assert error.resource_id == "test-resource"
        assert "Resource not found" in str(error)

    def test_state_error(self):
        """Test StateError handling."""
        error = StateError(
            message="Invalid state transition",
            current_state="initial",
            expected_state="active"
        )
        assert error.current_state == "initial"
        assert error.expected_state == "active"
        assert "Invalid state transition" in str(error)

    def test_error_handlers(self):
        """Test error handler decorators."""
        from core.exceptions import handle_system_errors

        @handle_system_errors
        def risky_operation():
            raise ValueError("Test error")

        with pytest.raises(SystemError):
            risky_operation()

    def test_error_context(self):
        """Test error context manager."""
        from core.exceptions import ErrorContext
        import logging

        with pytest.raises(SystemError):
            with ErrorContext("test_operation"):
                raise ValueError("Test error")

    def test_custom_error_creation(self):
        """Test custom error creation."""
        class CustomError(SystemError):
            def __init__(self, message: str, custom_data: Dict[str, Any]):
                super().__init__(message)
                self.custom_data = custom_data

        error = CustomError(
            message="Custom error",
            custom_data={"test": True}
        )
        assert error.custom_data["test"] is True
        assert "Custom error" in str(error)