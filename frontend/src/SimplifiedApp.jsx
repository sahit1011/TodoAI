import { useState, useEffect } from 'react'
import styled from 'styled-components'

// Hardcoded token that we know works
const HARDCODED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

const AppContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
`

const Header = styled.header`
  background-color: #4a6fa5;
  color: white;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 20px;
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
  
  border-left: 4px solid ${props => 
    props.priority === 'high' ? '#dc3545' : 
    props.priority === 'medium' ? '#ffc107' : 
    props.priority === 'low' ? '#28a745' : 
    props.priority === 'urgent' ? '#dc3545' : '#ced4da'};
  
  ${props => props.status === 'done' && `
    opacity: 0.7;
    text-decoration: line-through;
  `}
`

const Button = styled.button`
  background-color: #4a6fa5;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  
  &:hover {
    background-color: #3a5a8a;
  }
  
  &:disabled {
    background-color: #ced4da;
    cursor: not-allowed;
  }
`

function SimplifiedApp() {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  
  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);
  
  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log('Fetching tasks with hardcoded token...');
      
      const response = await fetch('/api/tasks', {
        headers: {
          'Authorization': `Bearer ${HARDCODED_TOKEN}`
        }
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Tasks data:', data);
        setTasks(Array.isArray(data) ? data : []);
      } else {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        setError(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setError(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleStatusChange = async (taskId, newStatus) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${HARDCODED_TOKEN}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (response.ok) {
        fetchTasks();
      } else {
        const errorText = await response.text();
        console.error('Error updating task status:', errorText);
        alert(`Failed to update task status: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error updating task status:', error);
      alert(`Error: ${error.message}`);
    }
  };
  
  const handleCreateTask = async (e) => {
    e.preventDefault();
    
    if (!newTaskTitle.trim()) {
      alert('Please enter a task title');
      return;
    }
    
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${HARDCODED_TOKEN}`
        },
        body: JSON.stringify({
          title: newTaskTitle,
          priority: 'medium'
        })
      });
      
      if (response.ok) {
        setNewTaskTitle('');
        fetchTasks();
      } else {
        const errorText = await response.text();
        console.error('Error creating task:', errorText);
        alert(`Failed to create task: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error creating task:', error);
      alert(`Error: ${error.message}`);
    }
  };
  
  return (
    <AppContainer>
      <Header>
        <h1>Todo AI - Simplified Version</h1>
        <p>Using hardcoded token for authentication</p>
      </Header>
      
      <div>
        <h2>Create New Task</h2>
        <form onSubmit={handleCreateTask} style={{ display: 'flex', marginBottom: '20px' }}>
          <input
            type="text"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            placeholder="Enter task title"
            style={{ flex: 1, padding: '8px', marginRight: '10px' }}
          />
          <Button type="submit">Add Task</Button>
        </form>
      </div>
      
      <div>
        <h2>Your Tasks</h2>
        {isLoading ? (
          <p>Loading tasks...</p>
        ) : error ? (
          <div style={{ color: 'red', padding: '10px', backgroundColor: '#ffeeee', borderRadius: '4px' }}>
            {error}
            <Button 
              onClick={fetchTasks} 
              style={{ marginLeft: '10px' }}
            >
              Retry
            </Button>
          </div>
        ) : tasks.length === 0 ? (
          <p>No tasks found.</p>
        ) : (
          <div>
            {tasks.map(task => (
              <TaskItem 
                key={task.id} 
                priority={task.priority}
                status={task.status}
              >
                <div>
                  <h3 style={{ margin: '0' }}>{task.title}</h3>
                  <p style={{ margin: '5px 0 0 0', color: '#6c757d', fontSize: '0.9em' }}>
                    {task.description || 'No description'}
                  </p>
                  <div style={{ fontSize: '0.8em', marginTop: '5px' }}>
                    Priority: {task.priority} • Status: {task.status}
                  </div>
                </div>
                <div>
                  {task.status !== 'done' ? (
                    <Button 
                      onClick={() => handleStatusChange(task.id, 'done')}
                      style={{ backgroundColor: '#28a745' }}
                    >
                      Complete
                    </Button>
                  ) : (
                    <Button 
                      onClick={() => handleStatusChange(task.id, 'todo')}
                    >
                      Reopen
                    </Button>
                  )}
                </div>
              </TaskItem>
            ))}
          </div>
        )}
      </div>
      
      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
        <h3>Debug Information</h3>
        <p>Token: {HARDCODED_TOKEN.substring(0, 20)}...</p>
        <p>Tasks Count: {tasks.length}</p>
        <Button onClick={fetchTasks}>Refresh Tasks</Button>
      </div>
    </AppContainer>
  );
}

export default SimplifiedApp;
