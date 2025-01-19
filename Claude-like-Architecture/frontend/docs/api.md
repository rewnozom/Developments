# API Integration Guide

## Overview

The chat interface supports multiple AI providers through a unified API layer:
- Claude API
- Local LM Studio
- Groq API

## Configuration

### Environment Variables

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_AI_PROVIDER=claude
VITE_AI_MODEL=claude-3-sonnet

# Authentication (if needed)
VITE_AI_API_KEY=your-api-key

# Local API (for LM Studio)
VITE_AI_BASE_URL=http://localhost:1234
```

### Provider Configuration

```typescript
// config/apiConfig.ts
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_BASE_URL,
  provider: import.meta.env.VITE_AI_PROVIDER,
  model: import.meta.env.VITE_AI_MODEL,
  apiKey: import.meta.env.VITE_AI_API_KEY,
  
  endpoints: {
    chat: '/api/chat',
    artifacts: '/api/artifacts',
    models: '/api/models',
  },
  
  options: {
    streamingEnabled: true,
    timeout: 30000,
    retryAttempts: 3,
  }
};
```

## API Endpoints

### Chat Endpoint

POST `/api/chat`

Request:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello!",
      "id": "msg-123"
    }
  ],
  "stream": true,
  "model": "claude-3-sonnet"
}
```

Response (non-streaming):
```json
{
  "id": "resp-456",
  "messages": [
    {
      "role": "assistant",
      "content": "Hello! How can I help you today?",
      "id": "msg-456"
    }
  ],
  "metadata": {
    "usage": {
      "promptTokens": 10,
      "completionTokens": 9,
      "totalTokens": 19
    }
  }
}
```

Streaming Response:
```
data: {"id":"resp-456","content":"Hello","role":"assistant"}

data: {"id":"resp-456","content":"! How can I ","role":"assistant"}

data: {"id":"resp-456","content":"help you today?","role":"assistant"}

data: [DONE]
```

### Models Endpoint

GET `/api/models`

Response:
```json
{
  "models": [
    {
      "id": "claude-3-sonnet",
      "name": "Claude 3 Sonnet",
      "maxTokens": 8192,
      "description": "Latest Claude model optimized for complex tasks"
    }
  ]
}
```

## Integration Examples

### Basic Usage

```typescript
import { useClaudeApi } from '@/hooks/useClaudeApi';

const MyComponent = () => {
  const { sendMessage, isLoading } = useClaudeApi();

  const handleSend = async (content: string) => {
    const result = await sendMessage([
      { role: 'user', content }
    ]);
    
    if (result) {
      // Handle response
    }
  };
};
```

### Streaming Usage

```typescript
import { useStreaming } from '@/providers/StreamingProvider';

const MyComponent = () => {
  const { streamMessage, isStreaming, abortStream } = useStreaming();

  const handleSend = async (content: string) => {
    const result = await streamMessage([
      { role: 'user', content }
    ]);
    
    if (result) {
      // Handle completed message
    }
  };

  // Cancel streaming if needed
  const handleCancel = () => {
    abortStream();
  };
};
```

## Error Handling

```typescript
try {
  const result = await sendMessage(messages);
} catch (error) {
  if (error instanceof APIError) {
    switch (error.code) {
      case 'token_limit_exceeded':
        // Handle token limit
        break;
      case 'rate_limit_exceeded':
        // Handle rate limit
        break;
      case 'invalid_request':
        // Handle invalid request
        break;
      default:
        // Handle other errors
    }
  }
}
```

## Backend Health Check

```typescript
import { validateBackendConfig } from '@/config/apiConfig';

const checkBackend = async () => {
  const isAvailable = await validateBackendConfig();
  if (!isAvailable) {
    console.error('Backend is not available');
  }
};
```

## Provider-Specific Configuration

### Claude

```typescript
const claudeConfig = {
  model: 'claude-3-sonnet',
  maxTokens: 8192,
  temperature: 0.7,
  topP: 0.9,
};
```

### Local LM Studio

```typescript
const lmStudioConfig = {
  baseUrl: 'http://localhost:1234',
  model: 'model-identifier',
  maxTokens: 8192,
};
```

### Groq

```typescript
const groqConfig = {
  apiKey: 'your-groq-api-key',
  model: 'llama-3.1-8b-instant',
  maxTokens: 8192,
};
```

## WebSocket Events

```typescript
const wsUrl = `${API_CONFIG.wsBaseUrl}/chat`;
const ws = new WebSocket(wsUrl);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle streaming message
};

ws.onerror = (error) => {
  // Handle WebSocket error
};

ws.onclose = () => {
  // Handle connection close
};
```