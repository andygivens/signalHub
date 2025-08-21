import { useState, useEffect } from 'react'

const API_BASE = '/api'

function Mappings({ token }) {
  const [mappings, setMappings] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    rcpt_pattern: '',
    user_key: '',
    device: ''
  })

  useEffect(() => {
    loadMappings()
  }, [])

  const apiCall = async (url, options = {}) => {
    const response = await fetch(`${API_BASE}${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response.json()
  }

  const loadMappings = async () => {
    try {
      setLoading(true)
      const data = await apiCall('/mappings/')
      setMappings(data)
    } catch (err) {
      setError(`Failed to load mappings: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      if (editingId) {
        await apiCall(`/mappings/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(formData)
        })
        setMessage('Mapping updated successfully!')
      } else {
        await apiCall('/mappings/', {
          method: 'POST',
          body: JSON.stringify(formData)
        })
        setMessage('Mapping created successfully!')
      }
      
      resetForm()
      loadMappings()
    } catch (err) {
      setError(`Failed to save mapping: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (mapping) => {
    setFormData({
      rcpt_pattern: mapping.rcpt_pattern,
      user_key: mapping.user_key,
      device: mapping.device || ''
    })
    setEditingId(mapping.id)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this mapping?')) return

    try {
      setLoading(true)
      await apiCall(`/mappings/${id}`, { method: 'DELETE' })
      setMessage('Mapping deleted successfully!')
      loadMappings()
    } catch (err) {
      setError(`Failed to delete mapping: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({ rcpt_pattern: '', user_key: '', device: '' })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div className="page">
      <h2>📧 Email Mappings</h2>
      <p>Configure which Pushover user receives notifications for each email address.</p>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      <div className="page-actions">
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Mapping'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>{editingId ? 'Edit Mapping' : 'Add New Mapping'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email Pattern:</label>
              <input
                type="text"
                value={formData.rcpt_pattern}
                onChange={(e) => setFormData({...formData, rcpt_pattern: e.target.value})}
                placeholder="user@domain.com or *@domain.com"
                required
              />
              <small>Use * as wildcard (e.g., *@example.com for all emails from that domain)</small>
            </div>

            <div className="form-group">
              <label>Pushover User Key:</label>
              <input
                type="text"
                value={formData.user_key}
                onChange={(e) => setFormData({...formData, user_key: e.target.value})}
                placeholder="30-character user key"
                required
              />
              <small>Your user key from <a href="https://pushover.net" target="_blank" rel="noopener noreferrer">pushover.net</a></small>
            </div>

            <div className="form-group">
              <label>Device (optional):</label>
              <input
                type="text"
                value={formData.device}
                onChange={(e) => setFormData({...formData, device: e.target.value})}
                placeholder="Leave blank for all devices"
              />
            </div>

            <div className="form-actions">
              <button type="submit" disabled={loading}>
                {loading ? 'Saving...' : (editingId ? 'Update' : 'Create')}
              </button>
              <button type="button" onClick={resetForm}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="data-table">
        <h3>Current Mappings</h3>
        {loading && <p>Loading...</p>}
        {mappings.length === 0 && !loading && (
          <p>No mappings configured. Add one to get started!</p>
        )}
        {mappings.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Email Pattern</th>
                <th>User Key</th>
                <th>Device</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((mapping) => (
                <tr key={mapping.id}>
                  <td><code>{mapping.rcpt_pattern}</code></td>
                  <td><code>{mapping.user_key.substring(0, 8)}...</code></td>
                  <td>{mapping.device || <em>All devices</em>}</td>
                  <td>
                    <button onClick={() => handleEdit(mapping)}>Edit</button>
                    <button onClick={() => handleDelete(mapping.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Mappings