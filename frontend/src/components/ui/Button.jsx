import styled, { css } from 'styled-components';
import { darken, lighten } from 'polished';

// Button variants
const variants = {
  // Primary button
  primary: css`
    background-color: var(--color-primary-500);
    color: white;
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-700);
    }
  `,
  
  // Secondary button
  secondary: css`
    background-color: var(--color-secondary-500);
    color: white;
    
    &:hover:not(:disabled) {
      background-color: var(--color-secondary-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-secondary-700);
    }
  `,
  
  // Accent button
  accent: css`
    background-color: var(--color-accent-500);
    color: var(--color-neutral-900);
    
    &:hover:not(:disabled) {
      background-color: var(--color-accent-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-accent-700);
    }
  `,
  
  // Outline button
  outline: css`
    background-color: transparent;
    color: var(--color-primary-500);
    border: 2px solid var(--color-primary-500);
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-50);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-100);
    }
  `,
  
  // Ghost button
  ghost: css`
    background-color: transparent;
    color: var(--color-primary-500);
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-50);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-100);
    }
  `,
  
  // Danger button
  danger: css`
    background-color: var(--color-error-main);
    color: white;
    
    &:hover:not(:disabled) {
      background-color: ${props => darken(0.1, props.theme.colors.error.main)};
    }
    
    &:active:not(:disabled) {
      background-color: ${props => darken(0.2, props.theme.colors.error.main)};
    }
  `,
  
  // Success button
  success: css`
    background-color: var(--color-success-main);
    color: white;
    
    &:hover:not(:disabled) {
      background-color: ${props => darken(0.1, props.theme.colors.success.main)};
    }
    
    &:active:not(:disabled) {
      background-color: ${props => darken(0.2, props.theme.colors.success.main)};
    }
  `,
};

// Button sizes
const sizes = {
  xs: css`
    font-size: var(--font-size-xs);
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-md);
  `,
  
  sm: css`
    font-size: var(--font-size-sm);
    padding: 0.375rem 0.75rem;
    border-radius: var(--radius-md);
  `,
  
  md: css`
    font-size: var(--font-size-md);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
  `,
  
  lg: css`
    font-size: var(--font-size-lg);
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-lg);
  `,
  
  xl: css`
    font-size: var(--font-size-xl);
    padding: 1rem 2rem;
    border-radius: var(--radius-lg);
  `,
};

// Button component
const Button = styled.button`
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-medium);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--timing-ease);
  white-space: nowrap;
  text-decoration: none;
  
  /* Apply variant styles */
  ${props => variants[props.variant || 'primary']}
  
  /* Apply size styles */
  ${props => sizes[props.size || 'md']}
  
  /* Full width option */
  ${props => props.fullWidth && css`
    width: 100%;
  `}
  
  /* Icon spacing */
  & > svg {
    margin-right: ${props => props.iconRight ? '0' : '0.5rem'};
    margin-left: ${props => props.iconRight ? '0.5rem' : '0'};
  }
  
  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Loading state */
  ${props => props.isLoading && css`
    position: relative;
    color: transparent;
    pointer-events: none;
    
    &::after {
      content: '';
      position: absolute;
      width: 1rem;
      height: 1rem;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `}
`;

export default Button;
