import React from 'react';
import { Modal } from '../common/Modal/Modal';
import { ThemeSelector } from './ThemeSelector';
import { Settings } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = React.useState<'general' | 'appearance' | 'advanced'>('general');

  const tabs = [
    { id: 'general', label: 'General' },
    { id: 'appearance', label: 'Appearance' },
    { id: 'advanced', label: 'Advanced' },
  ] as const;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Settings"
      size="large"
    >
      <div className="flex flex-col gap-6">
        {/* Tabs */}
        <div className="flex border-b dark:border-gray-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-500'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'general' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Message History</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Control how many messages are retained
                  </p>
                </div>
                <input
                  type="number"
                  className="w-24 rounded-lg border px-3 py-1"
                  min={10}
                  max={100}
                  defaultValue={50}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Auto-clear Context</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Clear conversation context periodically
                  </p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" className="peer sr-only" />
                  <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none dark:bg-gray-700"></div>
                </label>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-4">
              <ThemeSelector />

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Code Theme</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Select syntax highlighting theme
                  </p>
                </div>
                <select className="rounded-lg border px-3 py-1">
                  <option value="github">GitHub</option>
                  <option value="dracula">Dracula</option>
                  <option value="monokai">Monokai</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">API Endpoint</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Custom API endpoint URL
                  </p>
                </div>
                <input
                  type="text"
                  className="w-64 rounded-lg border px-3 py-1"
                  placeholder="https://api.example.com"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Debug Mode</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Enable detailed logging
                  </p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" className="peer sr-only" />
                  <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none dark:bg-gray-700"></div>
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
