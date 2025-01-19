import { z } from 'zod';

export const messageSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(['user', 'assistant']),
  content: z.string().min(1),
  timestamp: z.string().datetime(),
  metadata: z.record(z.any()).optional(),
});

export const artifactSchema = z.object({
  id: z.string().uuid(),
  type: z.enum(['code', 'markdown', 'html', 'svg', 'mermaid', 'react']),
  content: z.string(),
  title: z.string(),
  metadata: z.record(z.any()).optional(),
});

export function validateMessage(message: unknown) {
  return messageSchema.safeParse(message);
}

export function validateArtifact(artifact: unknown) {
  return artifactSchema.safeParse(artifact);
}

export function validateContentLength(content: string, maxLength: number = 4000) {
  if (content.length > maxLength) {
    throw new Error(`Content exceeds maximum length of ${maxLength} characters`);
  }
}

export function validateFileUpload(file: File) {
  const maxSize = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE) || 10485760; // 10MB default
  const allowedTypes = ['text/plain', 'text/markdown', 'application/json'];

  if (file.size > maxSize) {
    throw new Error(`File size exceeds maximum limit of ${maxSize / 1024 / 1024}MB`);
  }

  if (!allowedTypes.includes(file.type)) {
    throw new Error('File type not supported');
  }
}
