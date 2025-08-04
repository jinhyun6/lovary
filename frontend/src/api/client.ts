import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Set Content-Type to application/json only if it's not FormData
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json'
  }
  // For FormData, let axios set the Content-Type with boundary automatically
  
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response interceptor - success:', response.config.url)
    return response
  },
  (error) => {
    console.log('API Response interceptor - error:', {
      url: error.config?.url,
      status: error.response?.status,
      currentPath: window.location.pathname
    })
    
    if (error.response?.status === 401) {
      // 로그인 페이지에서는 리다이렉트하지 않음
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        console.log('401 error - removing token and redirecting to login')
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)