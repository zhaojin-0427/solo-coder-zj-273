import { request } from '../request'
import { uploadFormData } from '../request'

export const getAccessories = (params = {}) => request.get('/api/accessories', { params }).then(r => r.data)
export const getAccessory = (id) => request.get(`/api/accessories/${id}`).then(r => r.data)
export const createAccessory = (formData) => uploadFormData('/api/accessories', formData)
export const updateAccessory = (id, formData) => uploadFormData(`/api/accessories/${id}`, formData)
export const deleteAccessory = (id) => request.delete(`/api/accessories/${id}`).then(r => r.data)
export const wearAccessory = (id) => request.post(`/api/accessories/${id}/wear`).then(r => r.data)
export const setMaintenanceDate = (id, data) => request.post(`/api/accessories/${id}/set-maintenance`, data).then(r => r.data)
export const getStorageLocations = () => request.get('/api/storage_locations').then(r => r.data)
