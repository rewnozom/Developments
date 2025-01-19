import { rest } from 'msw';
import { API_CONFIG } from '../../config/apiConfig';
import { createMockMessage } from '../utils/test-utils';

export const handlers = [
  // Chat endpoint
  rest.post(`${API_CONFIG.baseUrl}/api/chat`, async (req, res, ctx) => {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1];

    // Check if streaming is requested
    if (req.headers.get('accept') === 'text/event-stream') {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          const chunks = ['Hello', ' world', '!'];
          for (const chunk of chunks) {
            const data = {
              id: 'test-response-id',
              content: chunk,
              role: 'assistant',
            };
            const encoded = encoder.encode(`data: ${JSON.stringify(data)}\n\n`);
            controller.enqueue(encoded);
            await new Promise(resolve => setTimeout(resolve, 10));
          }
          controller.close();
        },
      });

      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream' },
      });
    }

    // Regular response
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        id: 'test-response-id',
        messages: [
          createMockMessage({
            id: 'test-response-id',
            role: 'assistant',
            content: `Response to: ${lastMessage.content}`,
          }),
        ],
        metadata: {
          model: API_CONFIG.model,
          usage: {
            promptTokens: 100,
            completionTokens: 50,
            totalTokens: 150,
          },
        },
      })
    );
  }),

  // Health check endpoint
  rest.get(`${API_CONFIG.baseUrl}/api/health`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'ok',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
      })
    );
  }),

  // Models endpoint
  rest.get(`${API_CONFIG.baseUrl}/api/models`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        models: [
          'claude-3-opus',
          'claude-3-sonnet',
          'claude-3-haiku',
        ],
      })
    );
  }),

  // Error handling test endpoint
  rest.post(`${API_CONFIG.baseUrl}/api/chat/error`, async (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        error: 'Internal Server Error',
        message: 'Test error response',
      })
    );
  }),
];