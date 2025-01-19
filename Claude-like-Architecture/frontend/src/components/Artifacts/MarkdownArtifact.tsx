import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Artifact } from '../../types/api';

interface MarkdownArtifactProps {
  artifact: Artifact;
  className?: string;
}

export const MarkdownArtifact: React.FC<MarkdownArtifactProps> = ({
  artifact,
  className = '',
}) => {
  return (
    <div className={`prose max-w-none dark:prose-invert ${className}`}>
      <ReactMarkdown>{artifact.content}</ReactMarkdown>
    </div>
  );
};
