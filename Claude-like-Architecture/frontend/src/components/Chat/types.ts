// src/components/Chat/types.ts
import { Message, Artifact } from '../../types/api';

export interface ChatContainerProps {
  className?: string;
  initialMessages?: Message[];
}

export interface ChatMessageProps {
  message: Message;
  artifacts?: Artifact[];
  isLast?: boolean;
  className?: string;
}

export interface ChatInputProps {
  onSend: (message: string) => Promise<any>;
  isLoading?: boolean;
  isDisabled?: boolean;
  conversationId?: string;
  placeholder?: string;
  className?: string;
}

export interface ChatState {
  messages: Message[];
  artifacts: Record<string, Artifact[]>;
  isLoading: boolean;
  error: string | null;
}