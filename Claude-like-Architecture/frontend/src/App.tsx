import React, { useEffect, useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { ConversationProvider } from './contexts/ConversationContext';
import { StreamingProvider } from './providers/StreamingProvider';
import { ChatProvider } from './providers/ChatProvider';
import { ChatContainer } from './components/Chat/ChatContainer';
import { validateBackendConfig } from './config/apiConfig';
import { colors } from './constants/theme';
import { API_CONFIG } from './config/apiConfig';

const App: React.FC = () => {
  const [isBackendAvailable, setIsBackendAvailable] = useState(true);

  useEffect(() => {
    const checkBackend = async () => {
      const isAvailable = await validateBackendConfig();
      setIsBackendAvailable(isAvailable);
    };
    void checkBackend();
  }, []);

  if (!isBackendAvailable) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-[#1a1a1a] p-4 text-center">
        <div className="rounded-lg bg-red-500/10 p-6 text-red-400">
          <h2 className="mb-2 text-lg font-semibold">Backend Connection Error</h2>
          <p className="mb-4">Unable to connect to the backend server at {API_CONFIG.baseUrl}.</p>
          <p>Please verify that:</p>
          <ul className="mt-2 list-disc text-left">
            <li>The backend server is running</li>
            <li>The VITE_API_BASE_URL environment variable is set correctly</li>
            <li>Your network connection is working</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <SettingsProvider>
        <ConversationProvider>
          <StreamingProvider>
            <ChatProvider>
              <div className="flex h-screen flex-col bg-[rgba(43,41,41,0.85)]">
                {/* Header with glass effect */}
                <header className="relative z-10 border-b border-[rgba(82,82,82,0.3)] bg-[rgba(26,26,26,0.9)] 
                  p-4 shadow-lg backdrop-blur-md">
                  <div className="flex items-center justify-between">
                    <h1 className="text-xl font-semibold text-[rgb(209,204,204)]">
                      Claude Chat
                    </h1>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[#a3a3a3]">
                        Model: {API_CONFIG.model}
                      </span>
                      <div className="h-2 w-2 rounded-full bg-[#fb923c]" />
                      <span className="text-xs text-[#a3a3a3]">
                        {isBackendAvailable ? 'Connected' : 'Disconnected'}
                      </span>
                    </div>
                  </div>
                </header>
                
                {/* Main content */}
                <main className="relative flex-1 overflow-hidden bg-[#1a1a1a] p-4">
                  <div className="relative mx-auto h-full max-w-6xl rounded-lg border border-[rgba(82,82,82,0.3)] 
                    bg-[#262626] shadow-lg backdrop-blur-sm">
                    <ChatContainer />
                  </div>

                  {/* Background gradient effect */}
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-b 
                    from-[rgba(43,41,41,0)] via-[rgba(43,41,41,0.1)] to-[rgba(43,41,41,0.2)]" />
                </main>
              </div>
            </ChatProvider>
          </StreamingProvider>
        </ConversationProvider>
      </SettingsProvider>
    </ThemeProvider>
  );
};

export default App;