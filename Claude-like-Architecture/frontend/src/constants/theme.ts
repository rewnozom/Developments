export const THEME = {
    colors: {
      // Backgrounds
      bgPrimary: 'rgba(43, 41, 41, 0.85)',
      bgSecondary: '#1a1a1a',
      bgTertiary: '#262626',
      
      // Text colors
      textPrimary: 'rgb(209, 204, 204)',
      textSecondary: '#d4d4d4',
      textTertiary: '#a3a3a3',
      
      // Accent colors
      accentPrimary: '#fb923c',
      accentSecondary: '#f97316',
      accentTertiary: '#ea580c',
      
      // Special effects
      border: 'rgba(82, 82, 82, 0.3)',
      shadow: 'rgba(0, 0, 0, 0.3)',
      glass: 'rgba(26, 26, 26, 0.9)',
    },
    
    effects: {
      // Glass effect classes
      glass: 'backdrop-blur-md bg-[rgba(26,26,26,0.9)]',
      glassLight: 'backdrop-blur-sm bg-[rgba(26,26,26,0.7)]',
      
      // Transitions
      transition: 'transition-all duration-200 ease-in-out',
      transitionFast: 'transition-all duration-150 ease-in-out',
      transitionSlow: 'transition-all duration-300 ease-in-out',
      
      // Hover effects
      hoverAccent: 'hover:bg-[#f97316] hover:border-[#fb923c]',
      hoverGlass: 'hover:bg-[rgba(82,82,82,0.3)]',
      
      // Shadows
      shadowSm: 'shadow-sm shadow-black/30',
      shadowMd: 'shadow-md shadow-black/30',
      shadowLg: 'shadow-lg shadow-black/30',
    },
  
    components: {
      // Common component styles
      button: `
        rounded-lg px-4 py-2 font-medium 
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-[#fb923c] focus:ring-opacity-50
      `,
      buttonPrimary: `
        bg-[#fb923c] text-white
        hover:bg-[#f97316]
        disabled:bg-[rgba(82,82,82,0.3)] disabled:text-[#a3a3a3]
      `,
      buttonSecondary: `
        bg-[rgba(82,82,82,0.3)] text-[#e5e5e5]
        hover:bg-[rgba(82,82,82,0.5)]
        disabled:bg-[rgba(82,82,82,0.15)] disabled:text-[#a3a3a3]
      `,
      input: `
        rounded-lg border border-[rgba(82,82,82,0.3)]
        bg-[#1a1a1a] text-[#e5e5e5]
        focus:border-[#fb923c] focus:outline-none
        placeholder:text-[#a3a3a3]
      `,
      card: `
        rounded-lg border border-[rgba(82,82,82,0.3)]
        bg-[#262626] shadow-lg backdrop-blur-sm
      `,
    },
  } as const;
  
  // Re-export as individual constants for easier imports
  export const {colors, effects, components} = THEME;