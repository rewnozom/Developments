# main.py

from uuid import UUID, uuid4  # Add this import at the top

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import uvicorn
import json
import os
import asyncio
import signal
import psutil

from config.settings import Settings, ConfigError
from config.logging import setup_logging, get_logger
from core.base import BaseSystem
from core.exceptions import SystemError
from controllers.conversation import ConversationFlow, ConversationContext, StateManager
from processors import InputProcessor, ContentProcessor, FormatProcessor, OutputProcessor
from models.conversation import Conversation, Message, MessageRole
from models.response import Response, ResponseType, ResponseMetadata
from utils.helpers import safe_execute


# Constants
STATE_FILE = "system_state.json"
CONVERSATION_DIR = "conversations"
MAX_RETRIES = 3
API_VERSION = "v1"
BATCH_SIZE = 10

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class BatchChatRequest(BaseModel):
    messages: List[ChatRequest]
    options: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting up Claude 3.5 Sonnet system...")
    system.initialize()
    if os.path.exists(STATE_FILE):
        system.instance.load_state(Path(STATE_FILE))
    
    yield
    
    # Shutdown
    logging.info("Shutting down Claude 3.5 Sonnet system...")
    if system.instance:
        await system.instance.shutdown()
    await asyncio.sleep(1)  # Allow pending tasks to complete

# FastAPI instance
app = FastAPI(
    title="Claude 3.5 Sonnet API",
    version=API_VERSION,
    lifespan=lifespan
)

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Add SlowAPIMiddleware
app.add_middleware(SlowAPIMiddleware)

# Handle rate limit exceed errors
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Anpassa efter behov
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SystemInstance:
    def __init__(self):
        self.instance = None

    def initialize(self, config_path: Optional[Path] = None):
        if not self.instance:
            self.instance = ClaudeSonnet(config_path)
        return self.instance

    def save_state(self):
        if self.instance:
            self.instance.save_state(Path(STATE_FILE))

system = SystemInstance()

class ClaudeSonnet(BaseSystem):
    """Main system class for Claude 3.5 Sonnet."""

    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        self.config = Settings(config_path)
        if not self.config.validate():
            raise SystemError("Invalid configuration")
            
        # Initialize logging
        self.log_manager = setup_logging(
            level=self.config.logging.level,
            log_dir=self.config.logging.file_path and Path(self.config.logging.file_path).parent or None,
            config_file=None
        )
        self.logger = get_logger(__name__)
        
        # Initialize base system
        super().__init__(self.config)
        
        # Initialize LLM manager
        from models.llm_models import llm_manager
        self.llm = llm_manager
        if hasattr(self.config.system, "model_name") and self.config.system.model_name:
            self.llm.set_current_model(self.config.system.model_name)
        
        # Initialize conversations dictionary
        self.conversations: Dict[str, Conversation] = {}
        
        # Initialize components
        self._initialize_components()
        
        # Create conversations directory if it doesn't exist
        os.makedirs(CONVERSATION_DIR, exist_ok=True)
        
        # Load existing conversations
        self._load_conversations()

    def _initialize_components(self) -> None:
        """Initialize system components."""
        try:
            # Initialize controllers
            self.conversation_flow = ConversationFlow()
            self.conversation_context = ConversationContext()
            self.state_manager = StateManager()

            # Initialize processors
            self.input_processor = InputProcessor()
            self.content_processor = ContentProcessor()
            self.format_processor = FormatProcessor()
            self.output_processor = OutputProcessor()

            self.logger.info("System components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise SystemError(f"Component initialization failed: {str(e)}")

    async def process_conversation(self, 
                           conversation: Conversation,
                           options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process conversation and generate response."""
        
        def execute_with_retry(func, *args, retries=MAX_RETRIES):
            """Execute function with retry logic."""
            last_error = None
            for attempt in range(retries):
                try:
                    return safe_execute(lambda: func(*args))
                except Exception as e:
                    last_error = e
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue
            raise last_error if last_error else SystemError("All retry attempts failed")

        try:
            # Initialize if new conversation
            if not self.state_manager.get_state(conversation.id):
                self.state_manager.initialize_state(conversation)
                self.conversation_context.manage_context(conversation)
                self.conversation_flow.manage_flow(conversation)

            # Process input with retry
            processed_input = execute_with_retry(
                self.input_processor.process_input,
                conversation.messages[-1].content if conversation.messages else ""
            )

            # Process content with retry
            processed_content = execute_with_retry(
                self.content_processor.process_content,
                processed_input.content if processed_input else "",
                options
            )

            # Update context
            self.conversation_context.manage_context(conversation)

            # Generate response
            response_content = await self._generate_response(
                conversation,
                processed_content.processed if processed_content else ""
            )

            # Format response with retry
            formatted_response = execute_with_retry(
                self.format_processor.format_content,
                response_content,
                options.get('format_type', 'text') if options else 'text'
            )

            # Process output with retry
            processed_output = execute_with_retry(
                self.output_processor.process_output,
                formatted_response.content if formatted_response else response_content
            )

            # Collect metrics
            metrics = {
                'engagement': self.conversation_flow.optimize_engagement(conversation),
                'coherence': self.conversation_flow.maintain_coherence(conversation),
                'context_size': self.conversation_context.get_context_size(conversation.id),
                'processing_time': processed_output.metadata.processing_time if processed_output else 0,
                'total_tokens': processed_output.total_tokens if processed_output else 0
            }

            # Prepare result
            result = {
                'response': processed_output.content if processed_output else response_content,
                'metrics': metrics,
                'metadata': {
                    'state': self.state_manager.get_state(conversation.id).value,
                    'timestamp': datetime.now().isoformat()
                }
            }

            self.logger.info(f"Successfully processed conversation {conversation.id}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to process conversation: {str(e)}")
            raise SystemError(f"Conversation processing failed: {str(e)}")

    def get_uptime(self) -> float:
        """Calculate system uptime in seconds."""
        return (datetime.now() - self.state.start_time).total_seconds()

    async def _generate_response(self, 
                         conversation: Conversation,
                         processed_content: str) -> str:
        """Generate response based on conversation context and processed content."""
        try:
            # Get relevant context
            context = self.conversation_context.get_context(
                conversation.id,
                min_importance=0.5
            )

            # Get conversation state
            state = self.state_manager.get_state(conversation.id)
 
            # Apply safety checks
            if not self.validate_content(processed_content):
                raise ValueError("Content failed safety validation")

            # Handle error state
            if state == "error":
                return self._handle_error_state(conversation)
            
            # Format messages for the model
            messages = []
            
            # Add system message if needed
            if conversation.messages and conversation.messages[0].role == MessageRole.SYSTEM:
                messages.append({
                    "role": "system",
                    "content": conversation.messages[0].content
                })
            
            # Add context messages
            for msg in conversation.messages:
                if msg.role != MessageRole.SYSTEM:  # Skip system messages as they're handled above
                    messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": processed_content
            })
            
            # Generate response using LLM manager
            try:
                model_response = await self.llm.generate_response(messages)
                
                # Create response object
                response = Response(
                    content=model_response.content,
                    type=ResponseType.TEXT,
                    metadata=ResponseMetadata(
                        created_at=datetime.now(),
                        processing_time=model_response.processing_time,
                        model=model_response.model_name,
                        tokens=model_response.total_tokens,
                        context_tokens=model_response.prompt_tokens,
                        prompt_tokens=model_response.completion_tokens
                    )
                )
                
                return response.content
                
            except Exception as e:
                self.logger.error(f"Model generation failed: {str(e)}")
                return self._handle_error_state(conversation)

        except Exception as e:
            self.logger.error(f"Failed to generate response: {str(e)}")
            raise SystemError(f"Response generation failed: {str(e)}")

    def validate_content(self, content: str) -> bool:
        """Validate content for safety and quality."""
        # Implement actual validation logic here
        return True

    def _handle_error_state(self, conversation: Conversation) -> str:
        """Handle conversation in error state."""
        return "I apologize, but I encountered an error. Please try again or rephrase your message."

    def _load_conversations(self) -> None:
        """Load saved conversations from disk."""
        try:
            for filename in os.listdir(CONVERSATION_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(CONVERSATION_DIR, filename)
                    with open(file_path, 'r') as f:
                        conversation_data = json.load(f)
                        conversation = Conversation.from_dict(conversation_data)
                        self.conversations[str(conversation.id)] = conversation
        except Exception as e:
            self.logger.error(f"Failed to load conversations: {str(e)}")

    def save_conversation(self, conversation_id: str) -> None:
        """Save a conversation to disk."""
        try:
            conversation = self.conversations.get(conversation_id)
            if conversation:
                file_path = os.path.join(CONVERSATION_DIR, f"{conversation_id}.json")
                with open(file_path, 'w') as f:
                    json.dump(conversation.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save conversation {conversation_id}: {str(e)}")

    def save_state(self, path: Path) -> bool:
        """Save system state to file."""
        try:
            state = {
                'config': self.config.to_dict(),
                'metrics': self.get_status(),
                'conversation_ids': list(str(id) for id in self.conversations.keys())  # Convert UUIDs to strings
            }
            
            # Convert Path to string
            path_str = str(path)
            
            with open(path_str, 'w') as f:
                json.dump(state, f, indent=2, default=str)  # Add default=str to handle UUID serialization
                    
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {str(e)}")
            return False
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {str(e)}")
            return False

    def load_state(self, path: Path) -> bool:
        """Load system state from file."""
        try:
            with open(path, 'r') as f:
                state = json.load(f)

            # Update configuration
            self.config = Settings()
            self.config._update_settings(state['config'])
            
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to load state: {str(e)}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        return {
            'total_conversations': len(self.conversations),
            'active_conversations': sum(1 for c in self.conversations.values() if c.state == 'active'),
            'system_uptime': self.get_uptime(),
            'memory_usage': self.get_memory_usage()
        }

    def get_memory_usage(self) -> Dict[str, float]:
        """Get detailed memory usage stats."""
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss / 1024 / 1024,  # MB
            'vms': process.memory_info().vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }

    async def cleanup_resources(self):
        """Cleanup system resources."""
        try:
            # Add cleanup code here if needed
            pass
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    async def shutdown(self):
        """Graceful shutdown of system."""
        try:
            # Save all conversations
            for conv_id in self.conversations:
                self.save_conversation(conv_id)
            
            # Save system state
            self.save_state(Path(STATE_FILE))
            
            # Close any open resources
            await self.cleanup_resources()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and its persistent storage."""
        try:
            if conversation_id in self.conversations:
                # Remove from memory
                del self.conversations[conversation_id]
                
                # Remove from disk
                file_path = os.path.join(CONVERSATION_DIR, f"{conversation_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete conversation {conversation_id}: {str(e)}")
            return False

    async def process_batch(self, requests: List[ChatRequest]) -> List[Dict[str, Any]]:
        """Process multiple chat requests in batch."""
        results = []
        for batch in [requests[i:i + BATCH_SIZE] for i in range(0, len(requests), BATCH_SIZE)]:
            batch_results = await asyncio.gather(
                *[self.process_message_async(**request.dict()) for request in batch]
            )
            results.extend(batch_results)
        return results

    async def process_message(self, message: str, conversation_id: Optional[str] = None, 
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single message and return response."""
        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
        else:
            conversation = Conversation()
            self.conversations[str(conversation.id)] = conversation

        # Add user message
        user_message = Message(role=MessageRole.USER, content=message)
        conversation.add_message(user_message)

        # Process conversation
        result = await self.process_conversation(conversation, options)
        
        # Add assistant response to conversation
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=result['response']
        )
        conversation.add_message(assistant_message)

        # Save conversation in background
        self.save_conversation(str(conversation.id))

        return {
            'conversation_id': str(conversation.id),
            'response': result['response'],
            'metrics': result['metrics'],
            'metadata': result.get('metadata')
        }

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
@limiter.limit("100/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest, 
    background_tasks: BackgroundTasks
):
    """Chat endpoint."""
    try:
        if not system.instance:
            system.initialize()
            
        # Add await here
        result = await system.instance.process_message(
            message=chat_request.message,
            conversation_id=chat_request.conversation_id,
            options=chat_request.options
        )
        
        background_tasks.add_task(system.save_state)
        
        return result
    except RateLimitExceeded:
        error_response = ErrorResponse(
            detail="Too many requests. Try again later.",
            error_code="RATE_LIMIT_EXCEEDED"
        )
        return JSONResponse(
            status_code=429,
            content=error_response.dict()
        )
    except Exception as e:
        error_response = ErrorResponse(
            detail=str(e),
            error_code="PROCESSING_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )

@app.get("/conversations")
@limiter.limit("100/minute")  # Applicera rate limit
async def list_conversations(
    request: Request,  # Ändrat från req: Request = None till request: Request
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Get list of conversations with pagination."""
    try:
        if not system.instance:
            system.initialize()
            
        conversations = list(system.instance.conversations.values())
        
        # Sort conversations
        conversations.sort(
            key=lambda x: getattr(x.metadata, sort_by),
            reverse=(order.lower() == "desc")
        )
        
        # Apply pagination
        conversations = conversations[skip:skip + limit]
        
        return {
            "conversations": [conv.to_dict() for conv in conversations],
            "total": len(system.instance.conversations),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}")
@limiter.limit("100/minute")  # Applicera rate limit
async def get_conversation(
    request: Request,  # Ändrat från req: Request = None till request: Request
    conversation_id: str
):
    """Get conversation history."""
    try:
        if not system.instance:
            system.initialize()
            
        conversation = system.instance.conversations.get(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        return conversation.to_dict()
    except Exception as e:
        error_response = ErrorResponse(
            detail=str(e),
            error_code="RETRIEVAL_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )

@app.delete("/conversations/{conversation_id}")
@limiter.limit("100/minute")  # Applicera rate limit
async def delete_conversation(
    request: Request,  # Ändrat från req: Request = None till request: Request
    conversation_id: str
):
    """Delete a conversation."""
    try:
        if not system.instance:
            system.initialize()
            
        success = system.instance.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/batch")
@limiter.limit("100/minute")  # Applicera rate limit
async def batch_chat(
    request: Request,  # Ändrat från req: Request = None till request: Request
    batch_request: BatchChatRequest
):
    """Batch process multiple chat requests."""
    try:
        if not system.instance:
            system.initialize()
            
        results = await system.instance.process_batch(batch_request.messages)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Enhanced health check endpoint."""
    if not system.instance:
        return {
            "status": "initializing",
            "timestamp": datetime.now().isoformat()
        }
        
    try:
        memory_usage = system.instance.get_memory_usage()
        return {
            "status": "healthy",
            "version": API_VERSION,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "memory_usage": memory_usage,
                "total_conversations": len(getattr(system.instance, 'conversations', [])),
                "uptime": system.instance.get_uptime()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def main():
    """Main entry point with graceful shutdown."""
    try:
        # Setup signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: asyncio.create_task(system.instance.shutdown()))
        
        # Start FastAPI server with import string format
        uvicorn.run(
            "main:app",  # Use import string instead of app instance
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True,  # Enable hot reload for development
            workers=os.cpu_count(),
            reload_excludes=['*.pyc', '*.log'],  # Exclude files from reload
            reload_includes=['*.py', '*.json']   # Include files for reload
        )
        
    except Exception as e:
        logging.error(f"System error: {str(e)}")
        raise

if __name__ == "__main__":
    # För utveckling kan vi använda uvicorn direkt
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
