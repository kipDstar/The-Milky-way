import axios, { AxiosInstance } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle token expiration
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password })
    return response.data
  }

  // Farmers
  async getFarmers(params?: { search?: string; station_id?: string }) {
    const response = await this.client.get('/farmers', { params })
    return response.data
  }

  async createFarmer(data: any) {
    const response = await this.client.post('/farmers', data)
    return response.data
  }

  // Deliveries
  async getDeliveries(params?: { station_id?: string; date?: string }) {
    const response = await this.client.get('/deliveries', { params })
    return response.data
  }

  async createDelivery(data: any) {
    const response = await this.client.post('/deliveries', data)
    return response.data
  }

  // Reports
  async getDailyReport(report_date: string, station_id?: string) {
    const response = await this.client.get('/reports/daily', {
      params: { report_date, station_id },
    })
    return response.data
  }

  async getMonthlyReport(month: string, farmer_id: string) {
    const response = await this.client.get('/reports/monthly', {
      params: { month, farmer_id },
    })
    return response.data
  }
}

export const api = new ApiService()
