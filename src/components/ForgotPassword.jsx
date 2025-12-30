import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../config';
import '../styles/Auth.css';

export default function ForgotPassword() {
  const [username, setUsername] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/auth/request-reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        // In development, show the reset token
        if (data.reset_token) {
          setResetToken(data.reset_token);
        }
      } else {
        setError(data.error || 'Failed to request password reset');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Reset Password</h1>
          <p>Enter your username to reset your password</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              disabled={loading || !!resetToken}
            />
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          {message && (
            <div className="alert alert-success">
              {message}
            </div>
          )}

          {resetToken && (
            <div className="alert alert-info">
              <p><strong>Reset Token Generated!</strong></p>
              <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                Copy this token and use it to reset your password:
              </p>
              <code style={{
                display: 'block',
                background: 'rgba(0,0,0,0.1)',
                padding: '0.5rem',
                marginTop: '0.5rem',
                borderRadius: '4px',
                wordBreak: 'break-all',
                fontSize: '0.75rem'
              }}>
                {resetToken}
              </code>
              <button
                type="button"
                onClick={() => navigate(`/reset-password?token=${resetToken}`)}
                className="btn btn-primary"
                style={{ marginTop: '1rem', width: '100%' }}
              >
                Continue to Reset Password
              </button>
            </div>
          )}

          {!resetToken && (
            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? 'Requesting...' : 'Request Reset'}
            </button>
          )}
        </form>

        <div className="auth-footer">
          <p>
            Remember your password?{' '}
            <a href="/login" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>
              Back to Login
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
