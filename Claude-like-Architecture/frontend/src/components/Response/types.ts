import { Artifact } from '../../types/api';

export interface ResponseContentProps {
  content: string;
  artifacts?: Artifact[];
  isLast?: boolean;
  className?: string;
}

export interface ResponseContainerProps {
  content: string;
  artifacts?: Artifact[];
  metadata?: Record<string, any>;
  className?: string;
}

export interface ArtifactDisplayProps {
  artifact: Artifact;
  className?: string;
}
