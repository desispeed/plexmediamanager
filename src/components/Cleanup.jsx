import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:5001/api'

function Cleanup() {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedMovies, setSelectedMovies] = useState(new Set())
  const [maxViews, setMaxViews] = useState(1)
  const [days, setDays] = useState(30)
  const [totalCount, setTotalCount] = useState(0)
  const [totalSize, setTotalSize] = useState(0)

  const fetchMovies = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/plex/movies`, {
        params: { max_views: maxViews, days }
      })
      setMovies(response.data.movies)
      setTotalCount(response.data.totalCount)
      setTotalSize(response.data.totalSizeGB)
      setSelectedMovies(new Set())
    } catch (err) {
      alert(`Error fetching movies: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const toggleMovie = (index) => {
    const newSelected = new Set(selectedMovies)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedMovies(newSelected)
  }

  const toggleAll = () => {
    if (selectedMovies.size === movies.length) {
      setSelectedMovies(new Set())
    } else {
      setSelectedMovies(new Set(movies.map((_, i) => i)))
    }
  }

  const getSelectedSize = () => {
    let size = 0
    selectedMovies.forEach(index => {
      size += movies[index].fileSizeMB
    })
    return (size / 1024).toFixed(2)
  }

  const handleDelete = async () => {
    if (selectedMovies.size === 0) {
      alert('No movies selected')
      return
    }

    const selectedSize = getSelectedSize()
    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedMovies.size} movies (${selectedSize} GB)?\n\nThis cannot be undone!`
    )

    if (!confirmed) return

    const finalConfirm = window.prompt(
      'Type "DELETE" to confirm deletion:'
    )

    if (finalConfirm !== 'DELETE') {
      alert('Deletion cancelled')
      return
    }

    // Get movie keys for selected movies
    const movieKeys = Array.from(selectedMovies).map(index => movies[index].movieKey)

    try {
      setLoading(true)
      const response = await axios.post(`${API_BASE}/plex/movies/delete`, {
        movieKeys
      })

      const result = response.data

      let message = `✅ Deletion Complete!\n\n`
      message += `✓ Successfully deleted: ${result.deletedCount} movies\n`
      message += `💾 Space freed: ${result.deletedSizeGB} GB\n`

      if (result.failedCount > 0) {
        message += `\n❌ Failed to delete: ${result.failedCount} movies\n`
        if (result.errors && result.errors.length > 0) {
          message += `\nErrors:\n${result.errors.join('\n')}`
        }
      }

      alert(message)

      // Refresh the movie list
      fetchMovies()

    } catch (err) {
      alert(`❌ Error during deletion: ${err.response?.data?.error || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cleanup">
      <h1>Media Cleanup</h1>

      <div className="filters">
        <div className="filter-group">
          <label>Max Views:</label>
          <input
            type="number"
            value={maxViews}
            onChange={(e) => setMaxViews(parseInt(e.target.value))}
            min="0"
            max="10"
          />
        </div>

        <div className="filter-group">
          <label>Not Watched in (days):</label>
          <input
            type="number"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            min="1"
            max="365"
          />
        </div>

        <button className="btn-primary" onClick={fetchMovies} disabled={loading}>
          {loading ? 'Loading...' : 'Search Movies'}
        </button>
      </div>

      {movies.length > 0 && (
        <>
          <div className="summary">
            <p><strong>Total Found:</strong> {totalCount} movies ({totalSize} GB)</p>
            <p><strong>Selected:</strong> {selectedMovies.size} movies ({getSelectedSize()} GB)</p>
          </div>

          <div className="actions">
            <button className="btn-secondary" onClick={toggleAll}>
              {selectedMovies.size === movies.length ? 'Deselect All' : 'Select All'}
            </button>
            <button
              className="btn-danger"
              onClick={handleDelete}
              disabled={selectedMovies.size === 0}
            >
              Delete Selected
            </button>
          </div>

          <div className="movie-list">
            <table>
              <thead>
                <tr>
                  <th>Select</th>
                  <th>Title</th>
                  <th>Year</th>
                  <th>Views</th>
                  <th>Size (GB)</th>
                  <th>Last Watched</th>
                  <th>Added</th>
                </tr>
              </thead>
              <tbody>
                {movies.map((movie, index) => (
                  <tr key={index} className={selectedMovies.has(index) ? 'selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedMovies.has(index)}
                        onChange={() => toggleMovie(index)}
                      />
                    </td>
                    <td><strong>{movie.title}</strong></td>
                    <td>{movie.year || 'N/A'}</td>
                    <td>{movie.viewCount}</td>
                    <td>{(movie.fileSizeMB / 1024).toFixed(2)}</td>
                    <td>{movie.lastViewed}</td>
                    <td>{movie.addedDate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!loading && movies.length === 0 && (
        <div className="empty-state">
          <p>Click "Search Movies" to find movies matching your criteria.</p>
        </div>
      )}
    </div>
  )
}

export default Cleanup
