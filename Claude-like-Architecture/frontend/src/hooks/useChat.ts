import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message, ChatResponse } from '../types/api';
import { claudeApi } from '../api/claude';

export function useChat(initialMessages: Message[] = []) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [artifacts, setArtifacts] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await claudeApi.sendMessage([
        ...messages,
        userMessage,
      ]);

      if (response.artifacts) {
        setArtifacts(prev => ({
          ...prev,
          [response.id]: response.artifacts,
        }));
      }

      setMessages(prev => [
        ...prev,
        {
          id: response.id,
          role: 'assistant',
          content: response.messages[0].content,
          timestamp: new Date().toISOString(),
          metadata: response.metadata,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setArtifacts({});
    setError(null);
  }, []);

  return {
    messages,
    artifacts,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
}
