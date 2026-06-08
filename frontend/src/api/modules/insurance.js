import { request } from '../request'

export const getInsuranceItems = (params = {}) => request.get('/api/insurance', { params }).then(r => r.data)
export const getInsuranceItem = (id) => request.get(`/api/insurance/${id}`).then(r => r.data)
export const createInsuranceItem = (data) => request.post('/api/insurance', data).then(r => r.data)
export const updateInsuranceItem = (id, data) => request.put(`/api/insurance/${id}`, data).then(r => r.data)
export const deleteInsuranceItem = (id) => request.delete(`/api/insurance/${id}`).then(r => r.data)
export const exportInsuranceList = () => request.get('/api/insurance/export').then(r => r.data)
