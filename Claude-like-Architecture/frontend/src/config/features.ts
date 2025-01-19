// Type for environment configuration
type FeatureEnvironment = 'development' | 'staging' | 'production';

interface FeatureFlag {
  enabled: boolean;
  description: string;
  requiresAuth?: boolean;
  beta?: boolean;
  environment?: FeatureEnvironment[]; // Which environments this feature is available in
  rolloutPercentage?: number; // For gradual feature rollout
  dependencies?: string[]; // Other features this depends on
}

// Add user identifier utility
const getUserIdentifier = (): string => {
  // This should be implemented based on your user identification strategy
  // For example, you could use a session ID, user ID, or other unique identifier
  return localStorage.getItem('userId') || 'anonymous';
};

export const FEATURES: Record<string, FeatureFlag> = {
  streaming: {
    enabled: true,
    description: 'Enable streaming responses from Claude',
    beta: true,
    environment: ['development', 'staging'],
    rolloutPercentage: 100,
  },
  
  codeHighlighting: {
    enabled: true,
    description: 'Syntax highlighting for code blocks',
    environment: ['development', 'staging', 'production'],
  },
  
  darkMode: {
    enabled: true,
    description: 'Toggle between light and dark theme',
    environment: ['development', 'staging', 'production'],
  },
  
  messageHistory: {
    enabled: true,
    description: 'Store and display message history',
    environment: ['development', 'staging', 'production'],
    dependencies: ['contextRetention'],
  },
  
  fileUploads: {
    enabled: false,
    description: 'Upload and process files',
    beta: true,
    environment: ['development', 'staging'],
    requiresAuth: true,
  },
  
  contextRetention: {
    enabled: true,
    description: 'Retain conversation context across sessions',
    environment: ['development', 'staging', 'production'],
  },
  
  customPrompts: {
    enabled: true,
    description: 'Save and use custom prompts',
    requiresAuth: true,
    environment: ['development', 'staging', 'production'],
  },
  
  exportChat: {
    enabled: true,
    description: 'Export conversation history',
    environment: ['development', 'staging', 'production'],
    dependencies: ['messageHistory'],
  },
  
  markdownSupport: {
    enabled: true,
    description: 'Render markdown in messages',
    environment: ['development', 'staging', 'production'],
  },
  
  codeExecution: {
    enabled: false,
    description: 'Execute code snippets',
    beta: true,
    requiresAuth: true,
    environment: ['development'],
    rolloutPercentage: 20,
  },
};

// Enhanced feature checking with environment and dependency validation
export const isFeatureEnabled = (
  featureName: keyof typeof FEATURES,
  environment: FeatureEnvironment = 'production'
): boolean => {
  const feature = FEATURES[featureName];
  if (!feature) return false;

  // Check environment-specific overrides
  const envOverride = process.env[`VITE_FEATURE_${featureName.toUpperCase()}`];
  if (envOverride !== undefined) {
    return envOverride === 'true';
  }

  // Check if feature is enabled for current environment
  if (feature.environment && !feature.environment.includes(environment)) {
    return false;
  }

  // Check dependencies
  if (feature.dependencies) {
    const hasDependencies = feature.dependencies.every(dep => 
      isFeatureEnabled(dep as keyof typeof FEATURES, environment)
    );
    if (!hasDependencies) return false;
  }

  // Check rollout percentage if defined
  if (typeof feature.rolloutPercentage === 'number') {
    const userIdentifier = getUserIdentifier();
    const shouldEnableForUser = checkRolloutEligibility(
      userIdentifier,
      feature.rolloutPercentage
    );
    if (!shouldEnableForUser) return false;
  }

  return feature.enabled;
};

// Helper function to check rollout eligibility
const checkRolloutEligibility = (userIdentifier: string, percentage: number): boolean => {
  // Simple hash function for demonstration
  const hash = userIdentifier.split('').reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc);
  }, 0);
  
  return (Math.abs(hash) % 100) < percentage;
};

export const getBetaFeatures = () => {
  return Object.entries(FEATURES)
    .filter(([_, feature]) => feature.beta)
    .reduce((acc, [key, feature]) => ({
      ...acc,
      [key]: feature,
    }), {} as Record<string, FeatureFlag>);
};

export const getAuthRequiredFeatures = () => {
  return Object.entries(FEATURES)
    .filter(([_, feature]) => feature.requiresAuth)
    .reduce((acc, [key, feature]) => ({
      ...acc,
      [key]: feature,
    }), {} as Record<string, FeatureFlag>);
};

export const getFeaturesByEnvironment = (env: FeatureEnvironment) => {
  return Object.entries(FEATURES)
    .filter(([_, feature]) => feature.environment?.includes(env))
    .reduce((acc, [key, feature]) => ({
      ...acc,
      [key]: feature,
    }), {} as Record<string, FeatureFlag>);
};

export interface FeatureConfig {
  maxTokens: number;
  streamingEnabled: boolean;
  contextWindow: number;
  customPrompts: string[];
  environment: FeatureEnvironment;
}

export const DEFAULT_FEATURE_CONFIG: FeatureConfig = {
  maxTokens: 8192,
  streamingEnabled: true,
  contextWindow: 10,
  customPrompts: [],
  environment: 'production',
};

export const validateFeatureConfig = (config: Partial<FeatureConfig>): FeatureConfig => {
  const validatedConfig = {
    ...DEFAULT_FEATURE_CONFIG,
    ...config,
  };

  return {
    ...validatedConfig,
    maxTokens: Math.min(validatedConfig.maxTokens, 8192),
    contextWindow: Math.min(validatedConfig.contextWindow, 50),
  };
};

export default FEATURES;