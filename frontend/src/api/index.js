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
