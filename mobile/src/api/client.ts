import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error(
      'API Error:',
      error.response?.status,
      error.response?.data ?? error.message
    )
    return Promise.reject(error)
  }
)

export default apiClient
