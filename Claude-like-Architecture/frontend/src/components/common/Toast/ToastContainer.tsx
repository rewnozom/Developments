import React from 'react';
import { Toast, ToastType } from './Toast';
import { createRoot } from 'react-dom/client';

interface ToastOptions {
  type: ToastType;
  message: string;
  duration?: number;
}

class ToastManager {
  private containerRef: HTMLDivElement | null = null;
  private toasts: Map<string, { element: JSX.Element }> = new Map();

  private createContainer() {
    const container = document.createElement('div');
    container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
    document.body.appendChild(container);
    this.containerRef = container;
  }

  public show({ type, message, duration }: ToastOptions) {
    if (!this.containerRef) {
      this.createContainer();
    }

    const id = Math.random().toString(36).substr(2, 9);
    
    const removeToast = (toastId: string) => {
      const toast = this.toasts.get(toastId);
      if (toast && this.containerRef) {
        this.toasts.delete(toastId);
        this.render();
      }
    };

    const toast = (
      <Toast
        key={id}
        id={id}
        type={type}
        message={message}
        duration={duration}
        onClose={removeToast}
      />
    );

    this.toasts.set(id, { element: toast });
    this.render();

    return id;
  }

  private render() {
    if (this.containerRef) {
      const root = createRoot(this.containerRef);
      root.render(
        <React.Fragment>
          {Array.from(this.toasts.values()).map(({ element }) => element)}
        </React.Fragment>
      );
    }
  }
}

export const toastManager = new ToastManager();
