export interface Conversation {
  id: string;
  title: string;
  timestamp: string;
  lastMessage?: string;
  isEditing?: boolean;
}

export interface ConversationAction {
  type: 'create' | 'update' | 'delete' | 'rename';
  conversation: Conversation;
}

export interface ConversationContextType {
  conversations: Conversation[];
  activeConversationId?: string;
  isLoading: boolean;
  handleAction: (action: ConversationAction) => void;
  setActiveConversation: (id: string) => void;
  clearConversations: () => void;
  importConversations: (conversations: Conversation[]) => void;
}

export interface ConversationSearchProps {
  onSearch: (query: string) => void;
  className?: string;
}

export interface ConversationActionsProps {
  conversations: Conversation[];
  onImport: (data: any) => void;
  onClearHistory: () => void;
  className?: string;
}

export interface ExportedConversation {
  conversation: Conversation;
  messages: any[];
}

export interface ImportData {
  version: number;
  conversations: ExportedConversation[];
  timestamp: string;
  metadata?: Record<string, any>;
}