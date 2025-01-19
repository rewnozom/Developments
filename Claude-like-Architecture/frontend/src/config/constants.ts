export const APP_CONFIG = {
  name: 'Claude UI',
  version: '1.0.0',
  description: 'Frontend interface for Claude 3.5 Sonnet',
  apiVersion: 'v1',
} as const;

export const API_ENDPOINTS = {
  chat: '/api/chat',
  artifacts: '/api/artifacts',
  models: '/api/models',
  health: '/api/health',
} as const;

export const LIMITS = {
  maxMessageLength: 32000,
  maxMessages: 100,
  maxHistoryLength: 50,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  rateLimitPerMinute: 60,
} as const;

export const TIMEOUTS = {
  request: 30000, // 30 seconds
  socket: 60000,  // 1 minute
  typing: 1000,   // 1 second
  debounce: 300,  // 300ms
} as const;

export const STORAGE_KEYS = {
  theme: 'claude_theme',
  settings: 'claude_settings',
  history: 'claude_history',
  context: 'claude_context',
} as const;

export const DEFAULT_THEMES = {
  light: {
    primary: '#2563eb',
    background: '#ffffff',
    text: '#1f2937',
    border: '#e5e7eb',
  },
  dark: {
    primary: '#3b82f6',
    background: '#1f2937',
    text: '#f3f4f6',
    border: '#374151',
  },
} as const;

export const MIME_TYPES = {
  code: 'application/vnd.ant.code',
  markdown: 'text/markdown',
  html: 'text/html',
  svg: 'image/svg+xml',
  mermaid: 'application/vnd.ant.mermaid',
  react: 'application/vnd.ant.react',
} as const;

export const MESSAGE_TYPES = {
  text: 'text',
  code: 'code',
  artifact: 'artifact',
  error: 'error',
  system: 'system',
} as const;

export const ERROR_MESSAGES = {
  networkError: 'Unable to connect to the server. Please check your internet connection.',
  serverError: 'An error occurred while processing your request. Please try again later.',
  validationError: 'Invalid input. Please check your input and try again.',
  rateLimitError: 'Rate limit exceeded. Please wait before making more requests.',
  timeoutError: 'Request timed out. Please try again.',
  authError: 'Authentication failed. Please log in again.',
} as const;

export const KEYBOARD_SHORTCUTS = {
  sendMessage: 'Enter',
  newLine: 'Shift+Enter',
  clearChat: 'Ctrl+L',
  focusInput: '/',
  toggleTheme: 'Ctrl+T',
} as const;

export const ANIMATIONS = {
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  },
} as const;
