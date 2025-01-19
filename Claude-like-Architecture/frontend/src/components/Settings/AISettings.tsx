import React from 'react';
import { useSettings } from '../../contexts/SettingsContext';

export const AISettings: React.FC = () => {
  const { settings, updateSettings } = useSettings();

  const providers = [
    { value: 'claude', label: 'Claude 3.5 Sonnet' },
    { value: 'groq', label: 'Groq AI' },
    { value: 'local-ai', label: 'Local AI (LM Studio)' },
  ];

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium">AI Provider</label>
        <select
          value={settings.aiProvider}
          onChange={(e) => updateSettings({ aiProvider: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        >
          {providers.map(({ value, label }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium">Model</label>
        <input
          type="text"
          value={settings.aiModel}
          onChange={(e) => updateSettings({ aiModel: e.target.value })}
          placeholder="Enter model name"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium">API Base URL</label>
        <input
          type="text"
          value={settings.aiBaseUrl}
          onChange={(e) => updateSettings({ aiBaseUrl: e.target.value })}
          placeholder="Enter API base URL"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>
    </div>
  );
};