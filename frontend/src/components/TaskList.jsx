import { useState } from 'react'
import styled from 'styled-components'

// Direct API URL
const API_URL = 'http://localhost:8000'

const TaskContainer = styled.div`
  margin-top: 1rem;
`

const TaskItem = styled.div`
  background-color: white;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  &.high {
    border-left: 4px solid #dc3545;
  }

  &.medium {
    border-left: 4px solid #ffc107;
  }

  &.low {
    border-left: 4px solid #28a745;
  }

  &.urgent {
    border-left: 4px solid #dc3545;
    background-color: #fff8f8;
  }

  &.done {
    opacity: 0.7;
  }

  &.editing {
    border: 1px solid var(--primary-color);
    box-shadow: 0 0 5px rgba(74, 111, 165, 0.3);
  }
`

const TaskTitle = styled.h3`
  margin: 0;
  font-size: 1rem;
`

const TaskDetails = styled.div`
  font-size: 0.8rem;
  color: var(--dark-gray);
  margin-top: 0.25rem;
`

const TaskActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
`

const ActionButton = styled.button`
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  background-color: ${props => props.color || 'var(--light-gray)'};
  color: ${props => props.textColor || 'var(--text-color)'};
  margin-left: 5px;

  &:hover {
    opacity: 0.9;
  }
`

const EditForm = styled.div`
  margin-top: 10px;
  padding: 10px;
  background-color: var(--light-gray);
  border-radius: 4px;
`

const EditInput = styled.input`
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const EditTextarea = styled.textarea`
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;
  resize: vertical;
  min-height: 60px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const EditSelect = styled.select`
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const FilterContainer = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
`

const FilterButton = styled.button`
  background-color: ${props => props.active ? 'var(--primary-color)' : 'var(--light-gray)'};
  color: ${props => props.active ? 'white' : 'var(--text-color)'};
`

function TaskList({ tasks = [], onTaskUpdate }) {
  console.log('TaskList component rendered with tasks:', tasks);

  const [filter, setFilter] = useState('all')
  const [editingTask, setEditingTask] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editPriority, setEditPriority] = useState('medium')

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      console.log(`Changing task ${taskId} status to ${newStatus}`);

      // Get token from localStorage or use hardcoded token
      const token = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

      // First, let's try to get the task to see its current status
      const getResponse = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!getResponse.ok) {
        const errorText = await getResponse.text();
        console.error('Error getting task:', errorText);
        alert(`Failed to get task: ${getResponse.status} ${getResponse.statusText}`);
        return;
      }

      const task = await getResponse.json();
      console.log('Current task status:', task.status);

      const response = await fetch(`${API_URL}/api/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      })

      console.log(`Status change response: ${response.status}`);

      if (response.ok) {
        console.log('Status updated successfully');
        onTaskUpdate();
      } else {
        const errorText = await response.text();
        console.error('Error updating task status:', errorText);
        alert(`Failed to update task status: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error updating task status:', error);
      alert(`Error: ${error.message}`);
    }
  }

  // Make sure tasks is an array and filter them
  console.log('Filtering tasks with filter:', filter);

  const filteredTasks = tasks.filter(task => {
    console.log(`Filtering task: ${task.title}, status: ${task.status}`);
    if (filter === 'all') return true
    if (filter === 'active') return task.status === 'todo' || task.status === 'in_progress'
    if (filter === 'completed') {
      console.log(`Checking if task ${task.title} is completed: ${task.status === 'done'}`);
      return task.status === 'done'
    }
    return task.status === filter
  })

  console.log('Filtered tasks:', filteredTasks);

  const handleEditClick = (task) => {
    setEditingTask(task.id)
    setEditTitle(task.title)
    setEditDescription(task.description || '')
    setEditPriority(task.priority)
  }

  const handleCancelEdit = () => {
    setEditingTask(null)
    setEditTitle('')
    setEditDescription('')
    setEditPriority('medium')
  }

  const handleSaveEdit = async (taskId) => {
    try {
      // Get token from localStorage or use hardcoded token
      const token = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

      const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: editTitle,
          description: editDescription || undefined,
          priority: editPriority
        })
      })

      if (response.ok) {
        setEditingTask(null)
        onTaskUpdate()
      } else {
        const errorText = await response.text()
        console.error('Error updating task:', errorText)
        alert(`Failed to update task: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error updating task:', error)
      alert(`Error: ${error.message}`)
    }
  }

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return
    }

    try {
      // Get token from localStorage or use hardcoded token
      const token = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

      const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        onTaskUpdate()
      } else {
        const errorText = await response.text()
        console.error('Error deleting task:', errorText)
        alert(`Failed to delete task: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error deleting task:', error)
      alert(`Error: ${error.message}`)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }

  return (
    <div>
      <FilterContainer data-ui-target="task_section">
        <FilterButton
          active={filter === 'all'}
          onClick={() => setFilter('all')}
          data-ui-target="all_tasks_filter"
        >
          All
        </FilterButton>
        <FilterButton
          active={filter === 'active'}
          onClick={() => setFilter('active')}
          data-ui-target="active_tasks_filter"
        >
          Active
        </FilterButton>
        <FilterButton
          active={filter === 'completed'}
          onClick={() => setFilter('completed')}
          data-ui-target="completed_tasks_filter"
        >
          Completed
        </FilterButton>
      </FilterContainer>

      <TaskContainer>
        {filteredTasks.length === 0 ? (
          <p>No tasks found.</p>
        ) : (
          filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              className={`${task.priority} ${task.status === 'done' ? 'done' : ''} ${editingTask === task.id ? 'editing' : ''}`}
            >
              <div style={{ width: '100%' }}>
                {editingTask === task.id ? (
                  <EditForm data-ui-target={`edit_task_form_${task.id}`}>
                    <EditInput
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      placeholder="Task title"
                      name="title"
                      data-ui-target={`task_title_input_${task.id}`}
                    />
                    <EditTextarea
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      placeholder="Description (optional)"
                      name="description"
                      data-ui-target={`task_description_input_${task.id}`}
                    />
                    <EditSelect
                      value={editPriority}
                      onChange={(e) => setEditPriority(e.target.value)}
                      name="priority"
                      data-ui-target={`task_priority_input_${task.id}`}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </EditSelect>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                      <ActionButton
                        onClick={handleCancelEdit}
                        data-ui-target={`cancel_edit_button_${task.id}`}
                      >
                        Cancel
                      </ActionButton>
                      <ActionButton
                        color="#28a745"
                        textColor="white"
                        onClick={() => handleSaveEdit(task.id)}
                        data-ui-target={`save_task_button_${task.id}`}
                      >
                        Save
                      </ActionButton>
                    </div>
                  </EditForm>
                ) : (
                  <>
                    <TaskTitle style={{ textDecoration: task.status === 'done' ? 'line-through' : 'none' }}>
                      {task.title}
                    </TaskTitle>
                    {task.description && (
                      <TaskDetails style={{ margin: '5px 0', textDecoration: task.status === 'done' ? 'line-through' : 'none' }}>
                        {task.description}
                      </TaskDetails>
                    )}
                    <TaskDetails>
                      {task.due_date && `Due: ${formatDate(task.due_date)} • `}
                      Priority: {task.priority} • Status: {task.status}
                    </TaskDetails>
                    <TaskActions>
                      {task.status !== 'done' ? (
                        <ActionButton
                          color="#28a745"
                          textColor="white"
                          onClick={() => handleStatusChange(task.id, 'done')}
                          data-ui-target={`complete_task_button_${task.id}`}
                        >
                          Complete
                        </ActionButton>
                      ) : (
                        <ActionButton
                          onClick={() => handleStatusChange(task.id, 'todo')}
                          data-ui-target={`reopen_task_button_${task.id}`}
                        >
                          Reopen
                        </ActionButton>
                      )}
                      <ActionButton
                        color="#007bff"
                        textColor="white"
                        onClick={() => handleEditClick(task)}
                        data-ui-target={`edit_task_button_${task.id}`}
                      >
                        Edit
                      </ActionButton>
                      <ActionButton
                        color="#dc3545"
                        textColor="white"
                        onClick={() => handleDeleteTask(task.id)}
                        data-ui-target={`delete_task_button_${task.id}`}
                      >
                        Delete
                      </ActionButton>
                    </TaskActions>
                  </>
                )}
              </div>
            </TaskItem>
          ))
        )}
      </TaskContainer>
    </div>
  )
}

export default TaskList
