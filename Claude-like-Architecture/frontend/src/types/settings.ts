// src/types/settings.ts
export interface Settings {
    messageHistory: number;
    autoClearContext: boolean;
    codeTheme: string;
    apiEndpoint: string;
    debugMode: boolean;
    streamingEnabled: boolean;
    maxTokens: number;
    temperature: number;
    showTokenCount: boolean;
    saveHistory: boolean;
  }