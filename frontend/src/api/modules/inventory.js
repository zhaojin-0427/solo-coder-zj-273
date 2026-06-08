import { request } from '../request'

export const getInventoryBatches = (params = {}) => request.get('/api/inventory/batches', { params }).then(r => r.data)
export const getInventoryBatch = (id) => request.get(`/api/inventory/batches/${id}`).then(r => r.data)
export const createInventoryBatch = (data) => request.post('/api/inventory/batches', data).then(r => r.data)
export const completeInventoryBatch = (id) => request.post(`/api/inventory/batches/${id}/complete`).then(r => r.data)
export const deleteInventoryBatch = (id) => request.delete(`/api/inventory/batches/${id}`).then(r => r.data)
export const checkInventoryItem = (id, data) => request.post(`/api/inventory/items/${id}/check`, data || {}).then(r => r.data)
export const getInventoryExceptions = (params = {}) => request.get('/api/inventory/exceptions', { params }).then(r => r.data)
export const getInventoryException = (id) => request.get(`/api/inventory/exceptions/${id}`).then(r => r.data)
export const createInventoryException = (data) => request.post('/api/inventory/exceptions', data).then(r => r.data)
export const resolveInventoryException = (id, data) => request.post(`/api/inventory/exceptions/${id}/resolve`, data || {}).then(r => r.data)
export const deleteInventoryException = (id) => request.delete(`/api/inventory/exceptions/${id}`).then(r => r.data)
