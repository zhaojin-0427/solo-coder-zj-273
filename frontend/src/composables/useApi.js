import axios from 'axios'
import { ElMessage } from 'element-plus'

export const request = axios.create({
  baseURL: '/',
  timeout: 15000
})

export function apiErrorHandler(err) {
  const msg = err?.response?.data?.message || err?.message || '请求失败，请稍后重试'
  ElMessage.error(msg)
}

export function useApi() {
  const get = (url, params = {}) => {
    return request.get(url, { params })
      .then(r => r.data)
      .catch(err => {
        apiErrorHandler(err)
        throw err
      })
  }

  const post = (url, data = {}, config = {}) => {
    return request.post(url, data, config)
      .then(r => r.data)
      .catch(err => {
        apiErrorHandler(err)
        throw err
      })
  }

  const put = (url, data = {}, config = {}) => {
    return request.put(url, data, config)
      .then(r => r.data)
      .catch(err => {
        apiErrorHandler(err)
        throw err
      })
  }

  const del = (url) => {
    return request.delete(url)
      .then(r => r.data)
      .catch(err => {
        apiErrorHandler(err)
        throw err
      })
  }

  return { request, get, post, put, delete: del }
}
