import { useState, useEffect } from 'react'
import styled from 'styled-components'

// Direct API URL
const API_URL = 'http://localhost:8000'

const FormContainer = styled.div`
  margin-bottom: 20px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`

const Form = styled.form`
  display: flex;
  flex-direction: column;
`

const FormRow = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 10px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 5px;
  }
`

const Input = styled.input`
  flex: 3;
  padding: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;
  resize: vertical;
  min-height: 60px;
  margin-bottom: 10px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const Select = styled.select`
  flex: 1;
  padding: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const Button = styled.button`
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  align-self: flex-end;

  &:hover {
    background-color: var(--secondary-color);
  }

  &:disabled {
    background-color: var(--medium-gray);
    cursor: not-allowed;
  }
`

// Create a global reference to store the form state setters
window.taskFormSetters = null;

function AddTaskForm({ onTaskAdded }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('medium')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  // Store the setters in the global reference for direct access
  useEffect(() => {
    window.taskFormSetters = {
      setTitle,
      setDescription,
      setPriority,
      setIsExpanded
    };

    // Create a global function to directly set form values
    window.setTaskFormValues = (formData) => {
      console.log('Direct form value setting:', formData);
      if (formData.title) {
        setTitle(formData.title);
        console.log('Title set directly to:', formData.title);
      }
      if (formData.priority) {
        setPriority(formData.priority);
        console.log('Priority set directly to:', formData.priority);
      }
      if (formData.description) {
        setDescription(formData.description);
        console.log('Description set directly to:', formData.description);
      }
      setIsExpanded(true);
    };

    return () => {
      window.taskFormSetters = null;
      window.setTaskFormValues = null;
    };
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Form submitted with title:', title);

    // More robust title validation
    if (!title || !title.trim()) {
      console.warn('Form submission failed: Empty title');
      // Check if this is an automated submission
      const isAutomated = window.isAutomatedAction;

      if (!isAutomated) {
        // Only show alert for manual submissions
        alert('Please enter a task title');
      } else {
        console.warn('Automated submission with empty title, continuing anyway');
      }

      if (!isAutomated) {
        return; // Only block manual submissions
      }
    }

    setIsSubmitting(true)

    try {
      // Get token from localStorage or use hardcoded token
      const token = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc'

      const response = await fetch(`${API_URL}/api/tasks/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          description: description || undefined,
          priority
        })
      })

      if (response.ok) {
        // Reset form
        setTitle('')
        setDescription('')
        setPriority('medium')
        setIsExpanded(false)

        // Notify parent component
        if (onTaskAdded) {
          onTaskAdded()
        }
      } else {
        const errorText = await response.text()
        console.error('Error creating task:', errorText)
        alert(`Failed to create task: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error creating task:', error)
      alert(`Error: ${error.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <FormContainer data-ui-target="add_task_form">
      <h3>Add New Task</h3>
      <Form onSubmit={handleSubmit} data-ui-target="add_task_form">
        <FormRow>
          <Input
            type="text"
            value={title}
            onChange={(e) => {
              console.log('Title input changed:', e.target.value);
              setTitle(e.target.value);
            }}
            placeholder="Task title"
            onClick={() => setIsExpanded(true)}
            name="title"
            data-ui-target="task_title_input"
            id="task_title_input"
            autoComplete="off"
          />
          <Select
            value={priority}
            onChange={(e) => {
              console.log('Priority select changed:', e.target.value);
              setPriority(e.target.value);
            }}
            name="priority"
            data-ui-target="task_priority_input"
            id="task_priority_input"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </Select>
        </FormRow>

        {isExpanded && (
          <>
            <TextArea
              value={description}
              onChange={(e) => {
                console.log('Description textarea changed:', e.target.value);
                setDescription(e.target.value);
              }}
              placeholder="Description (optional)"
              name="description"
              data-ui-target="task_description_input"
              id="task_description_input"
              autoComplete="off"
            />
          </>
        )}

        <Button
          type="submit"
          disabled={isSubmitting}
          data-ui-target="add_task_button"
          id="add_task_button"
          onClick={(e) => {
            console.log('Add task button clicked');
            // The form's onSubmit handler will be called
          }}
        >
          {isSubmitting ? 'Adding...' : 'Add Task'}
        </Button>
      </Form>
    </FormContainer>
  )
}

export default AddTaskForm
