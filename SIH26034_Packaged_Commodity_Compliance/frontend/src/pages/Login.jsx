import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { errorMessage } from '../api'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(errorMessage(err, 'Invalid username or password.'))
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (u, p) => {
    setUsername(u)
    setPassword(p)
    setError('')
  }

  return (
    <div className="login-page">

      {/* Header */}
      <div className="login-header">

        <div className="sih-badge">
          <span className="status-dot">●</span>
          SIH26034
        </div>

        <h1>Packaged Commodity Compliance</h1>

        <p>
          AI-Assisted Legal Metrology Enforcement Portal
        </p>

        <div className="feature-line">
          <span>🔍 AI / OCR</span>
          <span>•</span>
          <span>⚖️ Compliance</span>
          <span>•</span>
          <span>📋 Inspection</span>
        </div>

      </div>


      {/* Login Card */}
      <form
        className="login-card"
        onSubmit={handleSubmit}
      >

        {/* Card heading */}
        <div className="login-title">

          <div className="login-shield">
            🛡️
          </div>

          <div>
            <h2>Officer / Admin Login</h2>
            <p>Secure access for enforcement personnel</p>
          </div>

        </div>


        {/* Error */}
        {error && (
          <div className="login-error">

            <span className="error-icon">⚠️</span>

            <div>
              <strong>Login failed</strong>
              <p>{error}</p>
            </div>

          </div>
        )}


        {/* Username */}
        <div className="login-field">

          <label>Username</label>

          <div className="input-wrapper">

            <span className="input-icon">
              👤
            </span>

            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              autoFocus
              autoComplete="username"
              required
            />

          </div>

        </div>


        {/* Password */}
        <div className="login-field password-field">

          <label>Password</label>

          <div className="input-wrapper">

            <span className="input-icon">
              🔒
            </span>

            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />

            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={
                showPassword
                  ? 'Hide password'
                  : 'Show password'
              }
            >
              {showPassword ? '🙈' : '👁️'}
            </button>

          </div>

        </div>


        {/* Sign In */}
        <button
          type="submit"
          disabled={loading}
          className="login-button"
        >

          {loading ? (
            <>
              <span>⏳</span>
              Signing in...
            </>
          ) : (
            <>
              <span>🔐</span>
              Sign In
            </>
          )}

        </button>


        {/* Demo Accounts */}
        <div className="demo-section">

          <div className="demo-heading">

            <div>
              <h3>DEMO ACCOUNTS</h3>
              <p>Quick access for prototype demonstration</p>
            </div>

            <span className="demo-icon">🧪</span>

          </div>


          <div className="demo-buttons">

            <button
              type="button"
              onClick={() =>
                fillDemo('admin', 'admin123')
              }
              className="demo-button"
            >
              <span>👑</span>
              <span>Admin</span>
            </button>

            <button
              type="button"
              onClick={() =>
                fillDemo('officer1', 'officer123')
              }
              className="demo-button"
            >
              <span>👮</span>
              <span>Officer</span>
            </button>

          </div>

        </div>


        {/* Security note */}
        <div className="security-note">

          <span>🔒</span>

          <p>
            <strong>Authorized personnel only.</strong>
            {' '}
            This portal supports AI-assisted inspection
            and compliance screening.
          </p>

        </div>

      </form>


      {/* Footer */}
      <div className="login-footer">

        <p>
          SIH26034 • Legal Metrology Compliance System
        </p>

        <span>
          AI-assisted screening • Officer verification required
        </span>

      </div>

    </div>
  )
}