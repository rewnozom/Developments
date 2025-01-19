import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, waitFor, act } from '@testing-library/react';
import { StreamingProvider, useStreaming } from '../StreamingProvider';
import { server } from '../../test/mocks/server';
import { rest } from 'msw';
import { API_CONFIG } from '../../config/apiConfig';

// Test component that uses the streaming hook
const TestComponent = ({ onMessage }: { onMessage: (msg: string) => void }) => {
  const { streamMessage, isStreaming, abortStream } = useStreaming();

  React.useEffect(() => {
    const messages = [{ role: 'user', content: 'Test message', id: '1' }];
    void streamMessage(messages).then((result) => {
      if (result) {
        onMessage(result.content);
      }
    });
  }, [onMessage, streamMessage]);

  return (
    <div>
      <div data-testid="streaming-status">{isStreaming ? 'Streaming' : 'Idle'}</div>
      <button onClick={abortStream}>Abort</button>
    </div>
  );
};

describe('StreamingProvider', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('handles successful streaming', async () => {
    const onMessage = vi.fn();
    const chunks = ['Hello', ' world', '!'];
    
    // Mock streaming response
    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          async start(controller) {
            for (const chunk of chunks) {
              const data = {
                id: '123',
                content: chunk,
                role: 'assistant'
              };
              controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
              await new Promise(resolve => setTimeout(resolve, 10));
            }
            controller.close();
          },
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledWith('Hello world!');
    });
  });

  it('handles stream abortion', async () => {
    const onMessage = vi.fn();
    let abortController: AbortController;

    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        abortController = new AbortController();
        const stream = new ReadableStream({
          start(controller) {
            const interval = setInterval(() => {
              if (abortController.signal.aborted) {
                clearInterval(interval);
                controller.close();
                return;
              }
              const data = { content: 'chunk' };
              controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(data)}\n\n`));
            }, 100);
          }
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    const { getByText } = render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    // Wait for streaming to start
    await waitFor(() => {
      expect(getByText('Streaming')).toBeInTheDocument();
    });

    // Click abort button
    getByText('Abort').click();

    // Check if streaming was stopped
    await waitFor(() => {
      expect(getByText('Idle')).toBeInTheDocument();
    });
  });

  it('handles network errors gracefully', async () => {
    const onMessage = vi.fn();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    const { getByText } = render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    await waitFor(() => {
      expect(getByText('Idle')).toBeInTheDocument();
    });

    expect(onMessage).not.toHaveBeenCalled();
    expect(consoleSpy).toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });

  it('handles malformed stream data', async () => {
    const onMessage = vi.fn();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('data: invalid json\n\n'));
            controller.close();
          }
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('accumulates streamed chunks correctly', async () => {
    const onMessage = vi.fn();
    const chunks = ['Hello', ' ', 'world', '!'];
    
    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          async start(controller) {
            for (const chunk of chunks) {
              const data = {
                id: '123',
                content: chunk,
                role: 'assistant'
              };
              controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
              await new Promise(resolve => setTimeout(resolve, 10));
            }
            controller.close();
          },
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledWith('Hello world!');
    });
  });

  it('handles reconnection on network failure', async () => {
    const onMessage = vi.fn();
    let failedOnce = false;

    server.use(
      rest.post(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, (req, res, ctx) => {
        if (!failedOnce) {
          failedOnce = true;
          return res(ctx.status(500));
        }

        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            const data = { content: 'Success after retry' };
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
            controller.close();
          }
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    render(
      <StreamingProvider>
        <TestComponent onMessage={onMessage} />
      </StreamingProvider>
    );

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledWith('Success after retry');
    });
  });
});