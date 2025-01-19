import React from 'react';
import { CodeArtifact } from './CodeArtifact';
import { MarkdownArtifact } from './MarkdownArtifact';
import { Artifact } from '../../types/api';

interface ArtifactContainerProps {
  artifact: Artifact;
  isInteractive?: boolean;
  className?: string;
}

export const ArtifactContainer: React.FC<ArtifactContainerProps> = ({
  artifact,
  isInteractive = true,
  className = '',
}) => {
  const renderArtifact = () => {
    switch (artifact.type) {
      case 'code':
        return <CodeArtifact artifact={artifact} isInteractive={isInteractive} />;
      case 'markdown':
        return <MarkdownArtifact artifact={artifact} />;
      case 'html':
        return <div dangerouslySetInnerHTML={{ __html: artifact.content }} />;
      case 'svg':
        return <div dangerouslySetInnerHTML={{ __html: artifact.content }} className="svg-container" />;
      case 'mermaid':
        return <div className="mermaid">{artifact.content}</div>;
      case 'react':
        // Handle React components dynamically
        try {
          const Component = eval(artifact.content);
          return <Component />;
        } catch (error) {
          console.error('Failed to render React component:', error);
          return <div>Failed to render React component</div>;
        }
      default:
        return <div>Unsupported artifact type: {artifact.type}</div>;
    }
  };

  return (
    <div className={`artifact-container rounded-lg border border-gray-200 ${className}`}>
      {artifact.title && (
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-2 text-sm font-medium">
          {artifact.title}
        </div>
      )}
      <div className="p-4">
        {renderArtifact()}
      </div>
    </div>
  );
};
