import { useState, useEffect } from 'react'

const API_BASE = '/api'

function Queue({ token }) {
  const [queueItems, setQueueItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadQueue()
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

  const loadQueue = async () => {
    try {
      setLoading(true)
      const data = await apiCall('/queue/')
      setQueueItems(data)
    } catch (err) {
      setError(`Failed to load queue: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = async (id) => {
    try {
      setLoading(true)
      await apiCall(`/queue/${id}/retry`, { method: 'POST' })
      setMessage('Message queued for retry!')
      loadQueue()
    } catch (err) {
      setError(`Failed to retry message: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRetryAll = async () => {
    if (!confirm('Retry all failed messages?')) return

    try {
      setLoading(true)
      await apiCall('/queue/retry-all', { method: 'POST' })
      setMessage('All messages queued for retry!')
      loadQueue()
    } catch (err) {
      setError(`Failed to retry messages: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this message?')) return

    try {
      setLoading(true)
      await apiCall(`/queue/${id}`, { method: 'DELETE' })
      setMessage('Message deleted!')
      loadQueue()
    } catch (err) {
      setError(`Failed to delete message: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all queue items? This cannot be undone.')) return

    try {
      setLoading(true)
      await apiCall('/queue/clear', { method: 'POST' })
      setMessage('Queue cleared!')
      loadQueue()
    } catch (err) {
      setError(`Failed to clear queue: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getStatusIcon = (attempts, maxRetries = 3) => {
    if (attempts === 0) return '⏳'
    if (attempts >= maxRetries) return '❌'
    return '🔄'
  }

  const getStatusText = (attempts, maxRetries = 3) => {
    if (attempts === 0) return 'Pending'
    if (attempts >= maxRetries) return 'Failed'
    return `Retrying (${attempts}/${maxRetries})`
  }

  return (
    <div className="page">
      <h2>📋 Message Queue</h2>
      <p>Monitor and manage failed email delivery attempts.</p>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      <div className="page-actions">
        <button onClick={loadQueue} disabled={loading}>
          🔄 Refresh
        </button>
        {queueItems.length > 0 && (
          <>
            <button onClick={handleRetryAll} disabled={loading}>
              ⚡ Retry All
            </button>
            <button onClick={handleClearAll} disabled={loading} className="danger">
              🗑️ Clear All
            </button>
          </>
        )}
      </div>

      <div className="data-table">
        {loading && <p>Loading...</p>}
        {queueItems.length === 0 && !loading && (
          <div className="empty-state">
            <h3>✅ Queue is empty</h3>
            <p>No failed messages in the queue. All emails are being delivered successfully!</p>
          </div>
        )}
        {queueItems.length > 0 && (
          <>
            <div className="queue-stats">
              <span>Total: {queueItems.length}</span>
              <span>Failed: {queueItems.filter(item => item.attempts >= 3).length}</span>
              <span>Retrying: {queueItems.filter(item => item.attempts > 0 && item.attempts < 3).length}</span>
            </div>
            
            <table>
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Recipient</th>
                  <th>Subject</th>
                  <th>Attempts</th>
                  <th>Last Error</th>
                  <th>Timestamp</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {queueItems.map((item) => (
                  <tr key={item.id} className={item.attempts >= 3 ? 'failed' : ''}>
                    <td>
                      <span className="status-badge">
                        {getStatusIcon(item.attempts)} {getStatusText(item.attempts)}
                      </span>
                    </td>
                    <td><code>{item.rcpt_to}</code></td>
                    <td className="subject-cell">
                      <span title={item.subject}>
                        {item.subject.length > 50 ? item.subject.substring(0, 50) + '...' : item.subject}
                      </span>
                    </td>
                    <td>{item.attempts}</td>
                    <td className="error-cell">
                      {item.last_error ? (
                        <span title={item.last_error}>
                          {item.last_error.length > 30 ? item.last_error.substring(0, 30) + '...' : item.last_error}
                        </span>
                      ) : (
                        <em>None</em>
                      )}
                    </td>
                    <td>{formatTimestamp(item.timestamp)}</td>
                    <td>
                      <button onClick={() => handleRetry(item.id)} disabled={loading}>
                        Retry
                      </button>
                      <button onClick={() => handleDelete(item.id)} disabled={loading}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  )
}

export default Queue