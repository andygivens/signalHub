import { useState, useEffect } from 'react'

const API_BASE = '/api'

function Templates({ token }) {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    content: ''
  })

  useEffect(() => {
    loadTemplates()
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

  const loadTemplates = async () => {
    try {
      setLoading(true)
      const data = await apiCall('/templates/')
      setTemplates(data)
    } catch (err) {
      setError(`Failed to load templates: ${err.message}`)
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
        await apiCall(`/templates/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(formData)
        })
        setMessage('Template updated successfully!')
      } else {
        await apiCall('/templates/', {
          method: 'POST',
          body: JSON.stringify(formData)
        })
        setMessage('Template created successfully!')
      }
      
      resetForm()
      loadTemplates()
    } catch (err) {
      setError(`Failed to save template: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (template) => {
    setFormData({
      name: template.name,
      content: template.content
    })
    setEditingId(template.id)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this template?')) return

    try {
      setLoading(true)
      await apiCall(`/templates/${id}`, { method: 'DELETE' })
      setMessage('Template deleted successfully!')
      loadTemplates()
    } catch (err) {
      setError(`Failed to delete template: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({ name: '', content: '' })
    setEditingId(null)
    setShowForm(false)
  }

  const insertVariable = (variable) => {
    const textarea = document.querySelector('textarea[name="content"]')
    if (textarea) {
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const currentContent = formData.content
      const newContent = currentContent.substring(0, start) + variable + currentContent.substring(end)
      setFormData({...formData, content: newContent})
      
      // Restore cursor position
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + variable.length
        textarea.focus()
      }, 0)
    }
  }

  return (
    <div className="page">
      <h2>📝 Notification Templates</h2>
      <p>Create and edit templates for formatting email notifications.</p>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      <div className="page-actions">
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Template'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>{editingId ? 'Edit Template' : 'Add New Template'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Template Name:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g., Default Alert, Security Alert"
                required
              />
            </div>

            <div className="form-group">
              <label>Template Content:</label>
              <div className="template-variables">
                <small>Insert variables:</small>
                <button type="button" onClick={() => insertVariable('{{sender}}')}>Sender</button>
                <button type="button" onClick={() => insertVariable('{{subject}}')}>Subject</button>
                <button type="button" onClick={() => insertVariable('{{recipient}}')}>Recipient</button>
                <button type="button" onClick={() => insertVariable('{{body}}')}>Body</button>
                <button type="button" onClick={() => insertVariable('{{timestamp}}')}>Timestamp</button>
              </div>
              <textarea
                name="content"
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                placeholder="📧 New email from {{sender}}&#10;&#10;Subject: {{subject}}&#10;Time: {{timestamp}}"
                rows="6"
                required
              />
              <small>Use variables like {`{{sender}}, {{subject}}, {{body}}`} to insert email data</small>
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
        <h3>Current Templates</h3>
        {loading && <p>Loading...</p>}
        {templates.length === 0 && !loading && (
          <p>No templates configured. Add one to customize your notifications!</p>
        )}
        {templates.length > 0 && (
          <div className="template-grid">
            {templates.map((template) => (
              <div key={template.id} className="template-card">
                <div className="template-header">
                  <h4>{template.name}</h4>
                  <div className="template-actions">
                    <button onClick={() => handleEdit(template)}>Edit</button>
                    <button onClick={() => handleDelete(template.id)}>Delete</button>
                  </div>
                </div>
                <div className="template-preview">
                  <pre>{template.content}</pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Templates