import { request } from '../request'

export const getTrips = (params = {}) => request.get('/api/trips', { params }).then(r => r.data)
export const getTrip = (id) => request.get(`/api/trips/${id}`).then(r => r.data)
export const createTrip = (data) => request.post('/api/trips', data).then(r => r.data)
export const updateTrip = (id, data) => request.put(`/api/trips/${id}`, data).then(r => r.data)
export const deleteTrip = (id) => request.delete(`/api/trips/${id}`).then(r => r.data)
export const regenerateTrip = (id) => request.post(`/api/trips/${id}/regenerate`).then(r => r.data)
export const togglePackItem = (id, data) => request.post(`/api/trips/items/${id}/pack`, data || {}).then(r => r.data)
export const packAllItems = (id) => request.post(`/api/trips/${id}/pack-all`).then(r => r.data)
export const saveTripFavorite = (id, data) => request.post(`/api/trips/${id}/save-favorite`, data).then(r => r.data)
export const exportTrip = (id) => request.get(`/api/trips/${id}/export`).then(r => r.data)
