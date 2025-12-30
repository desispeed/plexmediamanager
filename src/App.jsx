import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Cleanup from './components/Cleanup'
import Scanner from './components/Scanner'
import Requests from './components/Requests'
import Login from './components/Login'
import Register from './components/Register'
import ForgotPassword from './components/ForgotPassword'
import ResetPassword from './components/ResetPassword'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { useDeviceMode } from './hooks/useDeviceMode'
import './App.css'

function Navigation() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { mode, toggleMode, isMobile } = useDeviceMode()
  const { user, logout } = useAuth()

  const isActive = (path) => location.pathname === path

  const handleLinkClick = () => {
    setMobileMenuOpen(false)
  }

  const handleLogout = () => {
    logout()
    setMobileMenuOpen(false)
  }

  // Don't show navigation on auth pages
  const authPages = ['/login', '/register', '/forgot-password', '/reset-password'];
  if (authPages.includes(location.pathname)) {
    return null
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <h1>🎬 Plex Manager</h1>
        <span className="mode-indicator">{isMobile ? '📱' : '🖥️'}</span>
      </div>
      <button
        className="mobile-menu-toggle"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? '✕' : '☰'}
      </button>
      <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <Link to="/dashboard" className={isActive('/dashboard') ? 'active' : ''} onClick={handleLinkClick}>
          Dashboard
        </Link>
        <Link to="/cleanup" className={isActive('/cleanup') ? 'active' : ''} onClick={handleLinkClick}>
          Cleanup
        </Link>
        <Link to="/scanner" className={isActive('/scanner') ? 'active' : ''} onClick={handleLinkClick}>
          Scanner
        </Link>
        <Link to="/requests" className={isActive('/requests') ? 'active' : ''} onClick={handleLinkClick}>
          Requests
        </Link>
        <button className="mode-toggle-btn" onClick={toggleMode} title={`Switch to ${isMobile ? 'Desktop' : 'Mobile'} Mode`}>
          {isMobile ? '🖥️ Desktop' : '📱 Mobile'}
        </button>
        {user && (
          <div className="user-section">
            <span className="username">{user.username}</span>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Navigation />
          <main className="main-content">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              {/* Protected routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/cleanup" element={
                <ProtectedRoute>
                  <Cleanup />
                </ProtectedRoute>
              } />
              <Route path="/scanner" element={
                <ProtectedRoute>
                  <Scanner />
                </ProtectedRoute>
              } />
              <Route path="/requests" element={
                <ProtectedRoute>
                  <Requests />
                </ProtectedRoute>
              } />

              {/* Redirect root to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App
// Force rebuild Tue Dec 30 13:27:52 CST 2025
