import React from 'react';
import ReactMarkdown from 'react-markdown';
import { ResponseContentProps } from './types';
import { ArtifactContainer } from '../Artifacts/ArtifactContainer';

export const ResponseContent: React.FC<ResponseContentProps> = ({
  content,
  artifacts,
  isLast = false,
  className = '',
}) => {
  return (
    <div className={`response-content ${className}`}>
      <div className="prose max-w-none dark:prose-invert">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
      
      {artifacts && artifacts.length > 0 && (
        <div className="mt-4 space-y-4">
          {artifacts.map((artifact) => (
            <ArtifactContainer
              key={artifact.id}
              artifact={artifact}
              isInteractive={isLast}
            />
          ))}
        </div>
      )}
    </div>
  );
};
