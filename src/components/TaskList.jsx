import { useState } from 'react'
import styled from 'styled-components'

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
  align-items: center;
  
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
    text-decoration: line-through;
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
  gap: 0.5rem;
`

const ActionButton = styled.button`
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  background-color: ${props => props.color || 'var(--light-gray)'};
  color: ${props => props.textColor || 'var(--text-color)'};
  
  &:hover {
    opacity: 0.9;
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

function TaskList({ tasks, onTaskUpdate }) {
  const [filter, setFilter] = useState('all')
  
  const handleStatusChange = async (taskId, newStatus) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: newStatus })
      })
      
      if (response.ok) {
        onTaskUpdate()
      }
    } catch (error) {
      console.error('Error updating task status:', error)
    }
  }
  
  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true
    if (filter === 'active') return task.status !== 'done'
    if (filter === 'completed') return task.status === 'done'
    return task.status === filter
  })
  
  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }
  
  return (
    <div>
      <FilterContainer>
        <FilterButton 
          active={filter === 'all'} 
          onClick={() => setFilter('all')}
        >
          All
        </FilterButton>
        <FilterButton 
          active={filter === 'active'} 
          onClick={() => setFilter('active')}
        >
          Active
        </FilterButton>
        <FilterButton 
          active={filter === 'completed'} 
          onClick={() => setFilter('completed')}
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
              className={`${task.priority} ${task.status === 'done' ? 'done' : ''}`}
            >
              <div>
                <TaskTitle>{task.title}</TaskTitle>
                <TaskDetails>
                  {task.due_date && `Due: ${formatDate(task.due_date)} • `}
                  Priority: {task.priority}
                </TaskDetails>
              </div>
              <TaskActions>
                {task.status !== 'done' ? (
                  <ActionButton 
                    color="#28a745" 
                    textColor="white"
                    onClick={() => handleStatusChange(task.id, 'done')}
                  >
                    Complete
                  </ActionButton>
                ) : (
                  <ActionButton 
                    onClick={() => handleStatusChange(task.id, 'todo')}
                  >
                    Reopen
                  </ActionButton>
                )}
              </TaskActions>
            </TaskItem>
          ))
        )}
      </TaskContainer>
    </div>
  )
}

export default TaskList
