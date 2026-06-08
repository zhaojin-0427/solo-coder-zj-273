import axios from 'axios'

const request = axios.create({
  baseURL: '/',
  timeout: 15000
})

export const getMeta = () => request.get('/api/meta').then(r => r.data)

export const getAccessories = (params = {}) => request.get('/api/accessories', { params }).then(r => r.data)
export const getAccessory = (id) => request.get(`/api/accessories/${id}`).then(r => r.data)
export const createAccessory = (formData) => request.post('/api/accessories', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
}).then(r => r.data)
export const updateAccessory = (id, formData) => request.put(`/api/accessories/${id}`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
}).then(r => r.data)
export const deleteAccessory = (id) => request.delete(`/api/accessories/${id}`).then(r => r.data)
export const wearAccessory = (id) => request.post(`/api/accessories/${id}/wear`).then(r => r.data)

export const getStorageLocations = () => request.get('/api/storage_locations').then(r => r.data)

export const getRecommendations = (params = {}) => request.get('/api/recommend', { params }).then(r => r.data)

export const getFavorites = (params = {}) => request.get('/api/favorites', { params }).then(r => r.data)
export const createFavorite = (data) => request.post('/api/favorites', data).then(r => r.data)
export const useFavorite = (id) => request.post(`/api/favorites/${id}/use`).then(r => r.data)
export const deleteFavorite = (id) => request.delete(`/api/favorites/${id}`).then(r => r.data)

export const getStatistics = () => request.get('/api/statistics').then(r => r.data)

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

export const setMaintenanceDate = (id, data) => request.post(`/api/accessories/${id}/set-maintenance`, data).then(r => r.data)

export const getTrackingSummary = () => request.get('/api/tracking/summary').then(r => r.data)
