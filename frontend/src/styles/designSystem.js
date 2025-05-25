/**
 * Todo AI Design System
 * 
 * This file contains the core design tokens and theme variables
 * for the Todo AI application. It defines colors, typography,
 * spacing, shadows, and other design elements.
 */

// Color Palette
export const colors = {
  // Primary Colors
  primary: {
    50: '#EBF5FF',
    100: '#D6EBFF',
    200: '#ADD6FF',
    300: '#84C1FF',
    400: '#5AABFF',
    500: '#3195FF', // Main primary color
    600: '#1A7AE5',
    700: '#0D5FBF',
    800: '#064599',
    900: '#032C73',
  },
  
  // Secondary Colors
  secondary: {
    50: '#F2EBFF',
    100: '#E5D6FF',
    200: '#CCADFF',
    300: '#B284FF',
    400: '#995AFF',
    500: '#7F30FF', // Main secondary color
    600: '#661AE5',
    700: '#4C0DBF',
    800: '#330699',
    900: '#1A0373',
  },
  
  // Accent Colors
  accent: {
    50: '#EBFFF6',
    100: '#D6FFED',
    200: '#ADFFDB',
    300: '#84FFC9',
    400: '#5AFFB7',
    500: '#30FFA5', // Main accent color
    600: '#1AE58A',
    700: '#0DBF6F',
    800: '#069954',
    900: '#037339',
  },
  
  // Neutral Colors
  neutral: {
    50: '#F8F9FA',
    100: '#F1F3F5',
    200: '#E9ECEF',
    300: '#DEE2E6',
    400: '#CED4DA',
    500: '#ADB5BD',
    600: '#868E96',
    700: '#495057',
    800: '#343A40',
    900: '#212529',
  },
  
  // Semantic Colors
  success: {
    light: '#D4EDDA',
    main: '#28A745',
    dark: '#1E7E34',
  },
  warning: {
    light: '#FFF3CD',
    main: '#FFC107',
    dark: '#D39E00',
  },
  error: {
    light: '#F8D7DA',
    main: '#DC3545',
    dark: '#BD2130',
  },
  info: {
    light: '#D1ECF1',
    main: '#17A2B8',
    dark: '#117A8B',
  },
};

// Typography
export const typography = {
  fontFamily: {
    heading: "'Poppins', sans-serif",
    body: "'Inter', sans-serif",
    mono: "'Roboto Mono', monospace",
  },
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    md: '1rem',       // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
};

// Spacing
export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '2.5rem', // 40px
  '3xl': '3rem',   // 48px
  '4xl': '4rem',   // 64px
};

// Shadows
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
};

// Border Radius
export const borderRadius = {
  none: '0',
  sm: '0.125rem',  // 2px
  md: '0.25rem',   // 4px
  lg: '0.5rem',    // 8px
  xl: '0.75rem',   // 12px
  '2xl': '1rem',   // 16px
  '3xl': '1.5rem', // 24px
  full: '9999px',
};

// Transitions
export const transitions = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  timing: {
    ease: 'ease',
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

// Z-Index
export const zIndex = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
};

// Breakpoints
export const breakpoints = {
  xs: '0px',
  sm: '576px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  '2xl': '1400px',
};

// Default Theme
export const lightTheme = {
  colors: {
    background: colors.neutral[50],
    surface: '#FFFFFF',
    text: {
      primary: colors.neutral[900],
      secondary: colors.neutral[700],
      disabled: colors.neutral[500],
    },
    border: colors.neutral[300],
    divider: colors.neutral[200],
    ...colors,
  },
  typography,
  spacing,
  shadows,
  borderRadius,
  transitions,
  zIndex,
  breakpoints,
};

// Dark Theme
export const darkTheme = {
  colors: {
    background: colors.neutral[900],
    surface: colors.neutral[800],
    text: {
      primary: colors.neutral[50],
      secondary: colors.neutral[300],
      disabled: colors.neutral[500],
    },
    border: colors.neutral[700],
    divider: colors.neutral[700],
    ...colors,
  },
  typography,
  spacing,
  shadows,
  borderRadius,
  transitions,
  zIndex,
  breakpoints,
};

export default lightTheme;
