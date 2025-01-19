import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Dict, List, Type, Union

class SystemError(Exception):
    """Base class for system exceptions."""
    pass

class SystemInitializationError(SystemError):
    """Raised when system initialization fails."""
    pass

class SystemOperationError(SystemError):
    """Raised when a system operation fails."""
    pass

class ConfigurationError(SystemError):
    """Raised when there's a configuration error."""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key

class ValidationError(SystemError):
    """Raised when validation fails."""
    def __init__(self, message: str, validation_errors: list = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []

class ResourceError(SystemError):
    """Raised when there's a resource-related error."""
    def __init__(self, message: str, resource_id: str = None):
        super().__init__(message)
        self.resource_id = resource_id

class SecurityError(SystemError):
    """Raised when there's a security-related error."""
    def __init__(self, message: str, security_context: dict = None):
        super().__init__(message)
        self.security_context = security_context or {}

class OperationError(SystemError):
    """Raised when an operation fails."""
    def __init__(self, message: str, operation_id: str = None, details: dict = None):
        super().__init__(message)
        self.operation_id = operation_id
        self.details = details or {}

class TokenError(SystemError):
    """Raised when there's a token-related error."""
    def __init__(self, message: str, current_tokens: int, max_tokens: int):
        super().__init__(message)
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens

class ContentError(SystemError):
    """Raised when there's a content-related error."""
    def __init__(self, message: str, content_type: str = None):
        super().__init__(message)
        self.content_type = content_type

class MemoryError(SystemError):
    """Raised when there's a memory-related error."""
    def __init__(self, message: str, current_usage: int, limit: int):
        super().__init__(message)
        self.current_usage = current_usage
        self.limit = limit

class TimeoutError(SystemError):
    """Raised when an operation times out."""
    def __init__(self, message: str, timeout: int, operation_type: str = None):
        super().__init__(message)
        self.timeout = timeout
        self.operation_type = operation_type

class RateLimitError(SystemError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, limit: int, reset_time: int):
        super().__init__(message)
        self.limit = limit
        self.reset_time = reset_time

class AuthenticationError(SystemError):
    """Raised when authentication fails."""
    def __init__(self, message: str, auth_type: str = None):
        super().__init__(message)
        self.auth_type = auth_type

class AuthorizationError(SystemError):
    """Raised when authorization fails."""
    def __init__(self, message: str, required_permissions: list = None):
        super().__init__(message)
        self.required_permissions = required_permissions or []

class BoundaryError(SystemError):
    """Raised when a system boundary is violated."""
    def __init__(self, message: str, boundary_type: str = None):
        super().__init__(message)
        self.boundary_type = boundary_type

class StateError(SystemError):
    """Raised when there's a state-related error."""
    def __init__(self, message: str, current_state: str = None, expected_state: str = None, details: dict = None):
        super().__init__(message)
        self.current_state = current_state
        self.expected_state = expected_state
        self.details = details or {}

class StateLockError(StateError):
    """Raised when attempting to modify a locked state."""
    def __init__(self, message: str, locked_by: str = None, lock_time: str = None):
        super().__init__(
            message,
            current_state="locked",
            details={
                "locked_by": locked_by,
                "lock_time": lock_time
            }
        )
        self.locked_by = locked_by
        self.lock_time = lock_time


class StateCorruptionError(StateError):
    """Raised when state corruption is detected."""
    def __init__(self, message: str, corrupted_fields: list = None):
        super().__init__(
            message,
            current_state="corrupted",
            details={"corrupted_fields": corrupted_fields or []}
        )
        self.corrupted_fields = corrupted_fields or []     
        
class StateInitializationError(StateError):
    """Raised when state initialization fails."""
    def __init__(self, message: str, failed_components: list = None):
        super().__init__(
            message,
            current_state="initializing",
            details={"failed_components": failed_components or []}
        )
        self.failed_components = failed_components or []


class ConversationError(SystemError):
    """Base class for conversation-related errors."""
    def __init__(self, message: str, conversation_id: str = None, metadata: Dict[str, Any] = None):
        super().__init__(message)
        self.conversation_id = conversation_id
        self.metadata = metadata or {}

class MessageError(ConversationError):
    """Raised when there's an issue with message processing."""
    def __init__(self, message: str, conversation_id: str = None, 
                 message_id: str = None, message_type: str = None):
        super().__init__(message, conversation_id)
        self.message_id = message_id
        self.message_type = message_type

class MessageValidationError(MessageError):
    """Raised when message validation fails."""
    def __init__(self, message: str, conversation_id: str = None, 
                 message_id: str = None, validation_errors: List[str] = None):
        super().__init__(message, conversation_id, message_id)
        self.validation_errors = validation_errors or []

class MessageProcessingError(MessageError):
    """Raised when message processing fails."""
    def __init__(self, message: str, conversation_id: str = None, 
                 message_id: str = None, processing_stage: str = None):
        super().__init__(message, conversation_id, message_id)
        self.processing_stage = processing_stage


class StateVersionError(StateError):
    """Raised when there's a state version mismatch."""
    def __init__(self, message: str, current_version: str, required_version: str):
        super().__init__(
            message,
            details={
                "current_version": current_version,
                "required_version": required_version
            }
        )
        self.current_version = current_version
        self.required_version = required_version
        
class InvalidStateTransitionError(StateError):
    """Raised when attempting an invalid state transition."""
    def __init__(self, message: str, from_state: str, to_state: str):
        super().__init__(
            message,
            current_state=from_state,
            expected_state=to_state,
            details={"attempted_transition": f"{from_state} -> {to_state}"}
        )
        self.from_state = from_state
        self.to_state = to_state
        
        
class ArtifactError(SystemError):
    """Raised when there's an artifact-related error."""
    def __init__(self, message: str, artifact_id: str = None, artifact_type: str = None):
        super().__init__(message)
        self.artifact_id = artifact_id
        self.artifact_type = artifact_type

class ProcessingError(SystemError):
    """Raised when processing fails."""
    def __init__(self, message: str, processor_type: str = None, step: str = None):
        super().__init__(message)
        self.processor_type = processor_type
        self.step = step

class ContextError(SystemError):
    """Raised when there's a context-related error."""
    def __init__(self, message: str, context_id: str = None, context_type: str = None):
        super().__init__(message)
        self.context_id = context_id
        self.context_type = context_type

class ModelError(SystemError):
    """Raised when there's a model-related error."""
    def __init__(self, message: str, model_name: str = None, model_version: str = None):
        super().__init__(message)
        self.model_name = model_name
        self.model_version = model_version

class DataError(SystemError):
    """Raised when there's a data-related error."""
    def __init__(self, message: str, data_type: str = None, data_id: str = None):
        super().__init__(message)
        self.data_type = data_type
        self.data_id = data_id

# Error Handling Decorators
def handle_system_errors(func):
    """Decorator for handling system errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SystemError as e:
            logging.error(f"System error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise SystemError(f"Unexpected error: {str(e)}")
    return wrapper

def validate_operation(validator: Optional[Callable] = None):
    """Decorator for validating operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if validator:
                if not validator(*args, **kwargs):
                    raise ValidationError(f"Validation failed for operation: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, 
              delay: float = 1.0,
              exceptions: Union[Type[Exception], tuple] = Exception,
              logger: Optional[logging.Logger] = None):
    """Decorator for retrying operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if logger:
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

def validate_args(*args, **kwargs) -> bool:
    """Validate operation arguments."""
    try:
        # Basic validation
        for arg in args:
            if arg is None:
                return False
        for value in kwargs.values():
            if value is None:
                return False
        return True
    except Exception:
        return False

# Context manager for resource handling
class ErrorContext:
    """Context manager for handling errors in a specific context."""
    def __init__(self, context_name: str, logger: Optional[logging.Logger] = None):
        self.context_name = context_name
        self.logger = logger or logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(f"Error in context {self.context_name}: {str(exc_val)}")
            if not issubclass(exc_type, SystemError):
                raise SystemError(f"Error in {self.context_name}: {str(exc_val)}")
            return False
        return True

class ContextInitializationError(ContextError):
    """Raised when context initialization fails."""
    def __init__(self, message: str, conversation_id: str = None, 
                 failed_component: str = None):
        super().__init__(message, conversation_id)
        self.failed_component = failed_component

class UUIDGenerationError(SystemError):
    """Raised when there's an error generating or handling UUIDs."""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message)
        self.operation = operation

class GenerationError(SystemError):
    """Raised when content generation fails."""
    def __init__(self, message: str, generator_name: str = None, input_data: Any = None):
        super().__init__(message)
        self.generator_name = generator_name
        self.input_data = input_data

class ResourceNotFoundError(ResourceError):
    """Raised when a required resource is not found."""
    pass

class ResourceTypeError(ResourceError):
    """Raised when a resource is of an unexpected type."""
    def __init__(self, message: str, resource_id: str, expected_type: Type, actual_type: Type):
        super().__init__(message, resource_id)
        self.expected_type = expected_type
        self.actual_type = actual_type








class ConversationLimitError(ConversationError):
    """Raised when conversation limits are exceeded."""
    def __init__(self, message: str, conversation_id: str = None, 
                 limit_type: str = None, current_value: int = None, max_value: int = None):
        super().__init__(message, conversation_id)
        self.limit_type = limit_type
        self.current_value = current_value
        self.max_value = max_value


class ConversationContextError(ConversationError):
    """Raised when there's an issue with conversation context."""
    def __init__(self, message: str, conversation_id: str = None, 
                 context_size: int = None, max_context: int = None):
        super().__init__(message, conversation_id)
        self.context_size = context_size
        self.max_context = max_context


class ConversationFlowError(ConversationError):
    """Raised when there's an issue with conversation flow."""
    def __init__(self, message: str, conversation_id: str = None, 
                 flow_state: str = None, expected_flow: str = None):
        super().__init__(message, conversation_id)
        self.flow_state = flow_state
        self.expected_flow = expected_flow


class ConversationState(SystemError):
    """Raised when there's an issue with the conversation state."""
    def __init__(self, message: str, state: dict = None):
        super().__init__(message)
        self.state = state or {}

class ConversationStateError(ConversationError):
    """Raised when there's an issue with conversation state."""
    def __init__(self, message: str, conversation_id: str = None, 
                 current_state: str = None, expected_state: str = None):
        super().__init__(message, conversation_id)
        self.current_state = current_state
        self.expected_state = expected_state

class ResponseGenerationError(SystemError):
    """Raised when there's an error generating a response."""
    def __init__(self, message: str, generator_name: str = None, 
                 input_data: Any = None, error_details: Dict[str, Any] = None,
                 conversation_id: str = None):
        super().__init__(message)
        self.generator_name = generator_name
        self.input_data = input_data
        self.error_details = error_details or {}
        self.conversation_id = conversation_id


