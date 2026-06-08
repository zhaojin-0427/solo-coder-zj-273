import { request } from '../request'

export const getLoans = (params = {}) => request.get('/api/loans', { params }).then(r => r.data)
export const createLoan = (data) => request.post('/api/loans', data).then(r => r.data)
export const returnLoan = (id, data) => request.post(`/api/loans/${id}/return`, data || {}).then(r => r.data)
export const updateLoan = (id, data) => request.put(`/api/loans/${id}`, data).then(r => r.data)
export const deleteLoan = (id) => request.delete(`/api/loans/${id}`).then(r => r.data)
export const getMaintenance = (params = {}) => request.get('/api/maintenance', { params }).then(r => r.data)
export const createMaintenance = (data) => request.post('/api/maintenance', data).then(r => r.data)
export const completeMaintenance = (id, data) => request.post(`/api/maintenance/${id}/complete`, data || {}).then(r => r.data)
export const updateMaintenance = (id, data) => request.put(`/api/maintenance/${id}`, data).then(r => r.data)
export const deleteMaintenance = (id) => request.delete(`/api/maintenance/${id}`).then(r => r.data)
export const getTrackingSummary = () => request.get('/api/tracking/summary').then(r => r.data)
