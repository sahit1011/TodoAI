import { createContext, useState, useContext, useEffect } from 'react'

// Direct API URL
const API_URL = 'http://localhost:8000';

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    if (token) {
      // Validate token and get user info
      fetchUserInfo(token)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUserInfo = async (token) => {
    try {
      console.log('Fetching user info with token:', token ? token.substring(0, 20) + '...' : 'null');

      if (!token) {
        throw new Error('No token provided');
      }

      // This would be a real endpoint in a production app
      // For now, we'll just decode the JWT to get the username
      const payload = JSON.parse(atob(token.split('.')[1]))
      console.log('Decoded token payload:', payload);

      // Check if token is expired
      const currentTime = Math.floor(Date.now() / 1000);
      if (payload.exp && payload.exp < currentTime) {
        console.error('Token expired');
        throw new Error('Token expired');
      }

      setUser({ username: payload.sub })
      console.log('User set:', payload.sub);

      setIsAuthenticated(true)
      console.log('Authentication state set to true');
    } catch (error) {
      console.error('Error fetching user info:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      console.log('Attempting login for:', username);

      // Normal login flow - using direct API call with form-encoded data
      console.log('Sending login request to:', `${API_URL}/api/auth/token`);
      console.log('With credentials:', { username, password });

      const response = await fetch(`${API_URL}/api/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
      })

      console.log('Login response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Login error response:', errorText);
        throw new Error('Login failed')
      }

      const data = await response.json()
      console.log('Login successful, token:', data.access_token);

      localStorage.setItem('token', data.access_token)
      console.log('Token saved to localStorage');

      // Get user info
      await fetchUserInfo(data.access_token)

      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      return { success: true }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
