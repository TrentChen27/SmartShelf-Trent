import axios from 'axios'

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && (error.response.status === 401 || error.response.status === 422)) {
      // Token is invalid or expired
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('userRole')

      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        console.warn('Authentication failed, redirecting to login...')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default instance
