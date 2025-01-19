import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '../useChat';
import { server } from '../../test/mocks/server';
import { rest } from 'msw';
import { API_CONFIG } from '../../config/apiConfig';
import { createMockMessage } from '../../test/utils/test-utils';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <div>{children}</div>
);

describe('useChat', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('sends messages successfully', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(result.current.messages).toHaveLength(2); // User message + response
    expect(result.current.messages[0].content).toBe('Test message');
    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[1].role).toBe('assistant');
  });

  it('handles API errors', async () => {
    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(result.current.error).toBeTruthy();
  });

  it('maintains message order', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('First message');
      await result.current.sendMessage('Second message');
    });

    expect(result.current.messages[0].content).toBe('First message');
    expect(result.current.messages[2].content).toBe('Second message');
  });

  it('clears chat history', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(result.current.messages).toHaveLength(2);

    act(() => {
      result.current.clearChat();
    });

    expect(result.current.messages).toHaveLength(0);
  });

  it('preserves messages between re-renders', async () => {
    const { result, rerender } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(result.current.messages).toHaveLength(2);

    rerender();

    expect(result.current.messages).toHaveLength(2);
  });

  it('handles streaming responses', async () => {
    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        const stream = new ReadableStream({
          start(controller) {
            const encoder = new TextEncoder();
            const data = { content: 'Streamed response' };
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
            controller.close();
          }
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    await waitFor(() => {
      expect(result.current.messages[1].content).toBe('Streamed response');
    });
  });

  it('updates loading state correctly', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      const promise = result.current.sendMessage('Test message');
      expect(result.current.isLoading).toBe(true);
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('handles concurrent messages correctly', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });

    await act(async () => {
      const promises = [
        result.current.sendMessage('First message'),
        result.current.sendMessage('Second message')
      ];
      await Promise.all(promises);
    });

    expect(result.current.messages.filter(m => m.role === 'user')).toHaveLength(2);
    expect(result.current.messages.filter(m => m.role === 'assistant')).toHaveLength(2);
  });

  it('maintains message state with useEffect cleanup', () => {
    const messages = [createMockMessage(), createMockMessage()];
    const { result, unmount } = renderHook(() => useChat(messages), { wrapper });

    expect(result.current.messages).toEqual(messages);

    unmount();

    // After unmounting, messages should be saved to localStorage
    const savedMessages = localStorage.getItem('chatMessages');
    expect(savedMessages).toBeTruthy();
    expect(JSON.parse(savedMessages!)).toEqual(messages);
  });
});