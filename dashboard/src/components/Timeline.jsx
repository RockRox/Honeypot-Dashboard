import { useEffect, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { fetchTimeline } from '../api'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background:'#0f0f1a', border:'1px solid rgba(99,102,241,0.3)', borderRadius:8, padding:'10px 14px', fontSize:12 }}>
      <p style={{ color:'#94a3b8', marginBottom:4, fontFamily:'monospace' }}>{label}</p>
      <p style={{ color:'#f43f5e' }}>Attacks: <strong>{payload[0]?.value}</strong></p>
      <p style={{ color:'#22d3ee' }}>Unique IPs: <strong>{payload[1]?.value}</strong></p>
    </div>
  )
}

export default function Timeline({ hours }) {
  const [data, setData] = useState([])

  useEffect(() => {
    fetchTimeline(hours).then(r => {
      const formatted = r.data.map(d => ({
        ...d,
        hour: d.hour?.slice(11, 16) || d.hour,  // show HH:MM
      }))
      setData(formatted)
    }).catch(() => {})
  }, [hours])

  return (
    <div className="card">
      <p className="card-title">Attack Volume — {hours}h window</p>
      {data.length === 0
        ? <p className="loading">No timeline data yet…</p>
        : (
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={data} margin={{ top:4, right:4, bottom:0, left:-20 }}>
              <defs>
                <linearGradient id="gAtk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#f43f5e" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="gIp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#22d3ee" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
              <XAxis dataKey="hour" tick={{ fill:'#475569', fontSize:11, fontFamily:'monospace' }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill:'#475569', fontSize:11 }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="attacks"    stroke="#f43f5e" fill="url(#gAtk)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="unique_ips" stroke="#22d3ee" fill="url(#gIp)"  strokeWidth={1.5} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        )
      }
    </div>
  )
}
