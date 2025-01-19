export class Storage {
  private prefix: string;

  constructor(prefix: string = 'claude_') {
    this.prefix = prefix;
  }

  private getKey(key: string): string {
    return `${this.prefix}${key}`;
  }

  set<T>(key: string, value: T, ttl?: number): void {
    const item = {
      value,
      timestamp: Date.now(),
      expiry: ttl ? Date.now() + ttl * 1000 : null,
    };

    try {
      localStorage.setItem(this.getKey(key), JSON.stringify(item));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      this.cleanup();
    }
  }

  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(this.getKey(key));
      if (!item) return null;

      const { value, expiry } = JSON.parse(item);

      if (expiry && Date.now() > expiry) {
        this.remove(key);
        return null;
      }

      return value as T;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  }

  remove(key: string): void {
    localStorage.removeItem(this.getKey(key));
  }

  clear(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }

  cleanup(): void {
    const keys = Object.keys(localStorage);
    let totalSize = 0;
    const items: { key: string; size: number }[] = [];

    // Calculate sizes and collect expired items
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        const item = localStorage.getItem(key);
        if (item) {
          const size = new Blob([item]).size;
          totalSize += size;
          items.push({ key, size });
        }
      }
    });

    // If we're using more than 4MB (arbitrary limit), remove oldest items
    if (totalSize > 4 * 1024 * 1024) {
      items.sort((a, b) => {
        const aItem = localStorage.getItem(a.key);
        const bItem = localStorage.getItem(b.key);
        if (!aItem || !bItem) return 0;
        return JSON.parse(aItem).timestamp - JSON.parse(bItem).timestamp;
      });

      while (totalSize > 3 * 1024 * 1024 && items.length) {
        const item = items.shift();
        if (item) {
          localStorage.removeItem(item.key);
          totalSize -= item.size;
        }
      }
    }
  }
}

export const storage = new Storage();
