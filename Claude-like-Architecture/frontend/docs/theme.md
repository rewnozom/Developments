# Theme Customization Guide

## Overview

The application uses a dark theme with glass morphism effects and orange accents. The theme system is built with:
- CSS Variables
- Tailwind CSS
- CSS-in-JS support
- Dark/Light mode support

## Color Palette

### Base Colors
```css
--bg-primary: rgba(43, 41, 41, 0.85);    /* Primary background */
--bg-secondary: #1a1a1a;                 /* Secondary background */
--bg-tertiary: #262626;                  /* Tertiary background */

--text-primary: rgb(209, 204, 204);      /* Primary text */
--text-secondary: #d4d4d4;               /* Secondary text */
--text-tertiary: #a3a3a3;                /* Tertiary text */

--accent-primary: #fb923c;               /* Primary accent (orange) */
--accent-secondary: #f97316;             /* Secondary accent */
--accent-tertiary: #ea580c;              /* Tertiary accent */
```

### Special Effects
```css
--border-color: rgba(82, 82, 82, 0.3);   /* Border color */
--shadow-color: rgba(0, 0, 0, 0.3);      /* Shadow color */
--glass-bg: rgba(26, 26, 26, 0.9);       /* Glass effect background */
```

## Glass Morphism

### Basic Glass Effect
```css
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
}
```

### Light Glass Effect
```css
.glass-light {
  background: rgba(26, 26, 26, 0.7);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color);
}
```

## Component Themes

### Buttons
```css
/* Primary Button */
.btn-primary {
  background-color: var(--accent-primary);
  color: white;
  transition: background-color 200ms;
}
.btn-primary:hover {
  background-color: var(--accent-secondary);
}

/* Secondary Button */
.btn-secondary {
  background-color: rgba(82, 82, 82, 0.3);
  color: var(--text-primary);
}
```

### Inputs
```css
.input {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.input:focus {
  border-color: var(--accent-primary);
}
```

### Cards
```css
.card {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px var(--shadow-color);
}
```

## Dark Mode Support

### Theme Provider Usage
```typescript
import { useTheme } from '@/hooks/useTheme';

const MyComponent = () => {
  const { theme, setTheme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      Toggle {theme} mode
    </button>
  );
};
```

### Dark Mode Classes
```css
/* Dark mode specific styles */
:root[data-theme="dark"] {
  --bg-primary: rgba(43, 41, 41, 0.85);
  --text-primary: rgb(209, 204, 204);
}

/* Light mode specific styles */
:root[data-theme="light"] {
  --bg-primary: rgba(255, 255, 255, 0.85);
  --text-primary: rgb(51, 51, 51);
}
```

## Animation Effects

### Transitions
```css
.transition-fast {
  transition: all 150ms ease-in-out;
}

.transition-normal {
  transition: all 200ms ease-in-out;
}

.transition-slow {
  transition: all 300ms ease-in-out;
}
```

### Animations
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeIn 200ms ease-out;
}
```

## Customizing Themes

### Creating Custom Themes

1. Define theme colors in `src/constants/theme.ts`:
```typescript
export const customTheme = {
  colors: {
    primary: '#your-color',
    secondary: '#your-color',
    // ... other colors
  },
  effects: {
    // ... custom effects
  }
};
```

2. Register theme in ThemeProvider:
```typescript
const themes = {
  default: defaultTheme,
  custom: customTheme,
};
```

3. Use custom theme:
```typescript
const { setTheme } = useTheme();
setTheme('custom');
```

### Theme Variables

```css
/* Define CSS variables */
:root {
  /* Colors */
  --color-primary: #fb923c;
  --color-secondary: #f97316;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px var(--shadow-color);
  --shadow-md: 0 4px 6px var(--shadow-color);
}
```

## Layout & Spacing

### Container Sizes
```css
.container-sm {
  max-width: 640px;
}

.container-md {
  max-width: 768px;
}

.container-lg {
  max-width: 1024px;
}
```

### Spacing Scale
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

## Responsive Design

### Breakpoints
```css
/* Small (mobile) */
@media (min-width: 640px) {
  /* styles */
}

/* Medium (tablet) */
@media (min-width: 768px) {
  /* styles */
}

/* Large (desktop) */
@media (min-width: 1024px) {
  /* styles */
}
```