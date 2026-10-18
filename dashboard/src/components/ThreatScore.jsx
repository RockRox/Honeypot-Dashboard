import { useEffect, useState } from 'react'
import { fetchTopIPs } from '../api'

function ScorePill({ score }) {
  const cls = score >= 80 ? 'score-high' : score >= 40 ? 'score-medium' : 'score-low'
  return <span className={`score-pill ${cls}`}>{score ?? 0}%</span>
}

export default function ThreatScore({ hours }) {
  const [ips, setIps] = useState([])

  useEffect(() => {
    fetchTopIPs(hours).then(r => setIps(r.data)).catch(() => {})
  }, [hours])

  return (
    <div className="card">
      <p className="card-title">Top Threat Actors</p>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>IP</th>
              <th>Attempts</th>
              <th>Country</th>
              <th>ISP / ASN</th>
              <th>Tor</th>
              <th>AbuseIPDB</th>
            </tr>
          </thead>
          <tbody>
            {ips.length === 0
              ? <tr><td colSpan={6} style={{ textAlign:'center', color:'#475569', padding:20, fontFamily:'monospace' }}>No data yet</td></tr>
              : ips.map((ip, i) => (
                <tr key={i}>
                  <td className="ip-mono">{ip.src_ip}</td>
                  <td style={{ fontFamily:'monospace', color:'#f43f5e' }}>{ip.attempts}</td>
                  <td className="country-cell">{ip.country ?? '—'}</td>
                  <td style={{ fontSize:11, color:'#475569', maxWidth:140, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    {ip.isp ?? ip.asn ?? '—'}
                  </td>
                  <td style={{ textAlign:'center' }}>{ip.is_tor ? '🧅' : '—'}</td>
                  <td><ScorePill score={ip.abuse_score} /></td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
