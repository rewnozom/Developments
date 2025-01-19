import axios, { AxiosInstance } from 'axios';
import { API_CONFIG, MODEL_CONFIG, ERROR_MESSAGES } from '../config/apiConfig';
import type { Message, ChatResponse, ChatConfig, ApiError, Artifact } from '../types/api';

class ClaudeApi {
  private api: AxiosInstance;
  private retryCount: number = 0;

  constructor() {
    this.api = axios.create({
      baseURL: API_CONFIG.baseUrl,
      timeout: API_CONFIG.timeout,
      headers: API_CONFIG.defaultHeaders,
    });

    this.api.interceptors.response.use(
      (response) => response,
      this.handleApiError.bind(this)
    );
  }

  private async handleApiError(error: any): Promise<never> {
    if (error.response) {
      const apiError: ApiError = {
        code: error.response.data.code || 'unknown_error',
        message: error.response.data.message || ERROR_MESSAGES.requestFailed,
        details: error.response.data.details || {},
      };
      throw apiError;
    }

    if (error.request && this.retryCount < API_CONFIG.retryAttempts) {
      this.retryCount++;
      await new Promise(resolve => setTimeout(resolve, API_CONFIG.retryDelay));
      return this.api.request(error.config);
    }

    throw {
      code: 'network_error',
      message: ERROR_MESSAGES.connectionFailed,
      details: {},
    } as ApiError;
  }

  public async sendMessage(
    messages: Message[],
    config?: ChatConfig
  ): Promise<ChatResponse> {
    const requestConfig = {
      ...MODEL_CONFIG,
      ...config,
    };

    try {
      const response = await this.api.post<ChatResponse>(API_CONFIG.endpoints.chat, {
        messages,
        config: requestConfig,
      });

      return response.data;
    } finally {
      this.retryCount = 0;
    }
  }

  public async getArtifact(artifactId: string): Promise<Artifact> {
    const response = await this.api.get<Artifact>(
      `${API_CONFIG.endpoints.artifacts}/${artifactId}`
    );
    return response.data;
  }

  public async getModels(): Promise<string[]> {
    const response = await this.api.get<string[]>(API_CONFIG.endpoints.models);
    return response.data;
  }
}

export const claudeApi = new ClaudeApi();
