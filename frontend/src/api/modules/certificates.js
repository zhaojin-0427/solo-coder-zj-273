import { request } from '../request'
import { uploadFormData } from '../request'

export const getCertificates = (params = {}) => request.get('/api/certificates', { params }).then(r => r.data)
export const getCertificate = (id) => request.get(`/api/certificates/${id}`).then(r => r.data)
export const createCertificate = (formData) => uploadFormData('/api/certificates', formData)
export const updateCertificate = (id, formData) => uploadFormData(`/api/certificates/${id}`, formData)
export const deleteCertificate = (id) => request.delete(`/api/certificates/${id}`).then(r => r.data)
