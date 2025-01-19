import React, { useEffect, useCallback } from 'react';
import { AlertCircle, CheckCircle, Info, X, XCircle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

const icons = {
  success: <CheckCircle className="h-5 w-5 text-green-400" />,
  error: <XCircle className="h-5 w-5 text-red-400" />,
  warning: <AlertCircle className="h-5 w-5 text-yellow-400" />,
  info: <Info className="h-5 w-5 text-blue-400" />,
};

const styles = {
  success: 'bg-green-50 border-green-200 dark:bg-green-900/10 dark:border-green-900/20',
  error: 'bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-900/20',
  warning: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/10 dark:border-yellow-900/20',
  info: 'bg-blue-50 border-blue-200 dark:bg-blue-900/10 dark:border-blue-900/20',
};

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  duration = 5000,
  onClose,
}) => {
  const handleClose = useCallback(() => onClose(id), [id, onClose]);

  useEffect(() => {
    const timer = setTimeout(handleClose, duration);
    return () => clearTimeout(timer);
  }, [duration, handleClose]);

  return (
    <div
      className={`flex w-full max-w-sm items-center gap-3 rounded-lg border p-4 shadow-lg ${styles[type]} animate-fade-in`}
      role="alert"
    >
      {icons[type]}
      <p className="flex-1 text-sm font-medium">{message}</p>
      <button
        onClick={handleClose}
        className="rounded-lg p-1 hover:bg-black/5"
        aria-label="Close"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};
