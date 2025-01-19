import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/utils/test-utils';
import { ChatMessage } from './ChatMessage';
import { createMockMessage, createMockArtifact } from '@/test/utils/test-utils';

describe('ChatMessage', () => {
  it('renders user message correctly', () => {
    const message = createMockMessage({ role: 'user' });
    render(<ChatMessage message={message} />);

    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText(message.content)).toBeInTheDocument();
  });

  it('renders assistant message correctly', () => {
    const message = createMockMessage({ role: 'assistant' });
    render(<ChatMessage message={message} />);

    expect(screen.getByText('Claude')).toBeInTheDocument();
    expect(screen.getByText(message.content)).toBeInTheDocument();
  });

  it('renders artifacts when provided', () => {
    const message = createMockMessage({ role: 'assistant' });
    const artifacts = [
      createMockArtifact(),
      createMockArtifact({ id: 'test-2', type: 'markdown' }),
    ];

    render(<ChatMessage message={message} artifacts={artifacts} />);

    artifacts.forEach(artifact => {
      expect(screen.getByText(artifact.content)).toBeInTheDocument();
    });
  });

  it('shows processing time when provided in metadata', () => {
    const message = createMockMessage({
      role: 'assistant',
      metadata: { processingTime: 1.5 },
    });

    render(<ChatMessage message={message} />);
    expect(screen.getByText(/Processed in 1.50s/)).toBeInTheDocument();
  });

  it('applies isLast prop styling correctly', () => {
    const message = createMockMessage();
    const { container } = render(<ChatMessage message={message} isLast={true} />);
    
    expect(container.firstChild).toHaveClass('animate-fade-in');
  });
});
