import { useState, useEffect } from 'react'

const API_BASE = '/api'

function Settings({ token }) {
  const [activeTab, setActiveTab] = useState('smtp')
  const [smtpSettings, setSMTPSettings] = useState({
    host: '',
    port: 587,
    username: '',
    password: '',
    use_tls: true,
    use_ssl: false
  })
  const [pushoverSettings, setPushoverSettings] = useState({
    api_token: '',
    default_user_key: '',
    default_device: ''
  })
  const [appSettings, setAppSettings] = useState({
    queue_dir: './queue',
    max_retries: 3,
    retry_delay: 300
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadSettings()
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

  const loadSettings = async () => {
    try {
      const [smtp, pushover, app] = await Promise.all([
        apiCall('/settings/smtp'),
        apiCall('/settings/pushover'),
        apiCall('/settings/app')
      ])
      setSMTPSettings(smtp)
      if (pushover) setPushoverSettings(pushover)
      setAppSettings(app)
    } catch (err) {
      setError(`Failed to load settings: ${err.message}`)
    }
  }

  const saveSettings = async (type, settings) => {
    setLoading(true)
    setMessage('')
    setError('')
    try {
      await apiCall(`/settings/${type}`, {
        method: 'POST',
        body: JSON.stringify(settings)
      })
      setMessage(`${type.toUpperCase()} settings saved successfully!`)
    } catch (err) {
      setError(`Failed to save ${type} settings: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testConnection = async (type, settings) => {
    setLoading(true)
    setMessage('')
    setError('')
    try {
      const result = await apiCall(`/settings/${type}/test`, {
        method: 'POST',
        body: JSON.stringify(settings)
      })
      if (result.success) {
        setMessage(`${type.toUpperCase()} connection test successful!`)
      } else {
        setError(`${type.toUpperCase()} test failed: ${result.error}`)
      }
    } catch (err) {
      setError(`Test failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="settings">
      <h2>Settings</h2>
      
      <div className="tabs">
        <button 
          className={activeTab === 'smtp' ? 'active' : ''} 
          onClick={() => setActiveTab('smtp')}
        >
          SMTP
        </button>
        <button 
          className={activeTab === 'pushover' ? 'active' : ''} 
          onClick={() => setActiveTab('pushover')}
        >
          Pushover
        </button>
        <button 
          className={activeTab === 'app' ? 'active' : ''} 
          onClick={() => setActiveTab('app')}
        >
          Application
        </button>
      </div>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      {activeTab === 'smtp' && (
        <SMTPForm 
          settings={smtpSettings}
          onChange={setSMTPSettings}
          onSave={() => saveSettings('smtp', smtpSettings)}
          onTest={() => testConnection('smtp', smtpSettings)}
          loading={loading}
        />
      )}

      {activeTab === 'pushover' && (
        <PushoverForm 
          settings={pushoverSettings}
          onChange={setPushoverSettings}
          onSave={() => saveSettings('pushover', pushoverSettings)}
          onTest={() => testConnection('pushover', pushoverSettings)}
          loading={loading}
        />
      )}

      {activeTab === 'app' && (
        <AppForm 
          settings={appSettings}
          onChange={setAppSettings}
          onSave={() => saveSettings('app', appSettings)}
          loading={loading}
        />
      )}
    </div>
  )
}

function SMTPForm({ settings, onChange, onSave, onTest, loading }) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(); }}>
      <h3>SMTP Configuration</h3>
      
      <div className="form-group">
        <label>SMTP Host:</label>
        <input
          type="text"
          value={settings.host}
          onChange={(e) => onChange({...settings, host: e.target.value})}
          placeholder="smtp.gmail.com"
          required
        />
      </div>

      <div className="form-group">
        <label>Port:</label>
        <input
          type="number"
          value={settings.port}
          onChange={(e) => onChange({...settings, port: parseInt(e.target.value)})}
          min="1"
          max="65535"
          required
        />
      </div>

      <div className="form-group">
        <label>Username:</label>
        <input
          type="text"
          value={settings.username || ''}
          onChange={(e) => onChange({...settings, username: e.target.value})}
          placeholder="your-email@gmail.com"
        />
      </div>

      <div className="form-group">
        <label>Password:</label>
        <input
          type="password"
          value={settings.password === '***' ? '' : settings.password || ''}
          onChange={(e) => onChange({...settings, password: e.target.value})}
          placeholder={settings.password === '***' ? 'Password is set' : 'Enter password'}
        />
      </div>

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={settings.use_tls}
            onChange={(e) => onChange({...settings, use_tls: e.target.checked})}
          />
          Use TLS
        </label>
      </div>

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={settings.use_ssl}
            onChange={(e) => onChange({...settings, use_ssl: e.target.checked})}
          />
          Use SSL
        </label>
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
        <button type="button" onClick={onTest} disabled={loading}>
          {loading ? 'Testing...' : 'Test Connection'}
        </button>
      </div>
    </form>
  )
}

function PushoverForm({ settings, onChange, onSave, onTest, loading }) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(); }}>
      <h3>Pushover Configuration</h3>
      
      <div className="form-group">
        <label>API Token:</label>
        <input
          type="password"
          value={settings.api_token === '***' ? '' : settings.api_token}
          onChange={(e) => onChange({...settings, api_token: e.target.value})}
          placeholder={settings.api_token === '***' ? 'Token is set' : 'Enter API token'}
          required
        />
        <small>Get your API token from <a href="https://pushover.net/apps" target="_blank" rel="noopener noreferrer">pushover.net/apps</a></small>
      </div>

      <div className="form-group">
        <label>Default User Key:</label>
        <input
          type="text"
          value={settings.default_user_key || ''}
          onChange={(e) => onChange({...settings, default_user_key: e.target.value})}
          placeholder="30-character user key"
        />
        <small>Your user key from <a href="https://pushover.net" target="_blank" rel="noopener noreferrer">pushover.net</a></small>
      </div>

      <div className="form-group">
        <label>Default Device:</label>
        <input
          type="text"
          value={settings.default_device || ''}
          onChange={(e) => onChange({...settings, default_device: e.target.value})}
          placeholder="Leave blank for all devices"
        />
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
        <button type="button" onClick={onTest} disabled={loading}>
          {loading ? 'Testing...' : 'Test Connection'}
        </button>
      </div>
    </form>
  )
}

function AppForm({ settings, onChange, onSave, loading }) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(); }}>
      <h3>Application Settings</h3>
      
      <div className="form-group">
        <label>Queue Directory:</label>
        <input
          type="text"
          value={settings.queue_dir}
          onChange={(e) => onChange({...settings, queue_dir: e.target.value})}
          required
        />
        <small>Directory where failed messages are queued for retry</small>
      </div>

      <div className="form-group">
        <label>Max Retries:</label>
        <input
          type="number"
          value={settings.max_retries}
          onChange={(e) => onChange({...settings, max_retries: parseInt(e.target.value)})}
          min="0"
          max="10"
          required
        />
        <small>Maximum number of delivery attempts</small>
      </div>

      <div className="form-group">
        <label>Retry Delay (seconds):</label>
        <input
          type="number"
          value={settings.retry_delay}
          onChange={(e) => onChange({...settings, retry_delay: parseInt(e.target.value)})}
          min="30"
          max="3600"
          required
        />
        <small>Delay between retry attempts</small>
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </form>
  )
}

export default Settings