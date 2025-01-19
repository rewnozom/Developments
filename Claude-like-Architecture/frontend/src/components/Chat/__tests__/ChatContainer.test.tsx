import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../../../test/utils/test-utils';
import { ChatContainer } from '../ChatContainer';
import { server } from '../../../test/mocks/server';
import { rest } from 'msw';
import { API_CONFIG } from '../../../config/apiConfig';

describe('ChatContainer', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders initial empty state correctly', () => {
    render(<ChatContainer />);
    
    expect(screen.getByText(/Welcome to Claude Chat/i)).toBeInTheDocument();
    expect(screen.getByText(/Start a new conversation/i)).toBeInTheDocument();
  });

  it('shows loading state when sending message', async () => {
    const { user } = render(<ChatContainer />);
    
    // Find and type in the input
    const input = screen.getByRole('textbox');
    await user.type(input, 'Hello Claude{Enter}');

    // Check loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for response
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('displays messages correctly', async () => {
    const { user } = render(<ChatContainer />);
    
    // Send a message
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');

    // Wait for both user message and response to appear
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
      expect(screen.getByText(/Response to: Test message/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock an API error
    server.use(
      rest.post(`${API_CONFIG.baseUrl}/api/chat`, (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({ error: 'Internal Server Error' })
        );
      })
    );

    const { user } = render(<ChatContainer />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('preserves messages between renders', async () => {
    const { user, rerender } = render(<ChatContainer />);
    
    // Send message
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    // Rerender component
    rerender(<ChatContainer />);

    // Check if messages are still there
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('handles streaming responses correctly', async () => {
    // Mock streaming response
    server.use(
      rest.post(`${API_CONFIG.baseUrl}/api/chat`, (req, res, ctx) => {
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          async start(controller) {
            const chunks = ['Hello', ' world', '!'];
            for (const chunk of chunks) {
              const data = JSON.stringify({ content: chunk });
              controller.enqueue(encoder.encode(`data: ${data}\n\n`));
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

    const { user } = render(<ChatContainer />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Stream test{Enter}');

    await waitFor(() => {
      expect(screen.getByText('Hello world!')).toBeInTheDocument();
    });
  });

  it('handles sidebar toggle correctly', async () => {
    const { user } = render(<ChatContainer />);
    
    // Click sidebar toggle
    const toggleButton = screen.getByLabelText(/toggle sidebar/i);
    await user.click(toggleButton);

    // Check if sidebar is visible
    expect(screen.getByText(/conversations/i)).toBeInTheDocument();

    // Click toggle again to hide
    await user.click(toggleButton);

    // Check if sidebar is hidden
    await waitFor(() => {
      const sidebar = screen.queryByText(/conversations/i);
      expect(sidebar).not.toBeVisible();
    });
  });

  it('handles conversation switching', async () => {
    const { user } = render(<ChatContainer />);
    
    // Create first conversation
    const input = screen.getByRole('textbox');
    await user.type(input, 'First conversation{Enter}');

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('First conversation')).toBeInTheDocument();
    });

    // Start new chat
    const newChatButton = screen.getByText(/new chat/i);
    await user.click(newChatButton);

    // Send message in new conversation
    await user.type(input, 'Second conversation{Enter}');

    // Verify both conversations exist
    await waitFor(() => {
      expect(screen.getByText('Second conversation')).toBeInTheDocument();
    });

    // Switch back to first conversation
    const firstConvButton = screen.getByText('First conversation');
    await user.click(firstConvButton);

    // Verify first conversation's messages are shown
    expect(screen.getByText('First conversation')).toBeInTheDocument();
  });

  it('shows error when backend is unavailable', async () => {
    // Mock backend unavailable
    server.use(
      rest.get(`${API_CONFIG.baseUrl}/api/health`, (req, res, ctx) => {
        return res(ctx.status(503));
      })
    );

    render(<ChatContainer />);

    await waitFor(() => {
      expect(screen.getByText(/backend connection error/i)).toBeInTheDocument();
    });
  });

  it('maintains correct message order', async () => {
    const { user } = render(<ChatContainer />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'First message{Enter}');
    await user.type(input, 'Second message{Enter}');

    const messages = await screen.findAllByRole('article');
    expect(messages).toHaveLength(4); // 2 user messages + 2 responses
    
    // Check order
    const messageTexts = messages.map(msg => msg.textContent);
    expect(messageTexts).toEqual(
      expect.arrayContaining(['First message', 'Second message'])
    );
  });
});