import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('authToken'))
  const [loading, setLoading] = useState(true)

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5001/api'

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const response = await axios.get(`${API_BASE}/auth/verify`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (response.data.valid) {
          setUser({ username: response.data.username })
        } else {
          logout()
        }
      } catch (error) {
        console.error('Token verification failed:', error)
        logout()
      } finally {
        setLoading(false)
      }
    }

    verifyToken()
  }, [token])

  const login = async (username, password, mfaToken) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        username,
        password,
        token: mfaToken
      })

      if (response.data.status === 'mfa_required') {
        return { mfaRequired: true }
      }

      if (response.data.status === 'success') {
        const newToken = response.data.token
        setToken(newToken)
        setUser({ username: response.data.username })
        localStorage.setItem('authToken', newToken)
        return { success: true }
      }

      return { error: 'Login failed' }
    } catch (error) {
      return {
        error: error.response?.data?.error || 'Login failed. Please try again.'
      }
    }
  }

  const register = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, {
        username,
        password
      })

      if (response.status === 201) {
        return {
          success: true,
          totpSecret: response.data.totp_secret,
          qrCode: response.data.qr_code,
          username
        }
      }

      return { error: 'Registration failed' }
    } catch (error) {
      return {
        error: error.response?.data?.error || 'Registration failed. Please try again.'
      }
    }
  }

  const verifyTotp = async (username, token) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/verify-totp`, {
        username,
        token
      })

      if (response.data.status === 'success') {
        return { success: true }
      }

      return { error: 'Invalid token' }
    } catch (error) {
      return {
        error: error.response?.data?.error || 'Verification failed. Please try again.'
      }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('authToken')
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    verifyTotp,
    logout,
    isAuthenticated: !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
