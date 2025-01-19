export type UUID = string;

export interface Timestamp {
  created: string;
  updated: string;
}

export interface Metadata {
  [key: string]: any;
}

export interface Identifiable {
  id: UUID;
}

export interface BaseEntity extends Identifiable, Timestamp {
  metadata?: Metadata;
}

export interface ErrorDetails {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, any>;
}

export type ValidationResult = {
  valid: boolean;
  errors: ErrorDetails[];
};

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}

export type SortDirection = 'asc' | 'desc';

export interface SortOptions {
  field: string;
  direction: SortDirection;
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export type Theme = 'light' | 'dark' | 'system';

export interface Size {
  width: number;
  height: number;
}

export type Status = 'active' | 'inactive' | 'pending' | 'error';
