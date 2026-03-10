import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 30000 })

export const useApi = () => ({
  dashboard:     ()          => api.get('/dashboard'),
  telemetry:     (id, d=30)  => api.get(`/telemetry/${id}?days=${d}`),
  sensorChart:   (id, sensor)=> api.get(`/chart/${id}/${sensor}`),
  anomalies:     (id)        => api.get(`/anomalies/${id}`),
  risk:          (id)        => api.get(`/risk/${id}`),
  schedule:      (id)        => id ? api.get(`/schedule/${id}`) : api.get('/schedule'),
  vendors:       ()          => api.get('/vendors'),
  cost:          (id)        => id ? api.get(`/cost/${id}`) : api.get('/cost'),
  agentRun:      (id)        => api.post(`/agent/run/${id}`),
  agentRunAll:   ()          => api.post('/agent/run-all'),
  agentLogs:     ()          => api.get('/agent/logs'),
})
