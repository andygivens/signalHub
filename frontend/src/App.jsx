import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './theme/ThemeProvider'
import { Sidebar } from './components/Sidebar'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Settings from './components/Settings'
import Mappings from './components/Mappings'
import Templates from './components/Templates'
import Queue from './components/Queue'
import './components/Primitives.css'
import './App.css'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [health, setHealth] = useState(null)

  // Check health status periodically
  useEffect(() => {
    if (!token) return

    const checkHealth = () => {
      fetch('/healthz')
        .then(res => res.json())
        .then(data => setHealth(data))
        .catch(err => console.error('Health check failed:', err))
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30s
    return () => clearInterval(interval)
  }, [token])

  const handleLogin = (newToken) => {
    setToken(newToken)
    localStorage.setItem('token', newToken)
  }

  const handleLogout = () => {
    setToken(null)
    localStorage.removeItem('token')
    setCurrentPage('dashboard')
  }

  const handleNavigate = (page) => {
    setCurrentPage(page)
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'settings':
        return <Settings token={token} />
      case 'mappings':
        return <Mappings token={token} />
      case 'templates':
        return <Templates token={token} />
      case 'queue':
        return <Queue token={token} />
      default:
        return <Dashboard token={token} health={health} onNavigate={handleNavigate} />
    }
  }

  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route 
              path="/login" 
              element={!token ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} 
            />
            <Route 
              path="/dashboard" 
              element={token ? (
                <div className="layout">
                  <Sidebar 
                    currentPage={currentPage}
                    onNavigate={handleNavigate}
                    onLogout={handleLogout}
                    health={health}
                  />
                  <main className="main-content">
                    {renderPage()}
                  </main>
                </div>
              ) : <Navigate to="/login" />} 
            />
            <Route path="/" element={<Navigate to={token ? "/dashboard" : "/login"} />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App