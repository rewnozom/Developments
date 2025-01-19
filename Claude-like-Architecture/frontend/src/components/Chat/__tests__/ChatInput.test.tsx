import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../../test/utils/test-utils';
import { ChatInput } from '../ChatInput';

describe('ChatInput', () => {
  it('renders correctly', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('handles text input', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Hello, Claude!');
    
    expect(input).toHaveValue('Hello, Claude!');
  });

  it('calls onSend when submit button is clicked', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message');
    await user.click(screen.getByRole('button'));
    
    expect(onSend).toHaveBeenCalledWith('Test message');
    expect(input).toHaveValue('');
  });

  it('calls onSend when Enter is pressed', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');
    
    expect(onSend).toHaveBeenCalledWith('Test message');
    expect(input).toHaveValue('');
  });

  it('does not submit empty messages', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    await user.click(screen.getByRole('button'));
    
    expect(onSend).not.toHaveBeenCalled();
  });

  it('handles disabled state correctly', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} isDisabled />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('handles loading state correctly', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} isLoading />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('allows multiline input with Shift+Enter', async () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
    
    expect(onSend).not.toHaveBeenCalled();
  });

  it('auto-resizes textarea based on content', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox') as HTMLTextAreaElement;
    const initialHeight = input.clientHeight;
    
    // Type multiple lines
    await user.type(input, 'Line 1\nLine 2\nLine 3\nLine 4');
    
    await waitFor(() => {
      expect(input.clientHeight).toBeGreaterThan(initialHeight);
    });
  });

  it('trims whitespace from messages before sending', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, '   Test message with spaces   ');
    await user.click(screen.getByRole('button'));
    
    expect(onSend).toHaveBeenCalledWith('Test message with spaces');
  });

  it('preserves input state when disabled/enabled toggles', async () => {
    const onSend = vi.fn();
    const { rerender, user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message');
    
    // Disable input
    rerender(<ChatInput onSend={onSend} isDisabled />);
    expect(input).toHaveValue('Test message');
    
    // Enable input
    rerender(<ChatInput onSend={onSend} />);
    expect(input).toHaveValue('Test message');
  });

  it('shows custom placeholder text', () => {
    const onSend = vi.fn();
    const placeholder = 'Custom placeholder';
    render(<ChatInput onSend={onSend} placeholder={placeholder} />);
    
    expect(screen.getByPlaceholderText(placeholder)).toBeInTheDocument();
  });

  it('applies custom className correctly', () => {
    const onSend = vi.fn();
    const customClass = 'custom-class';
    render(<ChatInput onSend={onSend} className={customClass} />);
    
    const form = screen.getByRole('form');
    expect(form).toHaveClass(customClass);
  });

  it('focuses input on mount', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveFocus();
  });

  it('maintains focus after sending message', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');
    
    expect(input).toHaveFocus();
  });

  it('prevents default form submission', async () => {
    const onSend = vi.fn();
    const preventDefault = vi.fn();
    render(<ChatInput onSend={onSend} />);
    
    const form = screen.getByRole('form');
    fireEvent.submit(form, { preventDefault });
    
    expect(preventDefault).toHaveBeenCalled();
  });

  it('handles error case when onSend throws', async () => {
    const error = new Error('Send failed');
    const onSend = vi.fn().mockRejectedValue(error);
    const { user } = render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test message{Enter}');
    
    // Input should still be enabled and contain the message
    expect(input).not.toBeDisabled();
    expect(input).toHaveValue('Test message');
  });
});