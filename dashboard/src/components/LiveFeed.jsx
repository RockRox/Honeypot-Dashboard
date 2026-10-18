import { useEffect, useState } from 'react'
import { fetchAttacks } from '../api'

function ScorePill({ score }) {
  const cls = score >= 80 ? 'score-high' : score >= 40 ? 'score-medium' : 'score-low'
  return <span className={`score-pill ${cls}`}>{score ?? '—'}%</span>
}

function EventBadge({ eventId }) {
  const colors = {
    'cowrie.login.failed':       { bg:'rgba(244,63,94,0.12)',  color:'#f43f5e' },
    'cowrie.login.success':      { bg:'rgba(16,185,129,0.12)', color:'#10b981' },
    'cowrie.command.input':      { bg:'rgba(99,102,241,0.12)', color:'#818cf8' },
    'cowrie.session.connect':    { bg:'rgba(34,211,238,0.1)',  color:'#22d3ee' },
    'cowrie.session.closed':     { bg:'rgba(71,85,105,0.2)',   color:'#64748b' },
    'cowrie.session.file_download':{ bg:'rgba(245,158,11,0.12)',color:'#f59e0b'},
  }
  const label = eventId?.split('.').slice(-2).join('.') ?? eventId
  const style = colors[eventId] ?? { bg:'rgba(71,85,105,0.2)', color:'#94a3b8' }
  return (
    <span style={{ ...style, fontSize:11, padding:'2px 7px', borderRadius:99, fontFamily:'monospace', display:'inline-block' }}>
      {label}
    </span>
  )
}

export default function LiveFeed({ hours }) {
  const [data, setData]   = useState([])
  const [page, setPage]   = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    fetchAttacks(hours, page).then(r => {
      setData(r.data.data)
      setTotal(r.data.total)
    }).catch(() => {})
  }, [hours, page])

  const pages = Math.ceil(total / 25)

  return (
    <div className="card">
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:14 }}>
        <p className="card-title" style={{ marginBottom:0 }}>Live Event Feed — {total.toLocaleString()} total</p>
        <div style={{ display:'flex', gap:8, alignItems:'center', fontSize:12, color:'#475569' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{ background:'none', border:'1px solid var(--border)', color:'#94a3b8', borderRadius:6, padding:'3px 10px', cursor:'pointer', fontSize:12 }}
          >←</button>
          <span style={{ fontFamily:'monospace' }}>{page}/{pages || 1}</span>
          <button
            onClick={() => setPage(p => Math.min(pages, p + 1))}
            disabled={page >= pages}
            style={{ background:'none', border:'1px solid var(--border)', color:'#94a3b8', borderRadius:6, padding:'3px 10px', cursor:'pointer', fontSize:12 }}
          >→</button>
        </div>
      </div>
      <div style={{ overflowX:'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>IP</th>
              <th>Event</th>
              <th>Credential</th>
              <th>Command</th>
              <th>Location</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0
              ? <tr><td colSpan={7} style={{ textAlign:'center', color:'#475569', padding:24, fontFamily:'monospace' }}>No events yet — waiting for attackers…</td></tr>
              : data.map((ev, i) => (
                <tr key={i}>
                  <td style={{ fontFamily:'monospace', fontSize:11, color:'#475569', whiteSpace:'nowrap' }}>
                    {ev.timestamp?.slice(0,19).replace('T', ' ')}
                  </td>
                  <td className="ip-mono">{ev.src_ip}</td>
                  <td><EventBadge eventId={ev.event_id} /></td>
                  <td style={{ fontFamily:'monospace', fontSize:12, color:'#94a3b8' }}>
                    {ev.username ? `${ev.username}/${ev.password ?? ''}` : '—'}
                  </td>
                  <td style={{ fontFamily:'monospace', fontSize:11, color:'#818cf8', maxWidth:200, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    {ev.command || '—'}
                  </td>
                  <td className="country-cell">
                    {ev.country ? `${ev.city || ''} ${ev.country}`.trim() : '—'}
                  </td>
                  <td><ScorePill score={ev.abuse_score} /></td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
