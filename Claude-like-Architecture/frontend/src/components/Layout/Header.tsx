import React from 'react';
import { Settings, Sun, Moon, Menu } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';

interface HeaderProps {
  onOpenSettings: () => void;
  onToggleSidebar: () => void;
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenSettings,
  onToggleSidebar,
  className = '',
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className={`border-b bg-white px-4 py-3 dark:bg-gray-800 dark:border-gray-700 ${className}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <h1 className="text-xl font-semibold">Claude 3.5 Sonnet</h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </button>

          <button
            onClick={onOpenSettings}
            className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Open settings"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
