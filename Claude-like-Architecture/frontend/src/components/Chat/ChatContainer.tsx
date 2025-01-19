import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Sidebar } from '../Layout/Sidebar';
import { Menu } from 'lucide-react';
import { IconWrapper } from '../common/IconWrapper';
import { 
  useConversation, 
  useCreateConversation, 
  useDeleteConversation, 
  useRenameConversation 
} from '../../contexts/ConversationContext';
import { storageService } from '../../services/storage';
import type { ChatContainerProps } from './types';
import type { Message } from '../../types/api';

export const ChatContainer: React.FC<ChatContainerProps> = ({
  className = '',
}) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    conversations, 
    activeConversationId, 
    isLoading: isLoadingConversations,
    setActiveConversation,
    clearConversations 
  } = useConversation();
  
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();
  const renameConversation = useRenameConversation();

  // Load messages for active conversation
  const [messages, setMessages] = useState<Message[]>([]);
  useEffect(() => {
    if (activeConversationId) {
      const savedMessages = storageService.loadConversationMessages(activeConversationId);
      setMessages(savedMessages);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  // Chat hooks with message persistence
  const { 
    artifacts,
    isLoading: isLoadingChat, 
    error,
    sendMessage: baseSendMessage 
  } = useChat(messages);

  const sendMessage = async (content: string) => {
    try {
      if (!activeConversationId) {
        // Create new conversation if none exists
        const title = content.slice(0, 30) + (content.length > 30 ? '...' : '');
        createConversation(title);
        return;
      }

      const result = await baseSendMessage(content);
      if (result) {
        const newMessages = [...messages, result];
        setMessages(newMessages);
        storageService.saveConversationMessages(activeConversationId, newMessages);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleNewChat = () => {
    createConversation('New Chat');
  };

  const handleClearHistory = () => {
    clearConversations();
    setMessages([]);
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (isLoadingConversations) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-[#e5e5e5]">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setIsSidebarOpen(true)}
        className="fixed left-4 top-4 z-50 rounded-lg bg-[rgba(43,41,41,0.85)] p-2 text-[#e5e5e5] 
          shadow-lg backdrop-blur-sm lg:hidden"
      >
        <IconWrapper icon={Menu} className="h-6 w-6" />
      </button>

      <Sidebar 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onNewChat={handleNewChat}
        onClearHistory={handleClearHistory}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversation}
        onRenameConversation={renameConversation}
        onDeleteConversation={deleteConversation}
      />
      
      <div className={`flex flex-1 flex-col ${className}`}>
        {error && (
          <div className="m-4 rounded-lg border border-red-400/10 bg-red-400/10 p-4 text-red-400">
            {error}
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && !isLoadingChat ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <div className="text-xl font-medium text-[#e5e5e5]">
                Welcome to Claude Chat
              </div>
              <div className="text-[#a3a3a3]">
                Start a new conversation or select one from the sidebar.
              </div>
              <button
                onClick={handleNewChat}
                className="mt-4 rounded-lg bg-[#fb923c] px-6 py-2 font-medium text-white 
                  hover:bg-[#f97316] transition-colors duration-200"
              >
                New Chat
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  artifacts={artifacts[message.id]}
                  isLast={index === messages.length - 1}
                />
              ))}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          onSend={sendMessage}
          isLoading={isLoadingChat}
          isDisabled={!activeConversationId}
          placeholder={activeConversationId 
            ? "Ask Claude anything..." 
            : "Start a new chat to begin..."
          }
          className="border-t border-[rgba(82,82,82,0.3)] bg-[#262626] p-4"
        />
      </div>
    </div>
  );
};