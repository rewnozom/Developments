import React from 'react';
import { User, Bot } from 'lucide-react';
import { ChatMessageProps } from './types';
import { ResponseContent } from '../Response/ResponseContent';

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  artifacts,
  isLast,
  className = '',
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 p-4 ${isUser ? 'bg-gray-50' : 'bg-white'} ${className}`}>
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      
      <div className="flex-1">
        <div className="mb-1 text-sm font-medium text-gray-500">
          {isUser ? 'You' : 'Claude'}
        </div>
        
        <ResponseContent 
          content={message.content} 
          artifacts={artifacts}
          isLast={isLast}
        />
        
        {message.metadata && message.metadata.processingTime && (
          <div className="mt-2 text-xs text-gray-400">
            Processed in {message.metadata.processingTime.toFixed(2)}s
          </div>
        )}
      </div>
    </div>
  );
};
