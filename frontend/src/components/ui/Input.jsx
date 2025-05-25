import React, { forwardRef } from 'react';
import styled, { css } from 'styled-components';

// Input container
const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-md);
  width: 100%;
`;

// Input label
const Label = styled.label`
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
  color: var(--color-text-secondary);
`;

// Input variants
const variants = {
  // Default input
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
  
  // Filled input
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
  
  // Flushed input (bottom border only)
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

// Input sizes
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

// Input states
const inputStates = {
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

// Base input styles
const InputBase = styled.input`
  /* Base styles */
  width: 100%;
  background-color: ${props => props.variant === 'filled' ? 'var(--color-neutral-100)' : 'transparent'};
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--timing-ease);
  outline: none;
  
  /* Apply variant styles */
  ${props => variants[props.variant || 'default']}
  
  /* Apply size styles */
  ${props => sizes[props.size || 'md']}
  
  /* Apply state styles */
  ${props => props.state && inputStates[props.state]}
  
  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: var(--color-neutral-100);
  }
  
  /* Placeholder styling */
  &::placeholder {
    color: var(--color-neutral-500);
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

// Input group for prefix/suffix
const InputGroup = styled.div`
  display: flex;
  align-items: center;
  position: relative;
`;

const InputAddon = styled.div`
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-sm);
  color: var(--color-neutral-600);
  background-color: var(--color-neutral-100);
  border: 1px solid var(--color-neutral-300);
  font-size: var(--font-size-sm);
  
  ${props => props.position === 'left' && css`
    border-right: none;
    border-top-left-radius: var(--radius-md);
    border-bottom-left-radius: var(--radius-md);
  `}
  
  ${props => props.position === 'right' && css`
    border-left: none;
    border-top-right-radius: var(--radius-md);
    border-bottom-right-radius: var(--radius-md);
  `}
`;

// Input component
const Input = forwardRef(({
  label,
  helperText,
  state,
  variant = 'default',
  size = 'md',
  prefix,
  suffix,
  ...props
}, ref) => {
  return (
    <InputContainer>
      {label && <Label>{label}</Label>}
      
      {prefix || suffix ? (
        <InputGroup>
          {prefix && <InputAddon position="left">{prefix}</InputAddon>}
          <InputBase
            ref={ref}
            variant={variant}
            size={size}
            state={state}
            {...props}
            style={{
              ...(prefix && { borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }),
              ...(suffix && { borderTopRightRadius: 0, borderBottomRightRadius: 0 }),
            }}
          />
          {suffix && <InputAddon position="right">{suffix}</InputAddon>}
        </InputGroup>
      ) : (
        <InputBase
          ref={ref}
          variant={variant}
          size={size}
          state={state}
          {...props}
        />
      )}
      
      {helperText && <HelperText state={state}>{helperText}</HelperText>}
    </InputContainer>
  );
});

export default Input;
