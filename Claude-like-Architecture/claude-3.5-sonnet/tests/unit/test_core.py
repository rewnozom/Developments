# tests/unit/test_core.py
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4
from core.base import BaseSystem
from core.config import Settings
from core.exceptions import (
    SystemInitializationError, 
    SystemOperationError,
    ConfigError
)

class TestBaseSystem:
    @pytest.fixture
    def base_system(self, temp_config_file: Path) -> BaseSystem:
        settings = Settings(temp_config_file)
        return BaseSystem(settings)

    def test_initialization(self, base_system: BaseSystem):
        """Test system initialization."""
        assert base_system.initialize()
        assert base_system.state.initialized
        assert base_system.state.status == "ready"
        assert len(base_system.components) > 0

    def test_invalid_initialization(self, temp_config_file: Path):
        """Test initialization with invalid config."""
        settings = Settings(temp_config_file)
        settings.system.max_retries = -1  # Invalid value
        
        with pytest.raises(SystemInitializationError):
            system = BaseSystem(settings)
            system.initialize()

    def test_shutdown(self, base_system: BaseSystem):
        """Test system shutdown."""
        base_system.initialize()
        assert base_system.shutdown()
        assert base_system.state.status == "shutdown"

    def test_get_status(self, base_system: BaseSystem):
        """Test status retrieval."""
        base_system.initialize()
        status = base_system.get_status()
        
        assert isinstance(status, dict)
        assert "initialized" in status
        assert "status" in status
        assert "uptime" in status
        assert "resources" in status
        assert "metrics" in status

    def test_register_component(self, base_system: BaseSystem):
        """Test component registration."""
        class TestComponent:
            pass

        component = TestComponent()
        assert base_system.register_component("test", component)
        assert "test" in base_system.components

    def test_event_handling(self, base_system: BaseSystem):
        """Test event handling system."""
        events_received = []

        def test_handler(data: Any):
            events_received.append(data)

        base_system.register_event_handler("test_event", test_handler)
        base_system.trigger_event("test_event", "test_data")

        assert len(events_received) == 1
        assert events_received[0] == "test_data"

    def test_resource_management(self, base_system: BaseSystem):
        """Test resource management."""
        base_system.initialize()
        assert base_system.monitor_resources()
        
        resources = base_system.state.resources
        assert resources.memory_usage >= 0
        assert resources.cpu_usage >= 0
        assert resources.available_memory > 0

    def test_error_handling(self, base_system: BaseSystem):
        """Test error handling."""
        base_system.initialize()
        
        # Simulate error
        error = SystemError("Test error")
        base_system.handle_error(error)
        
        assert base_system.state.error_count == 1
        assert base_system.state.status == "error"