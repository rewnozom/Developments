import { storage } from './storage';

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeConfig {
  theme: Theme;
  systemPreference: 'light' | 'dark';
}

class ThemeManager {
  private storageKey = 'theme_preference';
  private defaultTheme: Theme = 'system';

  constructor() {
    this.initialize();
    this.watchSystemTheme();
  }

  private initialize() {
    const stored = storage.get<ThemeConfig>(this.storageKey);
    if (!stored) {
      this.setTheme(this.defaultTheme);
    } else {
      this.applyTheme(stored);
    }
  }

  private watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      const stored = storage.get<ThemeConfig>(this.storageKey);
      if (stored && stored.theme === 'system') {
        this.updateSystemPreference(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    handleChange(mediaQuery);
  }

  private updateSystemPreference(preference: 'light' | 'dark') {
    const config = storage.get<ThemeConfig>(this.storageKey);
    if (config) {
      config.systemPreference = preference;
      storage.set(this.storageKey, config);
      this.applyTheme(config);
    }
  }

  public getTheme(): ThemeConfig {
    return storage.get<ThemeConfig>(this.storageKey) || {
      theme: this.defaultTheme,
      systemPreference: window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light',
    };
  }

  public setTheme(theme: Theme) {
    const config: ThemeConfig = {
      theme,
      systemPreference: window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light',
    };
    storage.set(this.storageKey, config);
    this.applyTheme(config);
  }

  private applyTheme(config: ThemeConfig) {
    const isDark =
      config.theme === 'system'
        ? config.systemPreference === 'dark'
        : config.theme === 'dark';

    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    // Update meta theme-color
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', isDark ? '#1a1a1a' : '#ffffff');
  }

  public toggleTheme() {
    const current = this.getTheme();
    const newTheme: Theme = current.theme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  }
}

export const themeManager = new ThemeManager();
