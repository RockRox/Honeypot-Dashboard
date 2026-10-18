import { useState } from 'react'
import MetricCards        from '../components/MetricCards'
import Timeline           from '../components/Timeline'
import AttackMap          from '../components/AttackMap'
import LiveFeed           from '../components/LiveFeed'
import CredentialAnalysis from '../components/CredentialAnalysis'
import ThreatScore        from '../components/ThreatScore'

export default function Dashboard() {
  const [hours, setHours] = useState(24)

  return (
    <div className="layout">
      {/* Top bar */}
      <header className="topbar">
        <span className="topbar-logo">honeypot//intel</span>
        <span className="topbar-sub">SSH · Telnet · Real-time threat capture</span>
        <div className="topbar-right">
          <select
            className="window-select"
            value={hours}
            onChange={e => setHours(Number(e.target.value))}
          >
            <option value={1}>Last 1h</option>
            <option value={6}>Last 6h</option>
            <option value={24}>Last 24h</option>
            <option value={72}>Last 3d</option>
            <option value={168}>Last 7d</option>
            <option value={720}>Last 30d</option>
          </select>
          <div className="live-badge">
            <span className="live-dot" />
            LIVE
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="main-content">
        <MetricCards hours={hours} />
        <Timeline hours={hours} />
        <div className="two-col">
          <AttackMap hours={hours} />
          <CredentialAnalysis hours={hours} />
        </div>
        <ThreatScore hours={hours} />
        <LiveFeed hours={hours} />
      </main>
    </div>
  )
}
