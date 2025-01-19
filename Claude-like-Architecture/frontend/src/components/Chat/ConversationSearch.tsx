import React, { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { IconWrapper } from '../common/IconWrapper';

interface ConversationSearchProps {
  onSearch: (query: string) => void;
  className?: string;
}

export const ConversationSearch: React.FC<ConversationSearchProps> = ({
  onSearch,
  className = '',
}) => {
  const [query, setQuery] = useState('');

  // Debounce search
  useEffect(() => {
    const debounceTimeout = setTimeout(() => {
      onSearch(query);
    }, 300);

    return () => clearTimeout(debounceTimeout);
  }, [query, onSearch]);

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search conversations..."
          className="w-full rounded-lg border border-[rgba(82,82,82,0.3)] bg-[#1a1a1a] 
            py-2 pl-9 pr-8 text-[#e5e5e5] placeholder:text-[#a3a3a3]
            focus:border-[#fb923c] focus:outline-none"
        />
        <IconWrapper
          icon={Search}
          className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#a3a3a3]"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full 
              p-1 text-[#a3a3a3] hover:bg-[rgba(82,82,82,0.3)]"
          >
            <IconWrapper icon={X} className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};