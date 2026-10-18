import { useEffect, useState } from 'react'
import { fetchCredentials } from '../api'

function BarList({ items, color = '' }) {
  const max = Math.max(...items.map(i => i.count), 1)
  return (
    <div>
      {items.map((item, i) => (
        <div key={i} className="bar-row">
          <span className="bar-label" title={item.username || item.password || item.combo}>
            {item.username ?? item.password ?? item.combo}
          </span>
          <div className="bar-track">
            <div className={`bar-fill ${color}`} style={{ width: `${(item.count / max) * 100}%` }} />
          </div>
          <span className="bar-count">{item.count}</span>
        </div>
      ))}
    </div>
  )
}

export default function CredentialAnalysis({ hours }) {
  const [data, setData] = useState(null)
  const [tab,  setTab]  = useState('combos')

  useEffect(() => {
    fetchCredentials(hours).then(r => setData(r.data)).catch(() => {})
  }, [hours])

  const tabs = ['combos', 'usernames', 'passwords']
  const tabLabel = { combos:'Combinations', usernames:'Usernames', passwords:'Passwords' }

  return (
    <div className="card">
      <p className="card-title">Credential Analysis</p>
      <div style={{ display:'flex', gap:0, marginBottom:16, borderBottom:'1px solid var(--border)' }}>
        {tabs.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              background: 'none',
              border: 'none',
              borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent',
              color: tab === t ? 'var(--text-1)' : 'var(--text-3)',
              padding: '6px 14px',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: 'monospace',
              marginBottom: -1,
            }}
          >{tabLabel[t]}</button>
        ))}
      </div>
      {!data
        ? <p className="loading">Loading…</p>
        : <BarList items={data[tab] ?? []} color={tab === 'passwords' ? 'cyan' : ''} />
      }
    </div>
  )
}
