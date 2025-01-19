import { useState, useCallback, useMemo } from 'react';
import type { Conversation } from '../types/conversation';

export function useSearch(conversations: Conversation[]) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) {
      return conversations;
    }

    const query = searchQuery.toLowerCase();
    return conversations.filter(conversation =>
      conversation.title.toLowerCase().includes(query)
    );
  }, [conversations, searchQuery]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  return {
    searchQuery,
    filteredConversations,
    handleSearch,
  };
}