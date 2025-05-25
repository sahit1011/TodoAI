import { useState } from 'react'
import styled from 'styled-components'
import { useAuth } from '../context/AuthContext'

const Form = styled.form`
  display: flex;
  flex-direction: column;
`

const ErrorMessage = styled.div`
  color: red;
  margin-bottom: 1rem;
`

const SubmitButton = styled.button`
  background-color: var(--primary-color);
  color: white;
  padding: 0.5rem;
  
  &:hover {
    background-color: var(--secondary-color);
  }
`

function LoginForm() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!username || !password) {
      setError('Please enter both username and password')
      setLoading(false)
      return
    }

    const result = await login(username, password)
    
    if (!result.success) {
      setError(result.error || 'Invalid username or password')
    }
    
    setLoading(false)
  }

  return (
    <div>
      <h2>Login</h2>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      <Form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>
        <SubmitButton type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </SubmitButton>
      </Form>
    </div>
  )
}

export default LoginForm
