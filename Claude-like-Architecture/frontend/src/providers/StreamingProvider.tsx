import React, { createContext, useContext, useCallback, useState } from 'react';
import { API_CONFIG } from '../config/apiConfig';
import { Message } from '../types/api';

interface StreamingContextType {
  isStreaming: boolean;
  streamMessage: (messages: Message[]) => Promise<Message | null>;
  abortStream: () => void;
}

const StreamingContext = createContext<StreamingContextType | undefined>(undefined);

export const StreamingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [controller, setController] = useState<AbortController | null>(null);

  const abortStream = useCallback(() => {
    if (controller) {
      controller.abort();
      setController(null);
      setIsStreaming(false);
    }
  }, [controller]);

  const streamMessage = useCallback(async (messages: Message[]): Promise<Message | null> => {
    try {
      setIsStreaming(true);
      const newController = new AbortController();
      setController(newController);

      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(API_CONFIG.apiKey && { 'Authorization': `Bearer ${API_CONFIG.apiKey}` }),
        },
        body: JSON.stringify({
          messages,
          stream: true,
          model: API_CONFIG.model,
        }),
        signal: newController.signal,
      });

      if (!response.ok) {
        throw new Error('Stream request failed');
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedMessage = '';
      let messageId = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              continue;
            }

            try {
              const parsed = JSON.parse(data);
              if (!messageId) {
                messageId = parsed.id;
              }
              if (parsed.content) {
                accumulatedMessage += parsed.content;
              }
            } catch (error) {
              console.error('Error parsing stream chunk:', error);
            }
          }
        }
      }

      const finalMessage: Message = {
        id: messageId || crypto.randomUUID(),
        role: 'assistant',
        content: accumulatedMessage,
        timestamp: new Date().toISOString(),
      };

      return finalMessage;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Stream aborted');
        return null;
      }
      console.error('Streaming error:', error);
      throw error;
    } finally {
      setIsStreaming(false);
      setController(null);
    }
  }, []);

  const value = {
    isStreaming,
    streamMessage,
    abortStream,
  };

  return (
    <StreamingContext.Provider value={value}>
      {children}
    </StreamingContext.Provider>
  );
};

export const useStreaming = () => {
  const context = useContext(StreamingContext);
  if (context === undefined) {
    throw new Error('useStreaming must be used within a StreamingProvider');
  }
  return context;
};