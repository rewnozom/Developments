import { BaseProvider } from './base';
import { ChatMessage, ChatOptions } from './types';

export class GroqProvider extends BaseProvider {
  async *chat(messages: ChatMessage[], options: ChatOptions) {
    const response = await this.fetchWithTimeout(
      `${this.config.baseUrl || 'https://api.groq.com'}/v1/chat/completions`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages,
          model: this.config.model || 'llama-3.1-8b-instant',
          temperature: options.temperature ?? 1,
          max_tokens: options.maxTokens ?? 8192,
          top_p: options.topP ?? 1,
          stream: true,
        }),
      }
    );

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) throw new Error('No response body');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim());

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          yield data.choices[0]?.delta?.content || '';
        }
      }
    }
  }

  async listModels(): Promise<string[]> {
    const response = await this.fetchWithTimeout(
      `${this.config.baseUrl || 'https://api.groq.com'}/v1/models`,
      {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
        },
      }
    );
    const data = await response.json();
    return data.data.map((model: any) => model.id);
  }
}