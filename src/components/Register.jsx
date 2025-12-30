import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/Auth.css'

export default function Register() {
  const [step, setStep] = useState(1) // 1: credentials, 2: QR code, 3: verify
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [totpSecret, setTotpSecret] = useState('')
  const [verificationToken, setVerificationToken] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { register, verifyTotp } = useAuth()
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    try {
      const result = await register(username, password)

      if (result.success) {
        setQrCode(result.qrCode)
        setTotpSecret(result.totpSecret)
        setStep(2)
      } else if (result.error) {
        setError(result.error)
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await verifyTotp(username, verificationToken)

      if (result.success) {
        setStep(3)
        setTimeout(() => navigate('/login'), 2000)
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
          <h2>Create Account</h2>
        </div>

        {step === 1 && (
          <form onSubmit={handleRegister} className="auth-form">
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
                autoComplete="new-password"
                minLength="8"
              />
              <small>At least 8 characters</small>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Continue'}
            </button>
          </form>
        )}

        {step === 2 && (
          <div className="mfa-setup">
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <div className="setup-instructions">
              <h3>Set Up Two-Factor Authentication</h3>
              <ol>
                <li>Install Microsoft Authenticator or Google Authenticator on your phone</li>
                <li>Scan this QR code with your authenticator app</li>
                <li>Enter the 6-digit code to verify</li>
              </ol>
            </div>

            <div className="qr-code-container">
              {qrCode && <img src={qrCode} alt="QR Code" className="qr-code" />}
            </div>

            <div className="totp-secret">
              <p>Or enter this code manually:</p>
              <code>{totpSecret}</code>
            </div>

            <form onSubmit={handleVerify} className="auth-form">
              <div className="form-group">
                <label htmlFor="verificationToken">Verification Code</label>
                <input
                  id="verificationToken"
                  type="text"
                  value={verificationToken}
                  onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  required
                  maxLength="6"
                  pattern="[0-9]{6}"
                  className="mfa-input"
                  autoFocus
                />
              </div>

              <button
                type="submit"
                className="auth-button"
                disabled={loading || verificationToken.length !== 6}
              >
                {loading ? 'Verifying...' : 'Verify & Complete'}
              </button>
            </form>
          </div>
        )}

        {step === 3 && (
          <div className="success-message">
            <div className="success-icon">✓</div>
            <h3>Account Created!</h3>
            <p>Redirecting to login...</p>
          </div>
        )}

        {step === 1 && (
          <div className="auth-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
