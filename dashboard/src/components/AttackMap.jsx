import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchMapData } from '../api'

function scoreColor(score) {
  if (score >= 80) return '#f43f5e'
  if (score >= 40) return '#f59e0b'
  return '#22d3ee'
}

export default function AttackMap({ hours }) {
  const [points, setPoints] = useState([])

  useEffect(() => {
    fetchMapData(hours).then(r => setPoints(r.data)).catch(() => {})
  }, [hours])

  const maxAttempts = Math.max(...points.map(p => p.attempts), 1)

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '20px 20px 12px' }}>
        <p className="card-title" style={{ marginBottom: 0 }}>
          Attack Origins — {points.length} sources
        </p>
      </div>
      <MapContainer
        center={[20, 0]}
        zoom={2}
        style={{ height: '320px', width: '100%' }}
        attributionControl={false}
        zoomControl={false}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {points.map((p, i) => (
          <CircleMarker
            key={i}
            center={[p.lat, p.lon]}
            radius={4 + (p.attempts / maxAttempts) * 14}
            pathOptions={{
              color:       scoreColor(p.abuse_score),
              fillColor:   scoreColor(p.abuse_score),
              fillOpacity: 0.7,
              weight:      1,
            }}
          >
            <Tooltip>
              <div style={{ fontFamily: 'monospace', fontSize: 12 }}>
                <strong>{p.ip}</strong><br />
                {p.city}, {p.country}<br />
                Attempts: {p.attempts}<br />
                AbuseIPDB: {p.abuse_score}%
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
      <div style={{ padding: '10px 20px', display:'flex', gap:16, fontSize:11, color:'#475569', fontFamily:'monospace' }}>
        <span style={{ color:'#f43f5e' }}>● High threat (&gt;80%)</span>
        <span style={{ color:'#f59e0b' }}>● Medium (40–80%)</span>
        <span style={{ color:'#22d3ee' }}>● Low (&lt;40%)</span>
      </div>
    </div>
  )
}
