import { useEffect, useState } from 'react'
import { fetchStats } from '../api'

export default function MetricCards({ hours }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats(hours)
      .then(r => setData(r.data))
      .catch(() => setError('Failed to load stats'))
  }, [hours])

  if (error) return <p className="error">{error}</p>
  if (!data)  return <p className="loading">Loading metrics…</p>

  const cards = [
    {
      label: 'Total Attacks',
      value: data.total_attacks?.toLocaleString() ?? '—',
      sub:   `Last ${hours}h`,
      cls:   'danger',
    },
    {
      label: 'Unique Attacker IPs',
      value: data.unique_ips?.toLocaleString() ?? '—',
      sub:   'distinct sources',
      cls:   'warn',
    },
    {
      label: 'Top Country',
      value: data.top_country?.country ?? '—',
      sub:   `${data.top_country?.n ?? 0} attacks`,
      cls:   'accent',
    },
    {
      label: 'Top Credential',
      value: data.top_credential?.cred ?? '—',
      sub:   `tried ${data.top_credential?.n ?? 0}×`,
      cls:   'ok',
    },
  ]

  return (
    <div className="metrics-grid">
      {cards.map(c => (
        <div key={c.label} className={`metric-card ${c.cls}`}>
          <span className="metric-label">{c.label}</span>
          <span className="metric-value">{c.value}</span>
          <span className="metric-sub">{c.sub}</span>
        </div>
      ))}
    </div>
  )
}
