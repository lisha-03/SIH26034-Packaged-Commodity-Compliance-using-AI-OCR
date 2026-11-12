import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

export default api

export function errorMessage(err, fallback = 'Something went wrong. Please try again.') {
  return err?.response?.data?.error || fallback
}
