import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:5001/api'

function Dashboard() {
  const [plexStatus, setPlexStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPlexStatus()
  }, [])

  const fetchPlexStatus = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/plex/status`)
      setPlexStatus(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRestartPlex = async () => {
    if (!window.confirm('Are you sure you want to restart the Plex server?')) {
      return
    }

    try {
      await axios.post(`${API_BASE}/plex/restart`)
      alert('Plex server restart initiated!')
    } catch (err) {
      alert(`Error restarting server: ${err.message}`)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Connecting to Plex</h2>
        <p>{error}</p>
        <button onClick={fetchPlexStatus}>Retry</button>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="cards">
        <div className="card">
          <h3>🖥 Server Status</h3>
          <div className="status-badge success">
            {plexStatus?.status === 'connected' ? '● Online' : '● Offline'}
          </div>
          <p><strong>Server:</strong> {plexStatus?.serverName}</p>
          <p><strong>Version:</strong> {plexStatus?.version}</p>
          <p><strong>Platform:</strong> {plexStatus?.platform}</p>
          <p><strong>URL:</strong> {plexStatus?.url}</p>
        </div>

        <div className="card">
          <h3>⚙️ Quick Actions</h3>
          <button className="btn-primary" onClick={handleRestartPlex}>
            Restart Plex Server
          </button>
          <button className="btn-secondary" onClick={fetchPlexStatus}>
            Refresh Status
          </button>
        </div>

        <div className="card">
          <h3>📊 Overview</h3>
          <p>Welcome to Plex Manager! Use the navigation above to:</p>
          <ul>
            <li><strong>Cleanup:</strong> Remove unwatched movies</li>
            <li><strong>Scanner:</strong> Trigger library scans</li>
            <li><strong>Requests:</strong> Submit media requests</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
