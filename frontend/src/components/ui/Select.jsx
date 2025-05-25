import React, { forwardRef } from 'react';
import styled, { css } from 'styled-components';

// Select container
const SelectContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-md);
  width: 100%;
`;

// Select label
const Label = styled.label`
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
  color: var(--color-text-secondary);
`;

// Select variants
const variants = {
  // Default select
  default: css`
    border: 1px solid var(--color-neutral-300);
    
    &:hover:not(:disabled) {
      border-color: var(--color-neutral-400);
    }
    
    &:focus {
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 2px var(--color-primary-100);
    }
  `,
  
  // Filled select
  filled: css`
    border: none;
    background-color: var(--color-neutral-100);
    
    &:hover:not(:disabled) {
      background-color: var(--color-neutral-200);
    }
    
    &:focus {
      background-color: var(--color-neutral-100);
      box-shadow: 0 0 0 2px var(--color-primary-100);
    }
  `,
  
  // Flushed select (bottom border only)
  flushed: css`
    border: none;
    border-bottom: 1px solid var(--color-neutral-300);
    border-radius: 0;
    padding-left: 0;
    padding-right: 0;
    
    &:hover:not(:disabled) {
      border-bottom-color: var(--color-neutral-400);
    }
    
    &:focus {
      border-bottom-color: var(--color-primary-500);
      box-shadow: 0 1px 0 0 var(--color-primary-500);
    }
  `,
};

// Select sizes
const sizes = {
  sm: css`
    font-size: var(--font-size-xs);
    padding: 0.375rem 0.5rem;
    border-radius: var(--radius-md);
  `,
  
  md: css`
    font-size: var(--font-size-sm);
    padding: 0.5rem 0.75rem;
    border-radius: var(--radius-md);
  `,
  
  lg: css`
    font-size: var(--font-size-md);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
  `,
};

// Select states
const selectStates = {
  // Error state
  error: css`
    border-color: var(--color-error-main);
    
    &:hover:not(:disabled) {
      border-color: var(--color-error-main);
    }
    
    &:focus {
      border-color: var(--color-error-main);
      box-shadow: 0 0 0 2px var(--color-error-light);
    }
  `,
  
  // Success state
  success: css`
    border-color: var(--color-success-main);
    
    &:hover:not(:disabled) {
      border-color: var(--color-success-main);
    }
    
    &:focus {
      border-color: var(--color-success-main);
      box-shadow: 0 0 0 2px var(--color-success-light);
    }
  `,
};

// Base select styles
const SelectBase = styled.select`
  /* Base styles */
  width: 100%;
  background-color: ${props => props.variant === 'filled' ? 'var(--color-neutral-100)' : 'transparent'};
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--timing-ease);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
  padding-right: 2rem;
  
  /* Apply variant styles */
  ${props => variants[props.variant || 'default']}
  
  /* Apply size styles */
  ${props => sizes[props.size || 'md']}
  
  /* Apply state styles */
  ${props => props.state && selectStates[props.state]}
  
  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: var(--color-neutral-100);
  }
`;

// Helper text
const HelperText = styled.div`
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
  color: ${props => 
    props.state === 'error' ? 'var(--color-error-main)' :
    props.state === 'success' ? 'var(--color-success-main)' :
    'var(--color-neutral-600)'
  };
`;

// Select component
const Select = forwardRef(({
  label,
  helperText,
  state,
  variant = 'default',
  size = 'md',
  children,
  ...props
}, ref) => {
  return (
    <SelectContainer>
      {label && <Label>{label}</Label>}
      
      <SelectBase
        ref={ref}
        variant={variant}
        size={size}
        state={state}
        {...props}
      >
        {children}
      </SelectBase>
      
      {helperText && <HelperText state={state}>{helperText}</HelperText>}
    </SelectContainer>
  );
});

export default Select;
