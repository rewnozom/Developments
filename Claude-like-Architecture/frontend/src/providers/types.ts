export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
  }
  
  export interface ChatOptions {
    temperature?: number;
    maxTokens?: number;
    topP?: number;
    stream?: boolean;
    stop?: string[] | null;
  }
  
  export interface ProviderConfig {
    apiKey?: string;
    baseUrl?: string;
    model?: string;
  }
  
  export interface AIProvider {
    initialize(config: ProviderConfig): Promise<void>;
    chat(messages: ChatMessage[], options: ChatOptions): AsyncIterableIterator<string>;
    listModels(): Promise<string[]>;
  }