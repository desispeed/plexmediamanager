import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:5001/api'

function Requests() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    type: 'movie',
    year: '',
    requestedBy: '',
    notes: ''
  })

  useEffect(() => {
    fetchRequests()
  }, [])

  const fetchRequests = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/requests`)
      setRequests(response.data.requests)
    } catch (err) {
      alert(`Error fetching requests: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const requestData = {
        ...formData,
        requestedAt: new Date().toISOString()
      }

      await axios.post(`${API_BASE}/requests`, requestData)
      alert('Request submitted successfully!')

      // Reset form
      setFormData({
        title: '',
        type: 'movie',
        year: '',
        requestedBy: '',
        notes: ''
      })
      setShowForm(false)
      fetchRequests()
    } catch (err) {
      alert(`Error submitting request: ${err.message}`)
    }
  }

  const updateRequestStatus = async (requestId, newStatus) => {
    try {
      await axios.patch(`${API_BASE}/requests/${requestId}`, { status: newStatus })
      fetchRequests()
    } catch (err) {
      alert(`Error updating request: ${err.message}`)
    }
  }

  const getStatusBadge = (status) => {
    const classes = {
      pending: 'badge-pending',
      approved: 'badge-success',
      rejected: 'badge-danger',
      completed: 'badge-success'
    }
    return <span className={`badge ${classes[status]}`}>{status}</span>
  }

  return (
    <div className="requests">
      <h1>Media Requests</h1>

      <div className="actions">
        <button
          className="btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'New Request'}
        </button>
        <button className="btn-secondary" onClick={fetchRequests}>
          Refresh
        </button>
      </div>

      {showForm && (
        <div className="request-form">
          <h2>Submit New Request</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <option value="movie">Movie</option>
                <option value="tv">TV Show</option>
              </select>
            </div>

            <div className="form-group">
              <label>Year</label>
              <input
                type="number"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                min="1900"
                max="2030"
              />
            </div>

            <div className="form-group">
              <label>Your Name</label>
              <input
                type="text"
                value={formData.requestedBy}
                onChange={(e) => setFormData({ ...formData, requestedBy: e.target.value })}
                placeholder="Optional"
              />
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Any additional information..."
                rows="3"
              />
            </div>

            <button type="submit" className="btn-primary">
              Submit Request
            </button>
          </form>
        </div>
      )}

      <div className="request-list">
        <h2>All Requests ({requests.length})</h2>

        {loading && <p>Loading requests...</p>}

        {!loading && requests.length === 0 && (
          <p className="empty-state">No requests yet. Submit your first request!</p>
        )}

        {requests.map((request) => (
          <div key={request.id} className="request-card">
            <div className="request-header">
              <h3>{request.title} ({request.year})</h3>
              {getStatusBadge(request.status)}
            </div>
            <div className="request-details">
              <p><strong>Type:</strong> {request.type}</p>
              <p><strong>Requested by:</strong> {request.requestedBy || 'Anonymous'}</p>
              {request.notes && <p><strong>Notes:</strong> {request.notes}</p>}
            </div>
            <div className="request-actions">
              <button
                className="btn-success"
                onClick={() => updateRequestStatus(request.id, 'approved')}
                disabled={request.status === 'approved'}
              >
                Approve
              </button>
              <button
                className="btn-danger"
                onClick={() => updateRequestStatus(request.id, 'rejected')}
                disabled={request.status === 'rejected'}
              >
                Reject
              </button>
              <button
                className="btn-secondary"
                onClick={() => updateRequestStatus(request.id, 'completed')}
                disabled={request.status === 'completed'}
              >
                Mark Complete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Requests
