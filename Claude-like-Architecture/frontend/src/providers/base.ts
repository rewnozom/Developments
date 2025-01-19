import { AIProvider, ProviderConfig, ChatMessage, ChatOptions } from './types';

export abstract class BaseProvider implements AIProvider {
  protected config: ProviderConfig = {};

  async initialize(config: ProviderConfig): Promise<void> {
    this.config = config;
  }

  abstract chat(messages: ChatMessage[], options: ChatOptions): AsyncIterableIterator<string>;
  abstract listModels(): Promise<string[]>;

  protected async fetchWithTimeout(url: string, options: RequestInit & { timeout?: number }) {
    const { timeout = 30000, ...fetchOptions } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }
}