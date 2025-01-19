# controllers/safety/boundary.py
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from core.exceptions import BoundaryError

class BoundaryType(Enum):
    """Types of boundaries."""
    CONTENT = "content"
    INTERACTION = "interaction"
    RESOURCE = "resource"
    CAPABILITY = "capability"
    CUSTOM = "custom"

@dataclass
class Boundary:
    """Represents a system boundary."""
    type: BoundaryType
    name: str
    constraints: Dict[str, Any]
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BoundaryViolation:
    """Record of boundary violation."""
    boundary: Boundary
    violation_type: str
    details: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class BoundaryController:
    """Controls system boundaries and restrictions."""

    def __init__(self):
        self.boundaries: Dict[str, Boundary] = {}
        self.violations: Dict[UUID, List[BoundaryViolation]] = {}
        self.active_exemptions: Dict[str, Set[UUID]] = {}
        self._initialize_boundaries()

    def enforce_boundary(self,
                        boundary_name: str,
                        context: Any,
                        context_id: UUID) -> bool:
        """Enforce specific boundary."""
        try:
            # Validate UUID
            if not isinstance(context_id, UUID):
                raise BoundaryError("Invalid context ID type")
                
            if not boundary_name:
                raise BoundaryError("Boundary name cannot be empty")

            # Check if boundary exists
            if boundary_name not in self.boundaries:
                raise BoundaryError(f"Boundary {boundary_name} not found")

            boundary = self.boundaries[boundary_name]
            
            # Check if boundary is enabled
            if not boundary.enabled:
                return True

            # Check for exemptions
            if self._is_exempt(boundary_name, context_id):
                return True

            # Enforce boundary
            violation = self._check_boundary(boundary, context)
            
            if violation:
                self._record_violation(context_id, violation)
                return False

            return True

        except BoundaryError:
            raise
        except Exception as e:
            raise BoundaryError(f"Boundary enforcement failed: {str(e)}")

    def _initialize_boundaries(self) -> None:
        """Initialize system boundaries."""
        # Content boundaries
        self.boundaries.update({
            'content_length': Boundary(
                type=BoundaryType.CONTENT,
                name='content_length',
                constraints={'max_length': 10000}
            ),
            'content_type': Boundary(
                type=BoundaryType.CONTENT,
                name='content_type',
                constraints={'allowed_types': ['text', 'code', 'markdown']}
            )
        })

        # Interaction boundaries
        self.boundaries.update({
            'rate_limit': Boundary(
                type=BoundaryType.INTERACTION,
                name='rate_limit',
                constraints={'max_requests': 100, 'time_window': 3600}
            ),
            'session_length': Boundary(
                type=BoundaryType.INTERACTION,
                name='session_length',
                constraints={'max_duration': 7200}
            )
        })

        # Resource boundaries
        self.boundaries.update({
            'memory_usage': Boundary(
                type=BoundaryType.RESOURCE,
                name='memory_usage',
                constraints={'max_memory_mb': 1024}
            ),
            'cpu_usage': Boundary(
                type=BoundaryType.RESOURCE,
                name='cpu_usage',
                constraints={'max_cpu_percent': 80}
            )
        })

        # Capability boundaries
        self.boundaries.update({
            'file_access': Boundary(
                type=BoundaryType.CAPABILITY,
                name='file_access',
                constraints={'allowed_operations': ['read']}
            ),
            'network_access': Boundary(
                type=BoundaryType.CAPABILITY,
                name='network_access',
                constraints={'allowed_protocols': ['http', 'https']}
            )
        })

    def _check_boundary(self,
                       boundary: Boundary,
                       context: Any) -> Optional[BoundaryViolation]:
        """Check if context violates boundary."""
        if boundary.type == BoundaryType.CONTENT:
            return self._check_content_boundary(boundary, context)
        elif boundary.type == BoundaryType.INTERACTION:
            return self._check_interaction_boundary(boundary, context)
        elif boundary.type == BoundaryType.RESOURCE:
            return self._check_resource_boundary(boundary, context)
        elif boundary.type == BoundaryType.CAPABILITY:
            return self._check_capability_boundary(boundary, context)
        elif boundary.type == BoundaryType.CUSTOM:
            return self._check_custom_boundary(boundary, context)
        return None

    def _check_content_boundary(self,
                                boundary: Boundary,
                                context: Any) -> Optional[BoundaryViolation]:
        """Check content boundaries."""
        if boundary.name == 'content_length':
            content_length = len(str(context))
            if content_length > boundary.constraints['max_length']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='length_exceeded',
                    details=f"Content length {content_length} exceeds maximum {boundary.constraints['max_length']}",
                    timestamp=datetime.now()
                )
                
        elif boundary.name == 'content_type':
            content_type = getattr(context, 'type', str(type(context)))
            if content_type not in boundary.constraints['allowed_types']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='invalid_type',
                    details=f"Content type {content_type} not allowed",
                    timestamp=datetime.now()
                )
                
        return None

    def _check_interaction_boundary(self,
                                    boundary: Boundary,
                                    context: Any) -> Optional[BoundaryViolation]:
        """Check interaction boundaries."""
        if boundary.name == 'rate_limit':
            current_time = datetime.now().timestamp()
            time_window = boundary.constraints['time_window']
            request_count = sum(1 for t in context.get('request_times', [])
                                if current_time - t <= time_window)
                                
            if request_count > boundary.constraints['max_requests']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='rate_limit_exceeded',
                    details=f"Rate limit of {boundary.constraints['max_requests']} requests per {time_window}s exceeded",
                    timestamp=datetime.now()
                )
                
        elif boundary.name == 'session_length':
            session_duration = context.get('session_duration', 0)
            if session_duration > boundary.constraints['max_duration']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='session_timeout',
                    details=f"Session duration {session_duration}s exceeds maximum {boundary.constraints['max_duration']}s",
                    timestamp=datetime.now()
                )
                
        return None

    def _check_resource_boundary(self,
                                boundary: Boundary,
                                context: Any) -> Optional[BoundaryViolation]:
        """Check resource boundaries."""
        if boundary.name == 'memory_usage':
            memory_usage = context.get('memory_usage', 0)
            if memory_usage > boundary.constraints['max_memory_mb']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='memory_limit_exceeded',
                    details=f"Memory usage {memory_usage}MB exceeds maximum {boundary.constraints['max_memory_mb']}MB",
                    timestamp=datetime.now()
                )
                
        elif boundary.name == 'cpu_usage':
            cpu_usage = context.get('cpu_usage', 0)
            if cpu_usage > boundary.constraints['max_cpu_percent']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='cpu_limit_exceeded',
                    details=f"CPU usage {cpu_usage}% exceeds maximum {boundary.constraints['max_cpu_percent']}%",
                    timestamp=datetime.now()
                )
                
        return None

    def _check_capability_boundary(self,
                                    boundary: Boundary,
                                    context: Any) -> Optional[BoundaryViolation]:
        """Check capability boundaries."""
        if boundary.name == 'file_access':
            operation = context.get('operation')
            if operation not in boundary.constraints['allowed_operations']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='unauthorized_operation',
                    details=f"File operation {operation} not allowed",
                    timestamp=datetime.now()
                )
                
        elif boundary.name == 'network_access':
            protocol = context.get('protocol')
            if protocol not in boundary.constraints['allowed_protocols']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type='unauthorized_protocol',
                    details=f"Network protocol {protocol} not allowed",
                    timestamp=datetime.now()
                )
                
        return None

    def _check_custom_boundary(self,
                                boundary: Boundary,
                                context: Any) -> Optional[BoundaryViolation]:
        """Check custom boundaries."""
        checker = boundary.constraints.get('checker')
        if checker and callable(checker):
            result = checker(context)
            if not result['passed']:
                return BoundaryViolation(
                    boundary=boundary,
                    violation_type=result.get('violation_type', 'custom_violation'),
                    details=result.get('details', 'Custom boundary violated'),
                    timestamp=datetime.now(),
                    metadata=result.get('metadata')
                )
        return None

    def _record_violation(self,
                            context_id: UUID,
                            violation: BoundaryViolation) -> None:
        """Record boundary violation."""
        if context_id not in self.violations:
            self.violations[context_id] = []
        self.violations[context_id].append(violation)

    def _is_exempt(self,
                    boundary_name: str,
                    context_id: UUID) -> bool:
        """Check if context is exempt from boundary."""
        return (boundary_name in self.active_exemptions and
                context_id in self.active_exemptions[boundary_name])

    def add_boundary(self,
                    name: str,
                    boundary_type: BoundaryType,
                    constraints: Dict[str, Any],
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add new boundary."""
        if name in self.boundaries:
            raise ValueError(f"Boundary {name} already exists")
            
        self.boundaries[name] = Boundary(
            type=boundary_type,
            name=name,
            constraints=constraints,
            metadata=metadata
        )

    def remove_boundary(self, name: str) -> bool:
        """Remove boundary."""
        return bool(self.boundaries.pop(name, None))

    def update_boundary(self,
                        name: str,
                        constraints: Dict[str, Any]) -> bool:
        """Update boundary constraints."""
        if name not in self.boundaries:
            return False
            
        self.boundaries[name].constraints.update(constraints)
        return True

    def enable_boundary(self, name: str) -> bool:
        """Enable boundary."""
        if name not in self.boundaries:
            return False
            
        self.boundaries[name].enabled = True
        return True

    def disable_boundary(self, name: str) -> bool:
        """Disable boundary."""
        if name not in self.boundaries:
            return False
            
        self.boundaries[name].enabled = False
        return True

    def add_exemption(self,
                        boundary_name: str,
                        context_id: UUID) -> bool:
        """Add boundary exemption."""
        if boundary_name not in self.boundaries:
            return False
            
        if boundary_name not in self.active_exemptions:
            self.active_exemptions[boundary_name] = set()
            
        self.active_exemptions[boundary_name].add(context_id)
        return True

    def remove_exemption(self,
                        boundary_name: str,
                        context_id: UUID) -> bool:
        """Remove boundary exemption."""
        if boundary_name not in self.active_exemptions:
            return False
            
        self.active_exemptions[boundary_name].discard(context_id)
        return True

    def get_violations(self,
                        context_id: UUID) -> List[BoundaryViolation]:
        """Get boundary violations for context."""
        return self.violations.get(context_id, [])

    def clear_violations(self,
                        context_id: Optional[UUID] = None) -> None:
        """Clear violation history."""
        if context_id:
            self.violations.pop(context_id, None)
        else:
            self.violations.clear()