import React, { useState } from 'react';
import { 
  PlusCircle, 
  History, 
  Trash2, 
  Edit2, 
  Check, 
  ChevronRight,
  ChevronLeft,
  Settings
} from 'lucide-react';
import { IconWrapper } from '../common/IconWrapper';
import { ConversationSearch } from '../Chat/ConversationSearch';
import { useSearch } from '../../hooks/useSearch';
import type { Conversation } from '../../types/conversation';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onClearHistory: () => void;
  conversations: Conversation[];
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onRenameConversation: (id: string, newTitle: string) => void;
  onDeleteConversation: (id: string) => void;
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  onNewChat,
  onClearHistory,
  conversations,
  activeConversationId,
  onSelectConversation,
  onRenameConversation,
  onDeleteConversation,
  className = '',
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState('');
  const { filteredConversations, handleSearch } = useSearch(conversations);

  const handleStartEdit = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setNewTitle(conversation.title);
  };

  const handleSaveEdit = (id: string) => {
    if (newTitle.trim()) {
      onRenameConversation(id, newTitle.trim());
    }
    setEditingId(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent, id: string) => {
    if (e.key === 'Enter') {
      handleSaveEdit(id);
    } else if (e.key === 'Escape') {
      setEditingId(null);
    }
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          flex flex-col bg-[rgba(43,41,41,0.85)] backdrop-blur-md border-r border-[rgba(82,82,82,0.3)]
          ${className}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[rgba(82,82,82,0.3)]">
          <h2 className="text-lg font-semibold text-[#e5e5e5]">Conversations</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-[rgba(82,82,82,0.3)] text-[#a3a3a3] hover:text-[#e5e5e5] transition-colors"
              aria-label="Close sidebar"
            >
              <IconWrapper icon={isOpen ? ChevronLeft : ChevronRight} className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 p-4">
          <button
            onClick={onNewChat}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#fb923c] hover:bg-[#f97316] 
              text-white transition-colors duration-200"
          >
            <IconWrapper icon={PlusCircle} className="h-5 w-5" />
            New Chat
          </button>

          {/* Search */}
          <ConversationSearch onSearch={handleSearch} className="mt-2" />
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-2">
          <div className="space-y-1 py-2">
            {filteredConversations.map((conv: Conversation) => (
              <div
                key={conv.id}
                className={`group relative rounded-lg transition-colors duration-200
                  ${conv.id === activeConversationId
                    ? 'bg-[rgba(82,82,82,0.3)]'
                    : 'hover:bg-[rgba(82,82,82,0.15)]'
                  }`}
              >
                <button
                  onClick={() => onSelectConversation(conv.id)}
                  className="w-full px-4 py-3 text-left"
                >
                  <div className="flex items-start gap-3">
                    <IconWrapper icon={History} className="h-5 w-5 shrink-0 mt-1 text-[#a3a3a3]" />
                    <div className="flex-1 overflow-hidden">
                      {editingId === conv.id ? (
                        <input
                          type="text"
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          onKeyDown={(e) => handleKeyPress(e, conv.id)}
                          className="w-full bg-[#262626] text-[#e5e5e5] px-2 py-1 rounded border 
                            border-[rgba(82,82,82,0.3)] focus:outline-none focus:border-[#fb923c]"
                          autoFocus
                        />
                      ) : (
                        <>
                          <div className="text-sm font-medium text-[#e5e5e5] truncate">
                            {conv.title}
                          </div>
                          <div className="text-xs text-[#a3a3a3]">
                            {new Date(conv.timestamp).toLocaleDateString()}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </button>

                {/* Action buttons */}
                <div className={`absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1
                  ${editingId === conv.id ? 'visible' : 'invisible group-hover:visible'}`}>
                  {editingId === conv.id ? (
                    <button
                      onClick={() => handleSaveEdit(conv.id)}
                      className="p-1 rounded hover:bg-[rgba(82,82,82,0.3)] text-[#fb923c]"
                    >
                      <IconWrapper icon={Check} className="h-4 w-4" />
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartEdit(conv);
                      }}
                      className="p-1 rounded hover:bg-[rgba(82,82,82,0.3)] text-[#a3a3a3] 
                        hover:text-[#fb923c]"
                    >
                      <IconWrapper icon={Edit2} className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conv.id);
                    }}
                    className="p-1 rounded hover:bg-[rgba(82,82,82,0.3)] text-[#a3a3a3] 
                      hover:text-[#fb923c]"
                  >
                    <IconWrapper icon={Trash2} className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};