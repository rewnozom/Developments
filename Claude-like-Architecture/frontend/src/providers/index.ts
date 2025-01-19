import { AIProvider, ProviderConfig } from './types';
import { GroqProvider } from './groq';
import { LocalAIProvider } from './local-ai';

export type ProviderType = 'groq' | 'local-ai' | 'claude';

export const createProvider = async (
  type: ProviderType,
  config: ProviderConfig
): Promise<AIProvider> => {
  let provider: AIProvider;

  switch (type) {
    case 'groq':
      provider = new GroqProvider();
      break;
    case 'local-ai':
      provider = new LocalAIProvider();
      break;
    case 'claude':
      provider = new ClaudeProvider();
      break;
    default:
      throw new Error(`Unknown provider type: ${type}`);
  }

  await provider.initialize(config);
  return provider;
};

export * from './types';