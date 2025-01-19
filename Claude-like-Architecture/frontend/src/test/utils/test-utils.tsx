import React, { PropsWithChildren } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { SettingsProvider } from '../../contexts/SettingsContext';
import { ConversationProvider } from '../../contexts/ConversationContext';
import { StreamingProvider } from '../../providers/StreamingProvider';
import { ChatProvider } from '../../providers/ChatProvider';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { Message, Conversation } from '../../types/api';

interface WrapperProps {
  children: React.ReactNode;
}

const AllProviders = ({ children }: WrapperProps) => {
  return (
    <ThemeProvider>
      <SettingsProvider>
        <ConversationProvider>
          <StreamingProvider>
            <ChatProvider>
              {children}
            </ChatProvider>
          </StreamingProvider>
        </ConversationProvider>
      </SettingsProvider>
    </ThemeProvider>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const utils = rtlRender(ui, { wrapper: AllProviders, ...options });
  const user = userEvent.setup();
  return {
    user,
    ...utils,
  };
};

// Test data generators
export const createMockMessage = (overrides: Partial<Message> = {}): Message => ({
  id: 'test-message-id',
  role: 'user',
  content: 'Test message content',
  timestamp: new Date().toISOString(),
  ...overrides,
});

export const createMockConversation = (
  overrides: Partial<Conversation> = {}
): Conversation => ({
  id: 'test-conversation-id',
  title: 'Test Conversation',
  timestamp: new Date().toISOString(),
  ...overrides,
});

// Mock API responses
export const mockApiResponse = (data: any) => {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

// Mock streaming responses
export const mockStreamResponse = (chunks: string[]) => {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of chunks) {
        const encoded = encoder.encode(`data: ${JSON.stringify({ content: chunk })}\n\n`);
        controller.enqueue(encoded);
        await new Promise(resolve => setTimeout(resolve, 10));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
};

// Wait for loading states
export const waitForLoadingToFinish = async () => {
  return new Promise(resolve => setTimeout(resolve, 0));
};

// Mock intersection observer entries
export const mockIntersectionObserverEntry = (
  isIntersecting: boolean = true
): IntersectionObserverEntry => ({
  boundingClientRect: {} as DOMRectReadOnly,
  intersectionRatio: isIntersecting ? 1 : 0,
  intersectionRect: {} as DOMRectReadOnly,
  isIntersecting,
  rootBounds: null,
  target: document.createElement('div'),
  time: Date.now(),
});

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };