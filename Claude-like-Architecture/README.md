# Claude Project

This project combines a modern React frontend with the Claude 3.5 Sonnet model implementation.

## Project Structure

```
project-root/
├── frontend/           # React frontend application
└── claude-3.5-sonnet/ # Claude model implementation
```

## Quick Start

### Development
```bash
# Install dependencies for all workspaces
npm install
cd claude-3.5-sonnet
# Try to install package directly, if it fails, fall back to requirements.txt
pip install . || pip install -r requirements.txt
cd ..
# Start both frontend and backend in development mode
npm run dev
```

---


```bash
# Start only frontend
npm run dev:frontend

# Start only backend
npm run dev:backend
```

---

# Backend health validations
```bash
http://localhost:8000/docs
```

---

### Docker Deployment

```bash
# Build and start all services
npm run docker:up

# Stop all services
npm run docker:down

# View logs
npm run docker:logs
```

## Components

### Frontend
- React 18
- TypeScript
- TailwindCSS
- Vite

### Backend
- Claude 3.5 Sonnet model
- API endpoints
- WebSocket support

## Configuration

Create a `.env` file in the root directory for project-wide environment variables. Each component (frontend/backend) can also have its own `.env` file for component-specific variables.

# Environment Configuration

## Frontend Environment (.env)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_API_VERSION=v1

# Authentication
VITE_AUTH_ENABLED=false
VITE_AUTH_PROVIDER=none

# Feature Flags
VITE_ENABLE_STREAMING=true
VITE_ENABLE_FILE_UPLOAD=false
VITE_MAX_UPLOAD_SIZE=10485760

# UI Configuration
VITE_MAX_MESSAGES=100
VITE_ENABLE_DARK_MODE=true
VITE_DEFAULT_THEME=light

# Performance
VITE_ENABLE_CACHE=true
VITE_CACHE_TTL=3600

# AI Configuration
VITE_AI_API_KEY=your_api_key_here
VITE_AI_BASE_URL=http://localhost:1234
VITE_AI_PROVIDER=local-ai  # Options: local-ai, groq, claude
VITE_AI_MODEL=your-model-name
```

## Backend Environment (.env)
```env
# Model Settings
DEFAULT_MODEL=your-default-model
TEMPERATURE=0.7
TOP_P=0.9
MAX_TOKENS=200000

# Model Configuration
CLAUDE_HAIKU_MODEL=claude-3-haiku-20240307
CLAUDE_SONNET_MODEL=claude-3-sonnet-20240229
CLAUDE_OPUS_MODEL=claude-3-opus-20240229
GPT4_MODEL=gpt-4
GPT35_MODEL=gpt-3.5-turbo
GROQ_MODEL=llama-3.1-8b-instant

# LM Studio Settings
LM_STUDIO_MODEL=your-model-identifier
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# System Settings
SYSTEM_NAME=Claude
VERSION=1.a.6
ENVIRONMENT=development
DEBUG=false
RELOAD_ON_CHANGE=true

# Security Settings
ENABLE_SAFETY_FILTERS=true
CONTENT_FILTERING=true
MAX_TOKENS=100000
RATE_LIMIT=60
API_KEY_REQUIRED=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
SSL_VERIFY=true
MAX_REQUEST_SIZE=10485760

# Performance Settings
TIMEOUT=30
MAX_CONCURRENT_OPS=10
MAX_RETRIES=3
MEMORY_LIMIT=1073741824

# Resource Management
RESOURCE_PATH=resources
STORAGE_PATH=storage
TEMP_PATH=temp
CACHE_ENABLED=true
CACHE_SIZE=1000
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.txt,.md,.rst,.py,.js,.java,.cpp,.h,.json,.yaml,.yml,.csv,.svg
CLEANUP_INTERVAL=3600
MAX_STORAGE_SIZE=1073741824

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/claude.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
ROTATE_LOGS=true
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_CONSOLE_OUTPUT=true

# API Settings
BASE_URL=http://localhost:8000
CORS_ENABLED=true
EXPOSE_ERRORS=false

# Worker Settings
WORKER_COUNT=4
ENABLE_BACKGROUND_TASKS=true
TASK_QUEUE_SIZE=1000

# Monitoring
ENABLE_TELEMETRY=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=60

# Feature Flags
ENABLE_STREAMING=true
ENABLE_BATCH_PROCESSING=true
ENABLE_RATE_LIMITING=true
ENABLE_CACHING=true
```

## Docker Environment (.env.docker)
```env
# API Configuration
VITE_API_BASE_URL=http://api:8000
VITE_WS_BASE_URL=ws://api:8000

# Environment
NODE_ENV=production
DOCKER_BUILDKIT=1

# Runtime Configuration
PORT=80
HOST=0.0.0.0

# Resource Limits
MEMORY_LIMIT=512M
CPU_LIMIT=1

# Cache Configuration
NGINX_CACHE_STATUS=on
NGINX_CACHE_TIME=60m
```


## Development Requirements

- Node.js 18+
- npm 7+
- Docker and Docker Compose (for containerized deployment)

## Testing

```bash
# Run all tests
npm test

# Run frontend tests
npm run test --workspace frontend

# Run backend tests
npm run test --workspace claude-3.5-sonnet
```




## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
