import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'
import { API_URL } from '@/config'

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt')
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  }
)

export default api

export const get = <T>(url: string, config?: AxiosRequestConfig) => api.get<T>(url, config)
export const post = <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => api.post<T>(url, data, config)
export const put = <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => api.put<T>(url, data, config)
export const patch = <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => api.patch<T>(url, data, config)
export const del = <T>(url: string, config?: AxiosRequestConfig) => api.delete<T>(url, config)
