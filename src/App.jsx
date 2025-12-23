import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Cleanup from './components/Cleanup'
import Scanner from './components/Scanner'
import Requests from './components/Requests'
import './App.css'

function Navigation() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path) => location.pathname === path

  const handleLinkClick = () => {
    setMobileMenuOpen(false)
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <h1>🎬 Plex Manager</h1>
      </div>
      <button
        className="mobile-menu-toggle"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? '✕' : '☰'}
      </button>
      <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <Link to="/" className={isActive('/') ? 'active' : ''} onClick={handleLinkClick}>
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
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cleanup" element={<Cleanup />} />
            <Route path="/scanner" element={<Scanner />} />
            <Route path="/requests" element={<Requests />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
