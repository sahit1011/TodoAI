import styled, { css } from 'styled-components';

// Card variants
const variants = {
  // Default card
  default: css`
    background-color: ${props => props.theme.colors.surface};
    border: 1px solid var(--color-neutral-200);
  `,
  
  // Elevated card with shadow
  elevated: css`
    background-color: ${props => props.theme.colors.surface};
    box-shadow: var(--shadow-md);
    border: none;
  `,
  
  // Outlined card
  outlined: css`
    background-color: transparent;
    border: 1px solid var(--color-neutral-300);
  `,
  
  // Filled card with background color
  filled: css`
    background-color: var(--color-neutral-100);
    border: none;
  `,
};

// Card component
const Card = styled.div`
  /* Base styles */
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: transform var(--duration-normal) var(--timing-ease),
              box-shadow var(--duration-normal) var(--timing-ease);
  
  /* Apply variant styles */
  ${props => variants[props.variant || 'default']}
  
  /* Interactive card */
  ${props => props.interactive && css`
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    
    &:active {
      transform: translateY(0);
      box-shadow: var(--shadow-md);
    }
  `}
  
  /* Priority indicator */
  ${props => props.priority && css`
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background-color: ${
        props.priority === 'low' ? 'var(--color-success-main)' :
        props.priority === 'medium' ? 'var(--color-warning-main)' :
        props.priority === 'high' ? 'var(--color-error-main)' :
        props.priority === 'urgent' ? 'var(--color-error-dark)' :
        'var(--color-neutral-400)'
      };
    }
  `}
  
  /* Completed task styling */
  ${props => props.completed && css`
    opacity: 0.7;
    background-color: ${props => 
      props.variant === 'default' || props.variant === 'elevated' 
        ? 'var(--color-neutral-100)' 
        : 'transparent'
    };
    
    /* Add strikethrough for completed tasks */
    & ${CardTitle} {
      text-decoration: line-through;
    }
    
    & ${CardContent} {
      text-decoration: line-through;
    }
  `}
`;

// Card header
export const CardHeader = styled.div`
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-neutral-200);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

// Card title
export const CardTitle = styled.h3`
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
`;

// Card content
export const CardContent = styled.div`
  padding: var(--spacing-lg);
`;

// Card footer
export const CardFooter = styled.div`
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-neutral-200);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
`;

// Card media
export const CardMedia = styled.div`
  width: 100%;
  height: ${props => props.height || '200px'};
  background-image: url(${props => props.image});
  background-size: cover;
  background-position: center;
`;

// Card badge
export const CardBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  background-color: ${props => 
    props.variant === 'success' ? 'var(--color-success-light)' :
    props.variant === 'warning' ? 'var(--color-warning-light)' :
    props.variant === 'error' ? 'var(--color-error-light)' :
    props.variant === 'info' ? 'var(--color-info-light)' :
    props.variant === 'primary' ? 'var(--color-primary-100)' :
    'var(--color-neutral-200)'
  };
  color: ${props => 
    props.variant === 'success' ? 'var(--color-success-main)' :
    props.variant === 'warning' ? 'var(--color-warning-main)' :
    props.variant === 'error' ? 'var(--color-error-main)' :
    props.variant === 'info' ? 'var(--color-info-main)' :
    props.variant === 'primary' ? 'var(--color-primary-700)' :
    'var(--color-neutral-700)'
  };
  margin-right: var(--spacing-xs);
`;

export default Card;
