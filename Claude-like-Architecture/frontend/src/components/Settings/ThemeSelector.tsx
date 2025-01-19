import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import type { Theme } from '@/utils/theme';

export const ThemeSelector: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const themes: Array<{
    value: Theme;
    label: string;
    icon: React.ReactNode;
    description: string;
  }> = [
    {
      value: 'light',
      label: 'Light',
      icon: <Sun className="h-5 w-5" />,
      description: 'Light theme for daytime use',
    },
    {
      value: 'dark',
      label: 'Dark',
      icon: <Moon className="h-5 w-5" />,
      description: 'Dark theme for nighttime use',
    },
    {
      value: 'system',
      label: 'System',
      icon: <Monitor className="h-5 w-5" />,
      description: 'Follow system theme preference',
    },
  ];

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-medium">Theme</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Select your preferred theme appearance
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {themes.map(({ value, label, icon, description }) => (
          <button
            key={value}
            onClick={() => setTheme(value)}
            className={`flex flex-col items-center rounded-lg border p-3 text-center transition-colors ${
              theme === value
                ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/20'
                : 'border-gray-200 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
            }`}
          >
            <div
              className={`mb-2 rounded-full p-2 ${
                theme === value
                  ? 'bg-blue-100 text-blue-500 dark:bg-blue-900/40 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
              }`}
            >
              {icon}
            </div>
            <div className="text-sm font-medium">{label}</div>
            <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {description}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
