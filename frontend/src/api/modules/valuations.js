import { request } from '../request'

export const calculateValuation = (id) => request.get(`/api/valuations/calculate/${id}`).then(r => r.data)
export const getValuations = (params = {}) => request.get('/api/valuations', { params }).then(r => r.data)
export const getValuation = (id) => request.get(`/api/valuations/${id}`).then(r => r.data)
export const createValuation = (data) => request.post('/api/valuations', data).then(r => r.data)
export const deleteValuation = (id) => request.delete(`/api/valuations/${id}`).then(r => r.data)
export const getValuationOverview = () => request.get('/api/valuations/overview').then(r => r.data)
