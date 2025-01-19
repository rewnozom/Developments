import React, { useState } from 'react';
import { Clipboard, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Artifact } from '../../types/api';

interface CodeArtifactProps {
  artifact: Artifact;
  isInteractive?: boolean;
  className?: string;
}

export const CodeArtifact: React.FC<CodeArtifactProps> = ({
  artifact,
  isInteractive = true,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className={`relative ${className}`}>
      {isInteractive && (
        <button
          onClick={copyToClipboard}
          className="absolute right-2 top-2 rounded-lg bg-gray-800 p-2 text-white opacity-80 hover:opacity-100"
          title="Copy code"
        >
          {copied ? <Check size={16} /> : <Clipboard size={16} />}
        </button>
      )}
      
      <SyntaxHighlighter
        language={artifact.metadata?.language || 'text'}
        style={oneDark}
        showLineNumbers={true}
        customStyle={{
          margin: 0,
          borderRadius: '0.5rem',
          fontSize: '0.9rem',
        }}
      >
        {artifact.content}
      </SyntaxHighlighter>
    </div>
  );
};
