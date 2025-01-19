import { Conversation } from '../types/conversation';
import { Message } from '../types/api';
import { storageService } from './storage';

interface ExportedData {
  version: 1;
  timestamp: string;
  conversations: Array<{
    conversation: Conversation;
    messages: Message[];
  }>;
  metadata: {
    totalConversations: number;
    totalMessages: number;
    exportDate: string;
  };
}

class ConversationExporter {
  async exportConversations(conversations: Conversation[]): Promise<ExportedData> {
    const exportData: ExportedData = {
      version: 1,
      timestamp: new Date().toISOString(),
      conversations: [],
      metadata: {
        totalConversations: conversations.length,
        totalMessages: 0,
        exportDate: new Date().toISOString(),
      },
    };

    for (const conversation of conversations) {
      const messages = await storageService.loadConversationMessages(conversation.id);
      exportData.conversations.push({
        conversation,
        messages,
      });
      exportData.metadata.totalMessages += messages.length;
    }

    return exportData;
  }

  async downloadExport(conversations: Conversation[]): Promise<void> {
    try {
      const exportData = await this.exportConversations(conversations);
      const json = JSON.stringify(exportData, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const filename = `claude-chat-export-${new Date().toISOString().split('T')[0]}.json`;
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting conversations:', error);
      throw new Error('Failed to export conversations');
    }
  }

  async importConversations(file: File): Promise<ExportedData> {
    try {
      const text = await file.text();
      const data: ExportedData = JSON.parse(text);
      
      // Validate the imported data
      if (!this.isValidExportData(data)) {
        throw new Error('Invalid export file format');
      }

      // Import conversations and messages
      for (const { conversation, messages } of data.conversations) {
        await storageService.saveConversationMessages(conversation.id, messages);
      }

      return data;
    } catch (error) {
      console.error('Error importing conversations:', error);
      throw new Error('Failed to import conversations');
    }
  }

  private isValidExportData(data: any): data is ExportedData {
    return (
      data &&
      typeof data.version === 'number' &&
      Array.isArray(data.conversations) &&
      data.conversations.every((item: any) =>
        this.isValidConversationExport(item)
      )
    );
  }

  private isValidConversationExport(item: any): boolean {
    return (
      item &&
      item.conversation &&
      typeof item.conversation.id === 'string' &&
      typeof item.conversation.title === 'string' &&
      typeof item.conversation.timestamp === 'string' &&
      Array.isArray(item.messages)
    );
  }
}

export const conversationExporter = new ConversationExporter();