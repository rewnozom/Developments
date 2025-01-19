import React from 'react';
import { ResponseContainerProps } from './types';
import { ResponseContent } from './ResponseContent';

export const ResponseContainer: React.FC<ResponseContainerProps> = ({
  content,
  artifacts,
  metadata,
  className = '',
}) => {
  return (
    <div className={`rounded-lg border border-gray-200 bg-white p-4 shadow-sm ${className}`}>
      <ResponseContent
        content={content}
        artifacts={artifacts}
      />
      
      {metadata && (
        <div className="mt-4 border-t pt-2 text-sm text-gray-500">
          {metadata.tokenCount && (
            <div>Tokens: {metadata.tokenCount}</div>
          )}
          {metadata.processingTime && (
            <div>Processing Time: {metadata.processingTime.toFixed(2)}s</div>
          )}
          {metadata.modelVersion && (
            <div>Model: {metadata.modelVersion}</div>
          )}
        </div>
      )}
    </div>
  );
};
