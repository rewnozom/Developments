const getEnvVar = (key: string, defaultValue?: string): string => {
  const value = import.meta.env[key];
  if (value === undefined && defaultValue === undefined) {
    throw new Error(`Environment variable ${key} is not defined`);
  }
  return value ?? defaultValue!;
};

export const API_CONFIG = {
  baseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
  wsBaseUrl: getEnvVar('VITE_WS_BASE_URL', 'ws://localhost:8000'),
  provider: getEnvVar('VITE_AI_PROVIDER', 'claude'),
  model: getEnvVar('VITE_AI_MODEL', 'claude-3-sonnet'),
  apiKey: getEnvVar('VITE_AI_API_KEY', ''),
  apiVersion: 'v1',
  
  endpoints: {
    chat: '/api/chat',
    artifacts: '/api/artifacts',
    models: '/api/models',
    health: '/api/health',
  },
  
  defaultHeaders: {
    'Content-Type': 'application/json',
  },

  options: {
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000,
    streamingEnabled: getEnvVar('VITE_ENABLE_STREAMING', 'true') === 'true',
  },
};

export const MODEL_CONFIG = {
  maxTokens: 8192,
  temperature: 0.7,
  topP: 0.9,
  streaming: true,
  systemPrompt: getEnvVar('VITE_SYSTEM_PROMPT', 'You are Claude, an AI assistant created by Anthropic.'),
};

export const ERROR_MESSAGES = {
  connectionFailed: 'Unable to connect to the server. Please check your internet connection.',
  requestFailed: 'Request failed. Please try again.',
  tokenLimitExceeded: 'Message exceeds maximum token limit.',
  invalidResponse: 'Received invalid response from server.',
  streamingError: 'Error occurred during streaming. Please try again.',
};

// Validate backend connectivity and model availability
export const validateBackendConfig = async () => {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/health`);
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }
    const data = await response.json();
    console.log('Backend health check:', data);
    return true;
  } catch (error) {
    console.error('Backend validation error:', error);
    return false;
  }
};

// Initialize API configuration
export const initializeApi = async () => {
  const isBackendAvailable = await validateBackendConfig();
  if (!isBackendAvailable) {
    console.warn('Backend is not available, falling back to local mode if configured');
  }
  
  // Additional initialization logic can be added here
  return isBackendAvailable;
};