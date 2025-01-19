import React, { useRef, useState } from 'react';
import { Download, Upload, Trash2, AlertCircle } from 'lucide-react';
import { IconWrapper } from '../common/IconWrapper';
import { conversationExporter } from '../../services/conversationExporter';
import type { Conversation } from '../../types/conversation';

interface ConversationActionsProps {
  conversations: Conversation[];
  onImport: (data: any) => void;
  onClearHistory: () => void;
  className?: string;
}

export const ConversationActions: React.FC<ConversationActionsProps> = ({
  conversations,
  onImport,
  onClearHistory,
  className = '',
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleExport = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await conversationExporter.downloadExport(conversations);
    } catch (error) {
      setError('Failed to export conversations');
      console.error('Export error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setIsLoading(true);
      setError(null);
      const importedData = await conversationExporter.importConversations(file);
      onImport(importedData);
    } catch (error) {
      setError('Failed to import conversations');
      console.error('Import error:', error);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all conversations? This cannot be undone.')) {
      onClearHistory();
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-400/10 p-3 text-sm text-red-400">
          <IconWrapper icon={AlertCircle} className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="flex flex-col gap-2">
        <button
          onClick={handleExport}
          disabled={isLoading || conversations.length === 0}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-left transition-colors
            ${isLoading || conversations.length === 0
              ? 'cursor-not-allowed bg-[rgba(82,82,82,0.3)] text-[#a3a3a3]'
              : 'bg-[rgba(82,82,82,0.15)] text-[#e5e5e5] hover:bg-[rgba(82,82,82,0.3)]'
            }`}
        >
          <IconWrapper icon={Download} className="h-4 w-4 shrink-0" />
          Export Conversations
        </button>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-left transition-colors
            ${isLoading
              ? 'cursor-not-allowed bg-[rgba(82,82,82,0.3)] text-[#a3a3a3]'
              : 'bg-[rgba(82,82,82,0.15)] text-[#e5e5e5] hover:bg-[rgba(82,82,82,0.3)]'
            }`}
        >
          <IconWrapper icon={Upload} className="h-4 w-4 shrink-0" />
          Import Conversations
        </button>

        <button
          onClick={handleClearHistory}
          disabled={isLoading || conversations.length === 0}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-left transition-colors
            ${isLoading || conversations.length === 0
              ? 'cursor-not-allowed bg-[rgba(82,82,82,0.3)] text-[#a3a3a3]'
              : 'bg-red-400/10 text-red-400 hover:bg-red-400/20'
            }`}
        >
          <IconWrapper icon={Trash2} className="h-4 w-4 shrink-0" />
          Clear All Conversations
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleImport}
          className="hidden"
        />
      </div>
    </div>
  );
};