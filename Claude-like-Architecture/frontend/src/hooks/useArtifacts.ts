// src/hooks/useArtifacts.ts
import { useState, useCallback } from 'react';
import type { Artifact } from '../types/api';

interface ArtifactsState {
  artifacts: Record<string, Artifact[]>;
  activeArtifact: Artifact | null;
  isLoading: boolean;
  error: string | null;
}

export function useArtifacts() {
  const [state, setState] = useState<ArtifactsState>({
    artifacts: {},
    activeArtifact: null,
    isLoading: false,
    error: null
  });

  const addArtifacts = useCallback((messageId: string, newArtifacts: Artifact[]) => {
    setState(prev => ({
      ...prev,
      artifacts: {
        ...prev.artifacts,
        [messageId]: newArtifacts,
      }
    }));
  }, []);

  const removeArtifacts = useCallback((messageId: string) => {
    setState(prev => {
      const { [messageId]: removed, ...rest } = prev.artifacts;
      return {
        ...prev,
        artifacts: rest,
      };
    });
  }, []);

  const clearArtifacts = useCallback(() => {
    setState(prev => ({
      ...prev,
      artifacts: {},
      activeArtifact: null,
    }));
  }, []);

  const selectArtifact = useCallback((artifact: Artifact | null) => {
    setState(prev => ({
      ...prev,
      activeArtifact: artifact,
    }));
  }, []);

  const getArtifactsForMessage = useCallback((messageId: string): Artifact[] => {
    return state.artifacts[messageId] || [];
  }, [state.artifacts]);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({
      ...prev,
      error,
    }));
  }, []);

  const setLoading = useCallback((isLoading: boolean) => {
    setState(prev => ({
      ...prev,
      isLoading,
    }));
  }, []);

  return {
    artifacts: state.artifacts,
    activeArtifact: state.activeArtifact,
    isLoading: state.isLoading,
    error: state.error,
    addArtifacts,
    removeArtifacts,
    clearArtifacts,
    selectArtifact,
    getArtifactsForMessage,
    setError,
    setLoading,
  };
}