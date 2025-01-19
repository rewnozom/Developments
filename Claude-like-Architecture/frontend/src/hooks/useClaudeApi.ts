import { useState, useCallback } from 'react';
import { useStreaming } from '../providers/StreamingProvider';
import { API_CONFIG, MODEL_CONFIG } from '../config/apiConfig';
import type { Message, ChatConfig, ChatResponse } from '../types/api';

interface UseClaudeApiOptions {
  useStreaming?: boolean;
}

export function useClaudeApi(options: UseClaudeApiOptions = {}) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { streamMessage, isStreaming, abortStream } = useStreaming();

  const sendMessage = useCallback(async (
    messages: Message[],
    config?: ChatConfig
  ): Promise<ChatResponse | null> => {
    try {
      setIsLoading(true);
      setError(null);

      // Use streaming if enabled and available
      if (options.useStreaming && API_CONFIG.options.streamingEnabled) {
        const streamedMessage = await streamMessage(messages);
        if (!streamedMessage) return null;

        return {
          id: streamedMessage.id,
          messages: [streamedMessage],
          metadata: {
            model: API_CONFIG.model,
            usage: {
              promptTokens: 0,
              completionTokens: 0,
              totalTokens: 0,
            },
          }
        };
      }

      // Regular non-streaming request
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(API_CONFIG.apiKey && { 'Authorization': `Bearer ${API_CONFIG.apiKey}` }),
        },
        body: JSON.stringify({
          messages,
          model: config?.model || API_CONFIG.model,
          temperature: config?.temperature ?? MODEL_CONFIG.temperature,
          max_tokens: config?.maxTokens ?? MODEL_CONFIG.maxTokens,
          stream: false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Request failed with status ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      console.error('API Error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [options.useStreaming, streamMessage]);

  const getModels = useCallback(async (): Promise<string[]> => {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.models}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }
      const data = await response.json();
      return data.models || [];
    } catch (err) {
      console.error('Error fetching models:', err);
      return [];
    }
  }, []);

  return {
    sendMessage,
    getModels,
    isLoading,
    isStreaming,
    error,
    abortStream,
  };
}