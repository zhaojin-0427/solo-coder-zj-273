import { request } from '../composables/useApi'

export { request }

export const uploadFormData = (url, formData) => {
  return request.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(r => r.data)
}
