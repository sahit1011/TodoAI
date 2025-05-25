import { useRef, useEffect } from 'react';
import styled from 'styled-components';

const HighlightOverlay = styled.div`
  position: absolute;
  pointer-events: none;
  border: 2px solid #4a90e2;
  background-color: rgba(74, 144, 226, 0.1);
  border-radius: 4px;
  z-index: 1000;
  transition: all 0.3s ease;
`;

const UIActionExecutor = ({ actions, onComplete }) => {
  const overlayRef = useRef(null);

  useEffect(() => {
    console.log('UIActionExecutor useEffect triggered with actions:', actions);
    if (!actions || actions.length === 0) {
      console.log('No actions to execute');
      return;
    }

    // Set a global flag to indicate automated actions are in progress
    window.isAutomatedAction = true;
    console.log('Setting isAutomatedAction flag to true');

    // Remove duplicate actions
    const uniqueActions = [];
    const actionStrings = new Set();

    actions.forEach(action => {
      const actionString = JSON.stringify(action);
      if (!actionStrings.has(actionString)) {
        actionStrings.add(actionString);
        uniqueActions.push(action);
      }
    });

    console.log(`Filtered ${actions.length} actions to ${uniqueActions.length} unique actions`);

    // Create a function to execute all actions in sequence
    const executeAllActions = async () => {
      try {
        console.log(`Starting execution of ${uniqueActions.length} actions`);

        // Execute each action in sequence with proper delays
        for (let i = 0; i < uniqueActions.length; i++) {
          console.log(`Executing action ${i + 1}/${uniqueActions.length}:`, uniqueActions[i]);

          // Wait before starting each action (reduced delay)
          if (i > 0) {
            console.log(`Waiting before starting action ${i + 1}...`);
            await new Promise(resolve => setTimeout(resolve, 300));
          }

          // Execute the action
          await executeAction(uniqueActions[i]);

          // Wait after each action to ensure it completes (reduced delay)
          console.log(`Action ${i + 1} executed, waiting before next action...`);
          await new Promise(resolve => setTimeout(resolve, 400));
        }

        console.log('All actions executed successfully');

        // Reset the automated action flag
        window.isAutomatedAction = false;
        console.log('Setting isAutomatedAction flag to false');

        // Call onComplete after all actions are done
        if (onComplete) {
          console.log('Calling onComplete callback');
          setTimeout(() => onComplete(), 200);
        }
      } catch (error) {
        console.error('Error executing actions:', error);

        // Reset the automated action flag even on error
        window.isAutomatedAction = false;
        console.log('Setting isAutomatedAction flag to false after error');

        // Still call onComplete even if there was an error
        if (onComplete) {
          console.log('Calling onComplete callback after error');
          setTimeout(() => onComplete(), 200);
        }
      }
    };

    // Start executing actions
    executeAllActions();

    // Cleanup function to ensure flag is reset if component unmounts
    return () => {
      window.isAutomatedAction = false;
      console.log('Cleanup: Setting isAutomatedAction flag to false');
    };
  }, [actions, onComplete]);

  const executeAction = async (action) => {
    console.log('Executing UI action:', action);

    try {
      if (!action || typeof action !== 'object' || !action.type) {
        console.error('Invalid action object:', action);
        return;
      }

      switch (action.type) {
        case 'navigate':
          await navigateTo(action.target);
          break;
        case 'click':
          await clickElement(action.target);
          break;
        case 'fill_form':
          await fillForm(action.target, action.data);
          break;
        case 'search':
          await searchFor(action.target, action.query);
          break;
        default:
          console.warn(`Unknown action type: ${action.type}`);
      }
    } catch (error) {
      console.error('Error executing UI action:', error);
    }
  };

  const navigateTo = async (target) => {
    // Handle navigation to different sections of the app
    console.log(`Navigating to target: ${target}`);

    try {
      if (!target) {
        console.error('Invalid target:', target);
        return;
      }

      const targetElement = document.querySelector(`[data-ui-target="${target}"]`);
      console.log('Found target element:', targetElement);

      if (targetElement) {
        await highlightElement(targetElement);
        // Scroll to the element
        targetElement.scrollIntoView({ behavior: 'smooth' });
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        console.warn(`Target element not found: ${target}`);
        // Log all available data-ui-target elements for debugging
        const allTargets = document.querySelectorAll('[data-ui-target]');
        console.log('Available targets:', Array.from(allTargets).map(el => el.getAttribute('data-ui-target')));
      }
    } catch (error) {
      console.error('Error navigating to target:', error);
    }
  };

  const clickElement = async (target) => {
    console.log(`Clicking element with target: ${target}`);

    try {
      if (!target) {
        console.error('Invalid target:', target);
        return;
      }

      // Wait a moment before trying to find the element (reduced delay)
      await new Promise(resolve => setTimeout(resolve, 100));

      const targetElement = document.querySelector(`[data-ui-target="${target}"]`);
      console.log('Found target element to click:', targetElement);

      if (targetElement) {
        // Check if the element is disabled
        if (targetElement.disabled) {
          console.warn('Element is disabled, waiting for it to become enabled');
          // Wait a bit longer for the element to become enabled (reduced delay)
          await new Promise(resolve => setTimeout(resolve, 300));
        }

        // Highlight the element
        await highlightElement(targetElement);

        // Wait a moment for visual feedback (reduced delay)
        await new Promise(resolve => setTimeout(resolve, 200));

        // Ensure the element is visible and scrolled into view
        targetElement.scrollIntoView({ behavior: 'auto', block: 'center' });
        await new Promise(resolve => setTimeout(resolve, 100));

        // Trigger the click
        console.log('Clicking element:', targetElement);
        targetElement.click();

        // Wait after clicking to allow the action to complete (reduced delay)
        await new Promise(resolve => setTimeout(resolve, 300));
      } else {
        console.warn(`Target element not found for clicking: ${target}`);
        // Log all available data-ui-target elements for debugging
        const allTargets = document.querySelectorAll('[data-ui-target]');
        console.log('Available targets for clicking:', Array.from(allTargets).map(el => el.getAttribute('data-ui-target')));

        // Try again after a short delay (reduced delay)
        console.log('Retrying after delay...');
        await new Promise(resolve => setTimeout(resolve, 300));

        const retryElement = document.querySelector(`[data-ui-target="${target}"]`);
        if (retryElement) {
          console.log('Found element on retry, clicking:', retryElement);
          await highlightElement(retryElement);
          retryElement.click();
        } else {
          console.error(`Element still not found after retry: ${target}`);
        }
      }
    } catch (error) {
      console.error('Error clicking element:', error);
    }
  };

  const fillForm = async (target, data) => {
    console.log(`Filling form with target: ${target} and data:`, data);

    try {
      // First, check if we can use the direct React state setter method
      if (window.setTaskFormValues && target === 'add_task_form') {
        console.log('Using direct React state setter for form values');
        window.setTaskFormValues(data);

        // Highlight the form for visual feedback
        const formContainer = document.querySelector(`[data-ui-target="${target}"]`);
        if (formContainer) {
          await highlightElement(formContainer);
        }

        // Wait a short moment to allow React to update the DOM
        await new Promise(resolve => setTimeout(resolve, 300));
        return;
      }

      // If direct method is not available, fall back to DOM manipulation
      console.log('Direct method not available, falling back to DOM manipulation');

      // Find the form container
      const formContainer = document.querySelector(`[data-ui-target="${target}"]`);
      if (!formContainer) {
        console.warn(`Form container not found: ${target}`);
        // Log all available data-ui-target elements for debugging
        const allTargets = document.querySelectorAll('[data-ui-target]');
        console.log('Available targets:', Array.from(allTargets).map(el => el.getAttribute('data-ui-target')));
        return;
      }

      console.log('Found form container:', formContainer);
      await highlightElement(formContainer);

      // Wait a moment before starting to fill the form
      await new Promise(resolve => setTimeout(resolve, 300));

      // Fill each field
      for (const [key, value] of Object.entries(data)) {
        if (!value) {
          console.log(`Skipping empty value for field: ${key}`);
          continue; // Skip empty values
        }

        console.log(`Looking for field with name: ${key}`);

        // Try to find the field by name attribute, first in the form container, then in the entire document
        let field = formContainer.querySelector(`[name="${key}"]`);

        // If not found in the form container, try to find it by data-ui-target
        if (!field) {
          const targetId = `task_${key}_input`;
          console.log(`Field not found by name, trying data-ui-target: ${targetId}`);
          field = document.querySelector(`[data-ui-target="${targetId}"]`);
        }

        // If still not found, try to find it by ID
        if (!field) {
          const fieldId = `task_${key}_input`;
          console.log(`Field not found by data-ui-target, trying id: ${fieldId}`);
          field = document.getElementById(fieldId);
        }

        // If still not found, try to find it anywhere in the document
        if (!field) {
          console.log(`Field not found in form container, trying document-wide search`);
          field = document.querySelector(`[name="${key}"]`);
        }

        if (field) {
          console.log(`Found field for ${key}:`, field);
          await highlightElement(field);

          // Focus the field first
          field.focus();
          await new Promise(resolve => setTimeout(resolve, 100));

          // Clear the field first
          field.value = '';

          // Set the value directly instead of character by character
          field.value = value;
          console.log(`Set value for ${key} to: ${value}`);

          // Trigger multiple events to ensure the change is registered
          const inputEvent = new Event('input', { bubbles: true });
          field.dispatchEvent(inputEvent);

          const changeEvent = new Event('change', { bubbles: true });
          field.dispatchEvent(changeEvent);

          // For React components, we need to ensure the state is updated
          if (typeof field.onChange === 'function') {
            field.onChange({ target: { value } });
          }

          // Blur the field to trigger any onBlur handlers
          field.blur();

          // Wait a moment between fields
          await new Promise(resolve => setTimeout(resolve, 200));
        } else {
          console.warn(`Field not found: ${key} in form ${target}`);
          // Log all available fields for debugging
          const allFields = document.querySelectorAll('[name]');
          console.log('Available fields:', Array.from(allFields).map(el => el.getAttribute('name')));
        }
      }

      // Wait a moment after filling all fields before proceeding
      await new Promise(resolve => setTimeout(resolve, 300));
    } catch (error) {
      console.error('Error filling form:', error);
    }
  };

  const searchFor = async (target, query) => {
    const searchField = document.querySelector(`[data-ui-target="${target}"]`);
    if (!searchField) {
      console.warn(`Search field not found: ${target}`);
      return;
    }

    await highlightElement(searchField);

    // Set the search query
    searchField.value = query;

    // Trigger change event
    const event = new Event('input', { bubbles: true });
    searchField.dispatchEvent(event);

    // Trigger search (usually Enter key)
    const keyEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      bubbles: true
    });
    searchField.dispatchEvent(keyEvent);
  };

  const highlightElement = async (element) => {
    console.log('Highlighting element:', element);

    try {
      if (!element) {
        console.error('Invalid element to highlight:', element);
        return;
      }

      if (!overlayRef.current) {
        console.error('Overlay reference not available');
        return;
      }

      const rect = element.getBoundingClientRect();
      console.log('Element rect:', rect);

      const overlay = overlayRef.current;

      overlay.style.left = `${rect.left + window.scrollX}px`;
      overlay.style.top = `${rect.top + window.scrollY}px`;
      overlay.style.width = `${rect.width}px`;
      overlay.style.height = `${rect.height}px`;
      overlay.style.opacity = '1';

      // Fade out after a moment
      await new Promise(resolve => setTimeout(resolve, 600));
      overlay.style.opacity = '0';
    } catch (error) {
      console.error('Error highlighting element:', error);
    }
  };

  return <HighlightOverlay ref={overlayRef} style={{ opacity: 0 }} />;
};

export default UIActionExecutor;
