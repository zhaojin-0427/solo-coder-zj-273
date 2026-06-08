import { request } from '../request'

export const getStatistics = () => request.get('/api/statistics').then(r => r.data)
export const getMeta = () => request.get('/api/meta').then(r => r.data)
