import React, { forwardRef } from 'react';
import styled, { css, keyframes } from 'styled-components';

// Checkbox container
const CheckboxContainer = styled.label`
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  margin-bottom: var(--spacing-sm);
`;

// Hide the default checkbox
const HiddenCheckbox = styled.input.attrs({ type: 'checkbox' })`
  position: absolute;
  opacity: 0;
  height: 0;
  width: 0;
`;

// Checkmark animation
const checkmarkAnimation = keyframes`
  0% {
    stroke-dashoffset: 24;
  }
  100% {
    stroke-dashoffset: 0;
  }
`;

// Custom checkbox sizes
const sizes = {
  sm: {
    size: '16px',
    borderRadius: 'var(--radius-sm)',
  },
  md: {
    size: '20px',
    borderRadius: 'var(--radius-md)',
  },
  lg: {
    size: '24px',
    borderRadius: 'var(--radius-md)',
  },
};

// Custom checkbox
const StyledCheckbox = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: ${props => sizes[props.size].size};
  height: ${props => sizes[props.size].size};
  background: ${props => props.checked ? 'var(--color-primary-500)' : 'transparent'};
  border: ${props => props.checked ? '2px solid var(--color-primary-500)' : '2px solid var(--color-neutral-400)'};
  border-radius: ${props => sizes[props.size].borderRadius};
  transition: all var(--duration-fast) var(--timing-ease);
  
  ${props => props.indeterminate && css`
    background: var(--color-primary-500);
    border: 2px solid var(--color-primary-500);
  `}
  
  &:hover {
    border-color: ${props => props.checked ? 'var(--color-primary-600)' : 'var(--color-primary-400)'};
    background: ${props => props.checked ? 'var(--color-primary-600)' : 'var(--color-primary-50)'};
  }
  
  /* Disabled state */
  ${props => props.disabled && css`
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover {
      border-color: ${props => props.checked ? 'var(--color-primary-500)' : 'var(--color-neutral-400)'};
      background: ${props => props.checked ? 'var(--color-primary-500)' : 'transparent'};
    }
  `}
  
  /* Checkmark icon */
  svg {
    visibility: ${props => props.checked ? 'visible' : 'hidden'};
    
    path {
      stroke-dasharray: 24;
      stroke-dashoffset: ${props => props.checked ? 0 : 24};
      animation: ${props => props.checked ? css`${checkmarkAnimation} 0.3s ease-in-out forwards` : 'none'};
    }
  }
  
  /* Indeterminate icon */
  &::after {
    content: '';
    display: ${props => props.indeterminate ? 'block' : 'none'};
    width: 10px;
    height: 2px;
    background: white;
  }
`;

// Checkbox label
const Label = styled.span`
  margin-left: var(--spacing-sm);
  font-size: ${props => 
    props.size === 'sm' ? 'var(--font-size-xs)' :
    props.size === 'md' ? 'var(--font-size-sm)' :
    'var(--font-size-md)'
  };
  color: ${props => props.disabled ? 'var(--color-neutral-500)' : 'var(--color-text-primary)'};
`;

// Helper text
const HelperText = styled.div`
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
  margin-left: ${props => 
    props.size === 'sm' ? '24px' :
    props.size === 'md' ? '28px' :
    '32px'
  };
  color: ${props => 
    props.state === 'error' ? 'var(--color-error-main)' :
    props.state === 'success' ? 'var(--color-success-main)' :
    'var(--color-neutral-600)'
  };
`;

// Checkbox component
const Checkbox = forwardRef(({
  label,
  helperText,
  state,
  size = 'md',
  indeterminate = false,
  checked = false,
  disabled = false,
  onChange,
  ...props
}, ref) => {
  return (
    <div>
      <CheckboxContainer disabled={disabled}>
        <HiddenCheckbox
          ref={ref}
          checked={checked}
          disabled={disabled}
          onChange={onChange}
          {...props}
        />
        <StyledCheckbox
          checked={checked}
          disabled={disabled}
          indeterminate={indeterminate}
          size={size}
        >
          {!indeterminate && (
            <svg width="12" height="10" viewBox="0 0 12 10" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M1 5L4.5 8.5L11 1.5"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </StyledCheckbox>
        {label && <Label size={size} disabled={disabled}>{label}</Label>}
      </CheckboxContainer>
      
      {helperText && <HelperText state={state} size={size}>{helperText}</HelperText>}
    </div>
  );
});

export default Checkbox;
