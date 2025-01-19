import React, { createContext, useContext, useCallback, useReducer, useEffect } from 'react';
import { useClaudeApi } from '../hooks/useClaudeApi';
import { API_CONFIG } from '../config/apiConfig';
import type { Message, ChatState } from '../types/api';

interface ChatContextType extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
  abortCurrentMessage: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

type ChatAction =
  | { type: 'SET_MESSAGES'; messages: Message[] }
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'CLEAR_CHAT' };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'SET_MESSAGES':
      return { ...state, messages: action.messages };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] };
    case 'SET_LOADING':
      return { ...state, isLoading: action.isLoading };
    case 'SET_ERROR':
      return { ...state, error: action.error };
    case 'CLEAR_CHAT':
      return { messages: [], isLoading: false, error: null };
    default:
      return state;
  }
};

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const { sendMessage: apiSendMessage, abortStream, isStreaming } = useClaudeApi({
    useStreaming: API_CONFIG.options.streamingEnabled,
  });

  // Load messages from storage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      dispatch({ type: 'SET_MESSAGES', messages: JSON.parse(savedMessages) });
    }
  }, []);

  // Save messages to storage on update
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(state.messages));
  }, [state.messages]);

  const sendMessage = useCallback(async (content: string) => {
    try {
      dispatch({ type: 'SET_LOADING', isLoading: true });
      dispatch({ type: 'SET_ERROR', error: null });

      // Add user message
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      dispatch({ type: 'ADD_MESSAGE', message: userMessage });

      // Get all messages for context
      const messages = [...state.messages, userMessage];
      
      // Send to API
      const response = await apiSendMessage(messages);
      
      if (response?.messages[0]) {
        dispatch({ type: 'ADD_MESSAGE', message: response.messages[0] });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      dispatch({ type: 'SET_ERROR', error: errorMessage });
    } finally {
      dispatch({ type: 'SET_LOADING', isLoading: false });
    }
  }, [state.messages, apiSendMessage]);

  const clearChat = useCallback(() => {
    dispatch({ type: 'CLEAR_CHAT' });
    localStorage.removeItem('chatMessages');
  }, []);

  const value = {
    ...state,
    sendMessage,
    clearChat,
    abortCurrentMessage: abortStream,
    isStreaming,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};