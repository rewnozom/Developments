import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { IconWrapper } from '../common/IconWrapper';
import { draftManager } from '../../services/draftManager';
import { ChatInputProps } from './types';

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  isLoading = false,
  isDisabled = false,
  conversationId,
  placeholder = 'Type your message...',
  className = '',
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const draftTimeoutRef = useRef<NodeJS.Timeout>();

  // Load draft on mount or conversation change
  useEffect(() => {
    if (conversationId) {
      const draft = draftManager.loadDraft(conversationId);
      if (draft) {
        setMessage(draft);
      } else {
        setMessage('');
      }
    }
  }, [conversationId]);

  // Save draft when message changes
  useEffect(() => {
    if (conversationId && message) {
      clearTimeout(draftTimeoutRef.current);
      draftTimeoutRef.current = setTimeout(() => {
        draftManager.saveDraft(conversationId, message);
      }, 1000);
    }
    return () => clearTimeout(draftTimeoutRef.current);
  }, [message, conversationId]);

  // Adjust textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 200);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [message]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !isDisabled) {
      try {
        await onSend(message.trim());
        if (conversationId) {
          draftManager.deleteDraft(conversationId);
        }
        setMessage('');
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit(e);
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className={`flex items-end gap-2 ${className}`}
    >
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading || isDisabled}
        className={`flex-1 resize-none rounded-lg border bg-[#1a1a1a] p-3 text-[#e5e5e5]
          placeholder:text-[#a3a3a3] focus:outline-none
          ${isDisabled
            ? 'border-[rgba(82,82,82,0.3)] bg-opacity-50'
            : 'border-[rgba(82,82,82,0.3)] focus:border-[#fb923c]'
          }
          ${isLoading ? 'cursor-not-allowed opacity-50' : ''}
        `}
        rows={1}
      />
      
      <button
        type="submit"
        disabled={!message.trim() || isLoading || isDisabled}
        className={`rounded-lg p-3 transition-colors duration-200
          ${(!message.trim() || isLoading || isDisabled)
            ? 'cursor-not-allowed bg-[rgba(82,82,82,0.3)] text-[#a3a3a3]'
            : 'bg-[#fb923c] text-white hover:bg-[#f97316]'
          }
        `}
      >
        <IconWrapper icon={Send} className="h-5 w-5" />
      </button>
    </form>
  );
};