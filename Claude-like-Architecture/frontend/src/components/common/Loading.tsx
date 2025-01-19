import React from 'react';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
  className?: string;
}

export const Loading: React.FC<LoadingProps> = ({
  size = 'medium',
  message = 'Loading...',
  className = '',
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-2 ${className}`}>
      <div className="relative">
        <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-500 ${sizeClasses[size]}`} />
      </div>
      {message && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {message}<span className="loading-dots" />
        </p>
      )}
    </div>
  );
};

export const FullPageLoading: React.FC<Omit<LoadingProps, 'size'>> = (props) => (
  <div className="flex h-full w-full items-center justify-center">
    <Loading size="large" {...props} />
  </div>
);
