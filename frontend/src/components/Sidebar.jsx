import './Primitives.css'
import { useTheme } from '../theme/ThemeProvider'

export function Sidebar({ currentPage, onNavigate, onLogout, health }) {
  const { theme, setTheme } = useTheme()

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
    { id: 'mappings', label: 'Mappings', icon: '📧' },
    { id: 'templates', label: 'Templates', icon: '📝' },
    { id: 'queue', label: 'Queue', icon: '📋' },
  ]

  return (
    <aside className="sidebar">
      <div className="logo">SignalHub</div>
      <nav className="nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={currentPage === item.id ? 'active' : ''}
            onClick={() => onNavigate(item.id)}
          >
            {item.icon} {item.label}
          </button>
        ))}
      </nav>
      
      <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
        <div style={{ marginBottom: 12, color: 'var(--text-muted)', fontSize: 12 }}>
          <div>API: {health?.status === 'ok' ? '🟢 Online' : '🔴 Offline'}</div>
          <div>SMTP: {health?.smtp_running ? '🟢 Running' : '🔴 Stopped'}</div>
        </div>
        
        <button 
          className="btn secondary" 
          style={{ width: '100%', marginBottom: 8, fontSize: 12 }}
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        >
          {theme === 'light' ? '🌙' : '☀️'} {theme === 'light' ? 'Dark' : 'Light'} Mode
        </button>
        
        <button 
          className="btn secondary" 
          style={{ width: '100%', fontSize: 12 }}
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </aside>
  )
}