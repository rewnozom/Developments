import React, { createContext, useContext, useReducer } from 'react';
import { Message, Artifact } from '../types/api';

interface ChatContextState {
  messages: Message[];
  artifacts: Record<string, Artifact[]>;
  isLoading: boolean;
  error: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'ADD_ARTIFACTS'; messageId: string; artifacts: Artifact[] }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'CLEAR_CHAT' };

interface ChatContextType extends ChatContextState {
  addMessage: (message: Message) => void;
  addArtifacts: (messageId: string, artifacts: Artifact[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const initialState: ChatContextState = {
  messages: [],
  artifacts: {},
  isLoading: false,
  error: null,
};

function chatReducer(state: ChatContextState, action: ChatAction): ChatContextState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.message],
        error: null,
      };
    case 'ADD_ARTIFACTS':
      return {
        ...state,
        artifacts: {
          ...state.artifacts,
          [action.messageId]: action.artifacts,
        },
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.isLoading,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.error,
        isLoading: false,
      };
    case 'CLEAR_CHAT':
      return initialState;
    default:
      return state;
  }
}

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const value = {
    ...state,
    addMessage: (message: Message) => 
      dispatch({ type: 'ADD_MESSAGE', message }),
    addArtifacts: (messageId: string, artifacts: Artifact[]) =>
      dispatch({ type: 'ADD_ARTIFACTS', messageId, artifacts }),
    setLoading: (isLoading: boolean) =>
      dispatch({ type: 'SET_LOADING', isLoading }),
    setError: (error: string | null) =>
      dispatch({ type: 'SET_ERROR', error }),
    clearChat: () =>
      dispatch({ type: 'CLEAR_CHAT' }),
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
