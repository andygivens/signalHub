import { useState, useEffect } from 'react'
import './Primitives.css'

const API_BASE = '/api'

function Dashboard({ token, health, onNavigate }) {
  const [metrics, setMetrics] = useState({
    emailsReceived: 12560,
    pushedOK: 12420,
    failed: 32,
    dedupDropped: 28,
    rateLimited: 28,
    queueSize: 4
  })
  const [recentEvents, setRecentEvents] = useState([
    { time: '10:24 AM', input: 'SMTP', destination: 'alerts@home.local', status: 'Pushed' },
    { time: '9:28 AM', input: 'SMTP', destination: 'alerts@home.local', status: 'Failed' },
    { time: '9:28 AM', input: 'SMTP', destination: 'alerts@home.local', status: 'Deduplicated' },
    { time: '3:23 AM', input: 'SMTP', destination: 'alerts@home.local', status: 'Pushed' }
  ])
  const [routingRules] = useState([
    { pattern: 'alerts@home.local', destination: 'Group A' },
    { pattern: 'cams@home.local', destination: 'User B' }
  ])
  const [testForm, setTestForm] = useState({
    input: 'SMTP',
    destination: 'Pushover • User A',
    message: 'This is a test'
  })
  const [isRunning, setIsRunning] = useState(true)

  const handleTestSend = async () => {
    try {
      // You can implement actual test send API call here
      console.log('Test send:', testForm)
      alert('Test notification sent!')
    } catch (err) {
      alert(`Test failed: ${err.message}`)
    }
  }

  const getStatusBadge = (status) => {
    switch (status.toLowerCase()) {
      case 'pushed':
        return <span className="badge ok">Pushed</span>
      case 'failed':
        return <span className="badge fail">Failed</span>
      case 'deduplicated':
        return <span className="badge">Deduplicated</span>
      default:
        return <span className="badge">{status}</span>
    }
  }

  return (
    <div className="container grid">
      <div className="toolbar">
        <div>
          <div className="title">Overview</div>
          <div className="subtitle">Snapshot of system activity and health</div>
        </div>
        <div className={`badge ${health?.status === 'ok' ? 'ok' : 'fail'}`}>
          ● {health?.status === 'ok' ? 'Healthy' : 'Offline'}
        </div>
      </div>

      {/* Metrics Grid */}
      <section className="metrics">
        <div className="card metric">
          <h4>Emails Received</h4>
          <div className="value">{metrics.emailsReceived.toLocaleString()}</div>
        </div>
        <div className="card metric">
          <h4>Pushed OK</h4>
          <div className="value">{metrics.pushedOK.toLocaleString()}</div>
        </div>
        <div className="card metric">
          <h4 style={{color:'var(--danger)'}}>Failed</h4>
          <div className="value" style={{color:'var(--danger)'}}>{metrics.failed}</div>
        </div>
        <div className="card metric">
          <h4>Events Per Minute</h4>
          <div className="spark" style={{display:'flex',alignItems:'center',justifyContent:'center',color:'var(--text-muted)',fontSize:'12px'}}>
            📈 Live Chart
          </div>
        </div>
        <div className="card metric">
          <h4>Dedup Dropped</h4>
          <div className="value">{metrics.dedupDropped}</div>
        </div>
        <div className="card metric">
          <h4 style={{color:'var(--warn)'}}>Rate Limited</h4>
          <div className="value" style={{color:'var(--warn)'}}>{metrics.rateLimited}</div>
        </div>
        <div className="card metric">
          <h4>Rate Limited</h4>
          <div className="value">15</div>
        </div>
        <div className="card metric">
          <h4>Queue Size</h4>
          <div className="value">{metrics.queueSize}</div>
        </div>
      </section>

      {/* Main Content Layout */}
      <section className="cols">
        <div className="grid">
          {/* Recent Events */}
          <div className="card">
            <h3 style={{marginTop:0}}>Recent Events</h3>
            <table className="table">
              <thead>
                <tr>
                  <th style={{width:120}}>Time</th>
                  <th style={{width:100}}>Input</th>
                  <th>Destination</th>
                  <th style={{width:160}}>Status</th>
                  <th style={{width:40}}></th>
                </tr>
              </thead>
              <tbody>
                {recentEvents.map((event, index) => (
                  <tr key={index}>
                    <td>{event.time}</td>
                    <td>{event.input}</td>
                    <td><code>{event.destination}</code></td>
                    <td>{getStatusBadge(event.status)}</td>
                    <td><button className="btn secondary" style={{padding:'4px 8px',fontSize:'12px'}}>+</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Routing Rules & Logs Row */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'24px'}}>
            <div className="card">
              <h3 style={{marginTop:0}}>Routing Rules</h3>
              {routingRules.map((rule, index) => (
                <div key={index} className="card" style={{padding:12,display:'flex',justifyContent:'space-between',marginBottom:8}}>
                  <strong>{rule.pattern}</strong>
                  <span>→ {rule.destination}</span>
                </div>
              ))}
            </div>

            <div className="card">
              <h3 style={{marginTop:0}}>Logs</h3>
              <div className="logs" style={{fontSize:'11px',color:'var(--text-muted)'}}>
{`{ "ts": "2025-08-20T09:41:12Z", "event": "email.received", "rcpt": "alerts@home.local", "status": "queued" }
{ "ts": "2025-08-20T09:41:12Z", "event": "pushover.sent", "status": 200 }
{ "ts": "2025-08-20T09:42:09Z", "event": "rate.limit", "count": 121 }`}
              </div>
            </div>
          </div>

          {/* Queue & Retries + System Controls */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'24px'}}>
            <div className="card">
              <h3 style={{marginTop:0}}>Queue & Retries</h3>
              <div style={{display:'flex',alignItems:'center',gap:'12px',marginBottom:'16px'}}>
                <div className={`badge ${isRunning ? 'ok' : 'fail'}`}>
                  ● {isRunning ? 'Start' : 'Stop'}
                </div>
                <button 
                  className="btn secondary" 
                  style={{padding:'4px 12px',fontSize:'12px'}}
                  onClick={() => setIsRunning(!isRunning)}
                >
                  {isRunning ? 'Stop' : 'Start'}
                </button>
              </div>
              
              <div style={{marginTop:16}}>
                <h4 style={{margin:'0 0 8px',color:'var(--text-muted)',fontSize:'13px'}}>Queue & Retries</h4>
                <div style={{display:'flex',gap:'12px'}}>
                  <button className="btn">Start</button>
                  <button className="btn secondary">Stop</button>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 style={{marginTop:0}}>Health</h3>
              <div className={`badge ${health?.status === 'ok' ? 'ok' : 'fail'}`} style={{marginBottom:'12px'}}>
                ● {health?.status === 'ok' ? 'Healthy' : 'Offline'}
              </div>
              
              <div style={{marginTop:16}}>
                <label className="subtitle">STARTTLS</label>
                <select className="card" style={{padding:'10px 12px',marginTop:8,width:'100%'}}>
                  <option>OFF</option>
                  <option>ON</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="grid">
          {/* Test Send */}
          <div className="card">
            <h3 style={{marginTop:0}}>Test Send</h3>
            <div style={{display:'grid',gap:12}}>
              <div>
                <label className="subtitle">Input</label>
                <select 
                  className="card" 
                  style={{padding:'10px 12px',width:'100%',marginTop:4}}
                  value={testForm.input}
                  onChange={(e) => setTestForm({...testForm, input: e.target.value})}
                >
                  <option>SMTP</option>
                </select>
              </div>
              
              <div>
                <label className="subtitle">Pushover</label>
                <select 
                  className="card" 
                  style={{padding:'10px 12px',width:'100%',marginTop:4}}
                  value={testForm.destination}
                  onChange={(e) => setTestForm({...testForm, destination: e.target.value})}
                >
                  <option>User A ˃</option>
                  <option>Group A ˃</option>
                </select>
              </div>
              
              <button className="btn" onClick={handleTestSend} style={{marginTop:8}}>
                Send
              </button>
            </div>
          </div>

          {/* Phone Mockup */}
          <div className="card" style={{textAlign:'center'}}>
            <div style={{
              width:'200px',
              height:'360px',
              background:'linear-gradient(145deg, #2c2c2e 0%, #1c1c1e 100%)',
              borderRadius:'40px',
              margin:'0 auto',
              position:'relative',
              boxShadow:'0 8px 32px rgba(0,0,0,0.3)'
            }}>
              {/* Screen */}
              <div style={{
                position:'absolute',
                top:'20px',
                left:'20px',
                right:'20px',
                bottom:'20px',
                background:'#000',
                borderRadius:'32px',
                overflow:'hidden'
              }}>
                {/* Status Bar */}
                <div style={{
                  height:'24px',
                  background:'rgba(255,255,255,0.1)',
                  display:'flex',
                  justifyContent:'space-between',
                  alignItems:'center',
                  padding:'0 16px',
                  fontSize:'12px',
                  color:'white'
                }}>
                  <span>9:41</span>
                  <span>🔋</span>
                </div>
                
                {/* Notification */}
                <div style={{
                  margin:'40px 16px',
                  background:'rgba(255,255,255,0.95)',
                  borderRadius:'12px',
                  padding:'12px',
                  boxShadow:'0 2px 8px rgba(0,0,0,0.2)'
                }}>
                  <div style={{display:'flex',alignItems:'center',gap:'8px',marginBottom:'4px'}}>
                    <div style={{
                      width:'16px',
                      height:'16px',
                      background:'var(--accent)',
                      borderRadius:'50%'
                    }}></div>
                    <span style={{fontSize:'12px',fontWeight:'600',color:'#000'}}>Test Notification</span>
                    <span style={{fontSize:'11px',color:'#666',marginLeft:'auto'}}>now</span>
                  </div>
                  <div style={{fontSize:'11px',color:'#333'}}>This is a test</div>
                </div>
              </div>
              
              {/* Home Indicator */}
              <div style={{
                position:'absolute',
                bottom:'8px',
                left:'50%',
                transform:'translateX(-50%)',
                width:'120px',
                height:'4px',
                background:'#333',
                borderRadius:'2px'
              }}></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard