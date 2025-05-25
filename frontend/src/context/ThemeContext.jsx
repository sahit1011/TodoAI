import { createContext, useState, useContext, useEffect } from 'react';
import { ThemeProvider as StyledThemeProvider, createGlobalStyle } from 'styled-components';
import { lightTheme, darkTheme } from '../styles/designSystem';

// Create theme context
const ThemeContext = createContext({
  theme: 'light',
  toggleTheme: () => {},
});

// Global styles
const GlobalStyle = createGlobalStyle`
  :root {
    /* Import design tokens as CSS variables */
    ${({ theme }) => {
      let cssVars = '';
      
      // Colors
      Object.entries(theme.colors).forEach(([key, value]) => {
        if (typeof value === 'object') {
          Object.entries(value).forEach(([subKey, subValue]) => {
            cssVars += `--color-${key}-${subKey}: ${subValue};\n`;
          });
        } else {
          cssVars += `--color-${key}: ${value};\n`;
        }
      });
      
      // Typography
      Object.entries(theme.typography.fontFamily).forEach(([key, value]) => {
        cssVars += `--font-family-${key}: ${value};\n`;
      });
      
      Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
        cssVars += `--font-size-${key}: ${value};\n`;
      });
      
      Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
        cssVars += `--font-weight-${key}: ${value};\n`;
      });
      
      Object.entries(theme.typography.lineHeight).forEach(([key, value]) => {
        cssVars += `--line-height-${key}: ${value};\n`;
      });
      
      // Spacing
      Object.entries(theme.spacing).forEach(([key, value]) => {
        cssVars += `--spacing-${key}: ${value};\n`;
      });
      
      // Border Radius
      Object.entries(theme.borderRadius).forEach(([key, value]) => {
        cssVars += `--radius-${key}: ${value};\n`;
      });
      
      // Shadows
      Object.entries(theme.shadows).forEach(([key, value]) => {
        cssVars += `--shadow-${key}: ${value};\n`;
      });
      
      // Transitions
      Object.entries(theme.transitions.duration).forEach(([key, value]) => {
        cssVars += `--duration-${key}: ${value};\n`;
      });
      
      Object.entries(theme.transitions.timing).forEach(([key, value]) => {
        cssVars += `--timing-${key}: ${value};\n`;
      });
      
      return cssVars;
    }}
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html, body {
    font-family: var(--font-family-body);
    font-size: 16px;
    line-height: var(--line-height-normal);
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.text.primary};
    transition: background-color var(--duration-normal) var(--timing-ease);
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-heading);
    font-weight: var(--font-weight-semibold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--spacing-md);
  }

  h1 {
    font-size: var(--font-size-4xl);
  }

  h2 {
    font-size: var(--font-size-3xl);
  }

  h3 {
    font-size: var(--font-size-2xl);
  }

  h4 {
    font-size: var(--font-size-xl);
  }

  h5 {
    font-size: var(--font-size-lg);
  }

  h6 {
    font-size: var(--font-size-md);
  }

  p {
    margin-bottom: var(--spacing-md);
  }

  a {
    color: var(--color-primary-500);
    text-decoration: none;
    transition: color var(--duration-fast) var(--timing-ease);
  }

  a:hover {
    color: var(--color-primary-700);
  }

  button {
    cursor: pointer;
    font-family: var(--font-family-body);
  }

  input, textarea, select {
    font-family: var(--font-family-body);
  }

  /* Add smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Remove focus outline for mouse users, keep for keyboard */
  :focus:not(:focus-visible) {
    outline: none;
  }

  :focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
`;

// Theme provider component
export const ThemeProvider = ({ children }) => {
  // Check if user has a theme preference in localStorage or prefers dark mode
  const getInitialTheme = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme;
    }
    
    // Check user's system preference
    const prefersDark = window.matchMedia && 
      window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    return prefersDark ? 'dark' : 'light';
  };

  const [theme, setTheme] = useState('light'); // Default to light, will be updated in useEffect

  // Set initial theme after component mounts to avoid SSR issues
  useEffect(() => {
    setTheme(getInitialTheme());
  }, []);

  // Update localStorage when theme changes
  useEffect(() => {
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  // Get the current theme object
  const themeObject = theme === 'dark' ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <StyledThemeProvider theme={themeObject}>
        <GlobalStyle />
        {children}
      </StyledThemeProvider>
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeProvider;
