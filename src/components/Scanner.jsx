import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

function Scanner() {
  const [libraries, setLibraries] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)

  useEffect(() => {
    fetchLibraries()
  }, [])

  const fetchLibraries = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/plex/libraries`)
      setLibraries(response.data.libraries)
    } catch (err) {
      alert(`Error fetching libraries: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const scanLibrary = async (libraryKey, libraryName) => {
    try {
      setScanning(true)
      await axios.post(`${API_BASE}/plex/scan`, { libraryKey })
      alert(`Scan initiated for "${libraryName}"`)
    } catch (err) {
      alert(`Error scanning library: ${err.message}`)
    } finally {
      setScanning(false)
    }
  }

  const scanAll = async () => {
    try {
      setScanning(true)
      await axios.post(`${API_BASE}/plex/scan`, {})
      alert('Scan initiated for all libraries')
    } catch (err) {
      alert(`Error scanning libraries: ${err.message}`)
    } finally {
      setScanning(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading libraries...</div>
  }

  return (
    <div className="scanner">
      <h1>Library Scanner</h1>

      <div className="actions">
        <button
          className="btn-primary"
          onClick={scanAll}
          disabled={scanning}
        >
          {scanning ? 'Scanning...' : 'Scan All Libraries'}
        </button>
        <button className="btn-secondary" onClick={fetchLibraries}>
          Refresh List
        </button>
      </div>

      <div className="library-list">
        <h2>Available Libraries</h2>
        {libraries.length === 0 && (
          <p>No libraries found.</p>
        )}

        {libraries.map((library) => (
          <div key={library.key} className="library-card">
            <div className="library-info">
              <h3>{library.title}</h3>
              <p>
                <span className="badge">{library.type}</span>
                <span className="count">{library.count} items</span>
              </p>
            </div>
            <button
              className="btn-secondary"
              onClick={() => scanLibrary(library.key, library.title)}
              disabled={scanning}
            >
              Scan
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Scanner
