import { request } from '../request'

export const getRecommendations = (params = {}) => request.get('/api/recommend', { params }).then(r => r.data)
export const getFavorites = (params = {}) => request.get('/api/favorites', { params }).then(r => r.data)
export const createFavorite = (data) => request.post('/api/favorites', data).then(r => r.data)
export const useFavorite = (id) => request.post(`/api/favorites/${id}/use`).then(r => r.data)
export const deleteFavorite = (id) => request.delete(`/api/favorites/${id}`).then(r => r.data)
