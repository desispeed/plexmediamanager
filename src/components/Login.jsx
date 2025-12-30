import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/Auth.css'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [mfaToken, setMfaToken] = useState('')
  const [showMfa, setShowMfa] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await login(username, password, mfaToken || null)

      if (result.success) {
        navigate('/dashboard')
      } else if (result.mfaRequired) {
        setShowMfa(true)
        setError('')
      } else if (result.error) {
        setError(result.error)
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Plex Manager</h1>
          <h2>Sign In</h2>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              disabled={showMfa}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={showMfa}
            />
          </div>

          {showMfa && (
            <div className="form-group mfa-group">
              <label htmlFor="mfaToken">
                Authenticator Code
                <span className="mfa-hint">Enter the 6-digit code from your authenticator app</span>
              </label>
              <input
                id="mfaToken"
                type="text"
                value={mfaToken}
                onChange={(e) => setMfaToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                required
                autoComplete="one-time-code"
                maxLength="6"
                pattern="[0-9]{6}"
                className="mfa-input"
                autoFocus
              />
            </div>
          )}

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : (showMfa ? 'Verify & Sign In' : 'Sign In')}
          </button>

          {showMfa && (
            <button
              type="button"
              onClick={() => {
                setShowMfa(false)
                setMfaToken('')
                setError('')
              }}
              className="back-button"
            >
              Back
            </button>
          )}
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
