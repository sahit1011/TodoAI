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

const SuccessMessage = styled.div`
  color: green;
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

function RegisterForm() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    // Validation
    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields')
      setLoading(false)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address')
      setLoading(false)
      return
    }

    const result = await register(username, email, password)
    
    if (result.success) {
      setSuccess('Registration successful! You can now log in.')
      setUsername('')
      setEmail('')
      setPassword('')
      setConfirmPassword('')
    } else {
      setError(result.error || 'Registration failed')
    }
    
    setLoading(false)
  }

  return (
    <div>
      <h2>Register</h2>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}
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
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
        <div>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={loading}
          />
        </div>
        <SubmitButton type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </SubmitButton>
      </Form>
    </div>
  )
}

export default RegisterForm
