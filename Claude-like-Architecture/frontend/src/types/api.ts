export interface ApiConfig {
  baseUrl: string;
  apiKey?: string;
  version: string;
  timeout: number;
  retries: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

export interface PaginationParams {
  page: number;
  limit: number;
  cursor?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
  nextCursor?: string;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean>;
  body?: any;
  timeout?: number;
  signal?: AbortSignal;
}

export interface ApiClientOptions {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
  retries?: number;
}

export type ApiMethod = <T>(
  path: string,
  config?: Partial<RequestConfig>
) => Promise<ApiResponse<T>>;

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string; // Updated to string for consistency
  metadata?: Record<string, any>;
}

export interface Artifact {
  id: string;
  type: 'code' | 'markdown' | 'html' | 'svg' | 'mermaid' | 'react'; // Specific types
  content: string;
  title?: string; // Made optional since it was missing in src/types/api.ts
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  id: string; // Added for consistency with src/api/types/api.ts
  messages: Message[]; // Updated to an array
  artifacts?: Artifact[];
  metadata?: {
    processingTime: number;
    tokenCount: number;
    modelVersion: string;
  };
}

export interface ChatConfig {
  maxTokens?: number;
  temperature?: number;
  stopSequences?: string[];
  model?: string;
}
