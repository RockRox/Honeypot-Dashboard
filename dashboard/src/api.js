import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
const API_KEY = import.meta.env.VITE_API_KEY || 'dev_key_change_me'

const client = axios.create({
  baseURL: API_URL,
  headers: { 'X-API-Key': API_KEY },
})

export const fetchStats       = (hours = 24) => client.get(`/api/stats?hours=${hours}`)
export const fetchAttacks     = (hours = 24, page = 1) => client.get(`/api/attacks?hours=${hours}&page=${page}&per_page=25`)
export const fetchTopIPs      = (hours = 24) => client.get(`/api/top-ips?hours=${hours}&limit=10`)
export const fetchCommands    = (hours = 24) => client.get(`/api/commands?hours=${hours}&limit=15`)
export const fetchMapData     = (hours = 24) => client.get(`/api/map-data?hours=${hours}`)
export const fetchCredentials = (hours = 24) => client.get(`/api/credentials?hours=${hours}`)
export const fetchTimeline    = (hours = 24) => client.get(`/api/timeline?hours=${hours}`)
