import fetch from 'node-fetch';

async function testTasks() {
  try {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

    console.log('Fetching tasks...');
    const response = await fetch('http://localhost:8000/api/tasks', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('Response status:', response.status);

    if (response.ok) {
      const data = await response.json();
      console.log('Tasks data:', JSON.stringify(data, null, 2));
    } else {
      const errorText = await response.text();
      console.error('Error response:', errorText);
    }
  } catch (error) {
    console.error('Error fetching tasks:', error);
  }
}

testTasks();
