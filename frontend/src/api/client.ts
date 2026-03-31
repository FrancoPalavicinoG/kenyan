import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API error]', error.response?.status, error.config?.url, error.message)
    return Promise.reject(error)
  },
)

export default apiClient
