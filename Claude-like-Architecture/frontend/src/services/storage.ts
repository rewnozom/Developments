import { Conversation } from '../types/conversation';

const STORAGE_KEYS = {
  CONVERSATIONS: 'claude_conversations',
  ACTIVE_CONVERSATION: 'claude_active_conversation',
  CHAT_MESSAGES: 'claude_chat_messages_',
} as const;

interface StorageData {
  conversations: Conversation[];
  activeConversationId?: string;
  version: number;
  lastUpdated: string;
}

class StorageService {
  private getStorageData(): StorageData {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      if (data) {
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Error reading from localStorage:', error);
    }
    
    return {
      conversations: [],
      version: 1,
      lastUpdated: new Date().toISOString(),
    };
  }

  private setStorageData(data: StorageData): void {
    try {
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify({
        ...data,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  }

  loadConversations(): { conversations: Conversation[]; activeConversationId?: string } {
    const data = this.getStorageData();
    return {
      conversations: data.conversations,
      activeConversationId: data.activeConversationId,
    };
  }

  saveConversations(conversations: Conversation[], activeConversationId?: string): void {
    const data = this.getStorageData();
    this.setStorageData({
      ...data,
      conversations,
      activeConversationId,
    });
  }

  saveConversationMessages(conversationId: string, messages: any[]): void {
    try {
      localStorage.setItem(
        `${STORAGE_KEYS.CHAT_MESSAGES}${conversationId}`,
        JSON.stringify(messages)
      );
    } catch (error) {
      console.error('Error saving messages:', error);
    }
  }

  loadConversationMessages(conversationId: string): any[] {
    try {
      const messages = localStorage.getItem(
        `${STORAGE_KEYS.CHAT_MESSAGES}${conversationId}`
      );
      return messages ? JSON.parse(messages) : [];
    } catch (error) {
      console.error('Error loading messages:', error);
      return [];
    }
  }

  clearAll(): void {
    try {
      // Clear main conversation data
      localStorage.removeItem(STORAGE_KEYS.CONVERSATIONS);
      localStorage.removeItem(STORAGE_KEYS.ACTIVE_CONVERSATION);

      // Clear all message data
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(STORAGE_KEYS.CHAT_MESSAGES)) {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.error('Error clearing storage:', error);
    }
  }
}

export const storageService = new StorageService();