# tests/unit/test_services.py
import pytest
from datetime import datetime
from typing import Dict, Any
from services.validation import ValidationService, ValidationRule, ValidationLevel
from services.analytics import AnalyticsService
from services.optimization import OptimizationService, OptimizationType

class TestValidationService:
    @pytest.fixture
    def validation_service(self) -> ValidationService:
        return ValidationService()

    def test_content_validation(self, validation_service: ValidationService):
        """Test content validation."""
        # Add validation rule
        validation_service.add_rule(ValidationRule(
            name="length_check",
            description="Check content length",
            validator=lambda x: len(x) > 0,
            level=ValidationLevel.BASIC
        ))

        # Test validation
        result = validation_service.validate("test content", ValidationLevel.BASIC)
        assert result.valid
        assert not result.errors

        # Test invalid content
        result = validation_service.validate("", ValidationLevel.BASIC)
        assert not result.valid
        assert len(result.errors) > 0

class TestAnalyticsService:
    @pytest.fixture
    def analytics_service(self) -> AnalyticsService:
        return AnalyticsService()

    def test_metric_tracking(self, analytics_service: AnalyticsService):
        """Test metric tracking."""
        analytics_service.track_metric(
            "response_time",
            1.5,
            metadata={"request_id": "test"}
        )

        metrics = analytics_service.get_metric_history("response_time")
        assert len(metrics) == 1
        assert metrics[0].value == 1.5

    def test_report_generation(self, analytics_service: AnalyticsService):
        """Test report generation."""
        # Add some metrics
        analytics_service.track_metric("response_time", 1.5)
        analytics_service.track_metric("memory_usage", 100)

        report = analytics_service.generate_report()
        assert len(report.metrics) == 2
        assert len(report.recommendations) > 0
