import { Message, ChatConfig } from '../types/api';

// Token räknare baserad på Claude's tokeniseringsregler
export const estimateTokens = (text: string): number => {
  // Enkel uppskattning: ~4 tecken per token i genomsnitt
  return Math.ceil(text.length / 4);
};

// Truncera meddelanden för att passa inom token-gränsen
export const truncateMessages = (
  messages: Message[],
  maxTokens: number = 8192
): Message[] => {
  const reversedMessages = [...messages].reverse();
  const truncatedMessages: Message[] = [];
  let totalTokens = 0;

  for (const message of reversedMessages) {
    const messageTokens = estimateTokens(message.content);
    if (totalTokens + messageTokens <= maxTokens) {
      truncatedMessages.unshift(message);
      totalTokens += messageTokens;
    } else {
      break;
    }
  }

  return truncatedMessages;
};

// Formatera system prompts
export const formatSystemPrompt = (prompt: string, config: Partial<ChatConfig> = {}): string => {
  const { temperature = 0.7, topP = 0.9 } = config;
  return `${prompt}\n\nParameters: temperature=${temperature}, top_p=${topP}`;
};

// Parse Claude's svar för att extrahera metadata
export const parseClaudeResponse = (response: string) => {
  const metadataRegex = /\[metadata:\s*({[^}]+})\]/;
  const match = response.match(metadataRegex);
  
  if (match) {
    try {
      const metadata = JSON.parse(match[1]);
      const cleanResponse = response.replace(metadataRegex, '').trim();
      return { response: cleanResponse, metadata };
    } catch (e) {
      console.warn('Failed to parse metadata from Claude response');
    }
  }
  
  return { response, metadata: {} };
};

// Kontrollera om innehåll är säkert enligt Claude's riktlinjer
export const validateContent = (content: string): boolean => {
  const unsafePatterns = [
    /<%[^%>]*%>/,  // Embedded code
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, // Script tags
    /javascript:/gi, // JavaScript protocol
    /data:/gi,  // Data URLs
  ];

  return !unsafePatterns.some(pattern => pattern.test(content));
};

// Format settings for different use cases
export const CLAUDE_FORMATS = {
  CONCISE: {
    temperature: 0.3,
    topP: 0.8,
    systemPrompt: 'Please provide concise, direct responses.',
  },
  CREATIVE: {
    temperature: 0.9,
    topP: 0.95,
    systemPrompt: 'Feel free to be creative and exploratory in your responses.',
  },
  TECHNICAL: {
    temperature: 0.2,
    topP: 0.8,
    systemPrompt: 'Please provide technical, precise responses with examples where appropriate.',
  },
  ANALYTICAL: {
    temperature: 0.4,
    topP: 0.85,
    systemPrompt: 'Please analyze the problem thoroughly and provide structured responses.',
  },
};

// Utility för att hantera Claude's specialkommandon
export const parseClaudeCommands = (input: string) => {
  const commands: Record<string, string> = {};
  const commandRegex = /\/(\w+)\s+([^\/]+)/g;
  let match;

  while ((match = commandRegex.exec(input)) !== null) {
    commands[match[1]] = match[2].trim();
  }

  const cleanInput = input.replace(commandRegex, '').trim();
  return { commands, cleanInput };
};

// Rate limiting utilities
export const createRateLimiter = (maxRequests: number, timeWindow: number) => {
  const requests: number[] = [];
  
  return {
    canMakeRequest: () => {
      const now = Date.now();
      requests.push(now);
      
      // Remove old requests
      while (requests.length > 0 && requests[0] < now - timeWindow) {
        requests.shift();
      }
      
      return requests.length <= maxRequests;
    },
    
    getTimeUntilNext: () => {
      if (requests.length < maxRequests) return 0;
      return requests[0] + timeWindow - Date.now();
    }
  };
};
