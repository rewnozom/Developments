# managers/resources.py

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import yaml

from core.exceptions import (
    ResourceError,
    ResourceNotFoundError,
    ResourceTypeError
)

@dataclass
class Resource:
    """Represents a system resource."""
    name: str
    type: str
    location: Union[str, Path]
    size: int
    loaded: bool = False
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class ResourceManager:
    """Manages system resources and their allocation."""

    def __init__(self, resource_path: Union[str, Path]):
        self.resource_path = Path(resource_path)
        self.resources: Dict[str, Resource] = {}
        self.loaded_resources: Dict[str, Any] = {}
        self.resource_limits: Dict[str, int] = {}
        self._initialize_resources()

    def _initialize_resources(self) -> None:
        """Initialize resource tracking."""
        if not self.resource_path.exists():
            self.resource_path.mkdir(parents=True)
            
        self._load_resource_config()

    def _load_resource_config(self) -> None:
        """Load resource configuration."""
        config_path = self.resource_path / "resources.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.resource_limits = config.get("limits", {})

    def register_resource(self, 
                        name: str,
                        type: str,
                        location: Union[str, Path],
                        metadata: Optional[Dict[str, Any]] = None) -> Resource:
        """Register a new resource."""
        location_path = Path(location)
        if not location_path.exists():
            raise ResourceError(f"Resource location does not exist: {location}")

        resource = Resource(
            name=name,
            type=type,
            location=location,
            size=self._get_resource_size(location_path),
            metadata=metadata or {}
        )
        
        self.resources[name] = resource
        return resource

    def load_resource(self, name: str) -> Any:
        """Load a resource into memory."""
        if name not in self.resources:
            raise ResourceNotFoundError(f"Resource not found: {name}")

        if name in self.loaded_resources:
            resource = self.resources[name]
            resource.last_accessed = datetime.now()
            return self.loaded_resources[name]

        resource = self.resources[name]
        resource_type = resource.type
        location = Path(resource.location)

        if resource_type == "json":
            with open(location) as f:
                data = json.load(f)
        elif resource_type in ("yaml", "yml"):
            with open(location) as f:
                data = yaml.safe_load(f)
        elif resource_type == "text":
            with open(location) as f:
                data = f.read()
        else:
            raise ResourceTypeError(f"Unsupported resource type: {resource_type}")

        resource.loaded = True
        resource.last_accessed = datetime.now()
        self.loaded_resources[name] = data
        return data

    def unload_resource(self, name: str) -> bool:
        """Unload a resource from memory."""
        if name in self.loaded_resources:
            del self.loaded_resources[name]
            self.resources[name].loaded = False
            return True
        return False

    def get_resource(self, name: str) -> Optional[Resource]:
        """Get resource information."""
        return self.resources.get(name)

    def get_resources_by_type(self, type: str) -> List[Resource]:
        """Get all resources of specific type."""
        return [r for r in self.resources.values() if r.type == type]

    def get_loaded_resources(self) -> Dict[str, Any]:
        """Get all loaded resources."""
        return self.loaded_resources.copy()

    def _get_resource_size(self, location: Path) -> int:
        """Get resource size in bytes."""
        return location.stat().st_size

    def optimize_memory(self) -> int:
        """Optimize memory usage by unloading unused resources."""
        freed_memory = 0
        current_time = datetime.now()
        
        for name, resource in list(self.resources.items()):
            if (resource.loaded and resource.last_accessed and
                (current_time - resource.last_accessed).total_seconds() > 3600):
                freed_memory += resource.size
                self.unload_resource(name)
                
        return freed_memory

    def update_resource(self,
                       name: str,
                       content: Any,
                       type: Optional[str] = None) -> bool:
        """Update resource content."""
        if name not in self.resources:
            return False

        resource = self.resources[name]
        location = Path(resource.location)
        
        if type:
            resource.type = type

        if resource.type == "json":
            with open(location, 'w') as f:
                json.dump(content, f, indent=json.dump(content, f, indent=2)
        elif resource.type in ("yaml", "yml"):
            with open(location, 'w') as f:
                yaml.dump(content, f)
        elif resource.type == "text":
            with open(location, 'w') as f:
                f.write(content)
        else:
            return False

        resource.size = self._get_resource_size(location)
        resource.last_accessed = datetime.now()
        
        if name in self.loaded_resources:
            self.loaded_resources[name] = content
            
        return True

    def delete_resource(self, name: str) -> bool:
        """Delete a resource."""
        if name not in self.resources:
            return False

        resource = self.resources[name]
        location = Path(resource.location)
        
        try:
            if location.exists():
                location.unlink()
            del self.resources[name]
            self.loaded_resources.pop(name, None)
            return True
        except Exception:
            return False

    def get_resource_usage(self) -> Dict[str, int]:
        """Get current resource usage statistics."""
        usage = {
            "total_resources": len(self.resources),
            "loaded_resources": len(self.loaded_resources),
            "total_size": sum(r.size for r in self.resources.values()),
            "loaded_size": sum(r.size for r in self.resources.values() if r.loaded)
        }
        return usage


class ResourceError(Exception):
   """Base class for resource-related errors."""
   pass

class ResourceNotFoundError(ResourceError):
   """Raised when resource is not found."""
   pass

class ResourceTypeError(ResourceError):
   """Raised when resource type is not supported."""
   pass

class ResourceLimitError(ResourceError):
   """Raised when resource limit is exceeded."""
   pass