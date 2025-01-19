import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { storageService } from '../services/storage';
import { Conversation, ConversationAction, ConversationContextType } from '../types/conversation';

interface State {
  conversations: Conversation[];
  activeConversationId?: string;
  isLoading: boolean;
}

type Action =
  | { type: 'SET_STATE'; payload: Partial<State> }
  | { type: 'ADD_CONVERSATION'; conversation: Conversation }
  | { type: 'UPDATE_CONVERSATION'; conversation: Conversation }
  | { type: 'DELETE_CONVERSATION'; id: string }
  | { type: 'SET_ACTIVE_CONVERSATION'; id: string }
  | { type: 'IMPORT_CONVERSATIONS'; conversations: Conversation[] }
  | { type: 'CLEAR_CONVERSATIONS' };

const initialState: State = {
  conversations: [],
  activeConversationId: undefined,
  isLoading: true,
};

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

function conversationReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_STATE':
      return { ...state, ...action.payload };
    
    case 'ADD_CONVERSATION': {
      const newState = {
        ...state,
        conversations: [action.conversation, ...state.conversations],
        activeConversationId: action.conversation.id,
      };
      storageService.saveConversations(newState.conversations, newState.activeConversationId);
      return newState;
    }
    
    case 'UPDATE_CONVERSATION': {
      const newState = {
        ...state,
        conversations: state.conversations.map(conv =>
          conv.id === action.conversation.id ? action.conversation : conv
        ),
      };
      storageService.saveConversations(newState.conversations, newState.activeConversationId);
      return newState;
    }
    
    case 'DELETE_CONVERSATION': {
      const newState = {
        ...state,
        conversations: state.conversations.filter(conv => conv.id !== action.id),
        activeConversationId: state.activeConversationId === action.id
          ? state.conversations[1]?.id
          : state.activeConversationId,
      };
      storageService.saveConversations(newState.conversations, newState.activeConversationId);
      return newState;
    }
    
    case 'SET_ACTIVE_CONVERSATION': {
      const newState = {
        ...state,
        activeConversationId: action.id,
      };
      storageService.saveConversations(state.conversations, newState.activeConversationId);
      return newState;
    }

    case 'IMPORT_CONVERSATIONS': {
      const existingIds = new Set(state.conversations.map(c => c.id));
      const newConversations = action.conversations.filter(c => !existingIds.has(c.id));
      
      const newState = {
        ...state,
        conversations: [...state.conversations, ...newConversations],
      };
      storageService.saveConversations(newState.conversations, newState.activeConversationId);
      return newState;
    }
    
    case 'CLEAR_CONVERSATIONS': {
      storageService.clearAll();
      return { ...initialState, isLoading: false };
    }
    
    default:
      return state;
  }
}

export const ConversationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(conversationReducer, initialState);

  useEffect(() => {
    const loadSavedConversations = async () => {
      const { conversations, activeConversationId } = storageService.loadConversations();
      dispatch({
        type: 'SET_STATE',
        payload: {
          conversations,
          activeConversationId,
          isLoading: false,
        },
      });
    };

    loadSavedConversations();
  }, []);

  const handleAction = useCallback((action: ConversationAction) => {
    switch (action.type) {
      case 'create':
        dispatch({
          type: 'ADD_CONVERSATION',
          conversation: {
            ...action.conversation,
            id: uuidv4(),
            timestamp: new Date().toISOString(),
          },
        });
        break;
      
      case 'update':
      case 'rename':
        dispatch({
          type: 'UPDATE_CONVERSATION',
          conversation: action.conversation,
        });
        break;
      
      case 'delete':
        dispatch({
          type: 'DELETE_CONVERSATION',
          id: action.conversation.id,
        });
        break;
    }
  }, []);

  const setActiveConversation = useCallback((id: string) => {
    dispatch({ type: 'SET_ACTIVE_CONVERSATION', id });
  }, []);

  const clearConversations = useCallback(() => {
    dispatch({ type: 'CLEAR_CONVERSATIONS' });
  }, []);

  const importConversations = useCallback((conversations: Conversation[]) => {
    dispatch({ type: 'IMPORT_CONVERSATIONS', conversations });
  }, []);

  const value = {
    conversations: state.conversations,
    activeConversationId: state.activeConversationId,
    isLoading: state.isLoading,
    handleAction,
    setActiveConversation,
    clearConversations,
    importConversations,
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
};

// Export hooks
export const useConversation = () => {
  const context = useContext(ConversationContext);
  if (context === undefined) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
};

export const useActiveConversation = () => {
  const { conversations, activeConversationId } = useConversation();
  return conversations.find(conv => conv.id === activeConversationId);
};

export const useCreateConversation = () => {
  const { handleAction } = useConversation();
  return useCallback((title: string) => {
    handleAction({
      type: 'create',
      conversation: {
        id: '', // Will be generated
        title,
        timestamp: '', // Will be set
      },
    });
  }, [handleAction]);
};

export const useDeleteConversation = () => {
  const { handleAction } = useConversation();
  return useCallback((id: string) => {
    handleAction({
      type: 'delete',
      conversation: { id, title: '', timestamp: '' },
    });
  }, [handleAction]);
};

export const useRenameConversation = () => {
  const { handleAction } = useConversation();
  return useCallback((id: string, newTitle: string) => {
    handleAction({
      type: 'rename',
      conversation: {
        id,
        title: newTitle,
        timestamp: new Date().toISOString(),
      },
    });
  }, [handleAction]);
};