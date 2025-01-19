import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '../../../test/utils/test-utils';
import { ConversationSearch } from '../ConversationSearch';

describe('ConversationSearch', () => {
  it('renders search input correctly', () => {
    const onSearch = vi.fn();
    render(<ConversationSearch onSearch={onSearch} />);
    
    expect(screen.getByPlaceholderText(/search conversation/i)).toBeInTheDocument();
  });

  it('debounces search input', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'test');

    // Should not call immediately
    expect(onSearch).not.toHaveBeenCalled();

    // Should call after debounce delay
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test');
    });
  });

  it('clears search input when clear button is clicked', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'test');

    // Wait for debounce
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test');
    });

    // Clear input
    const clearButton = screen.getByRole('button');
    await user.click(clearButton);

    expect(input).toHaveValue('');
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('');
    });
  });

  it('does not show clear button when input is empty', () => {
    const onSearch = vi.fn();
    render(<ConversationSearch onSearch={onSearch} />);
    
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('shows clear button when input has value', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'test');

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('applies custom className correctly', () => {
    const onSearch = vi.fn();
    const customClass = 'custom-class';
    render(<ConversationSearch onSearch={onSearch} className={customClass} />);
    
    const container = screen.getByRole('search');
    expect(container).toHaveClass(customClass);
  });

  it('handles special characters in search', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, '!@#$%^&*()');

    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('!@#$%^&*()');
    });
  });

  it('handles paste events', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.click(input);
    await user.paste('pasted text');

    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('pasted text');
    });
  });

  it('maintains focus after clearing', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'test');
    
    const clearButton = screen.getByRole('button');
    await user.click(clearButton);

    expect(input).toHaveFocus();
  });

  it('handles rapid input changes correctly', async () => {
    const onSearch = vi.fn();
    const { user } = render(<ConversationSearch onSearch={onSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fast');
    await user.type(input, 'typing');

    // Should only call with final value after debounce
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('fasttyping');
      expect(onSearch).toHaveBeenCalledTimes(1);
    });
  });
});