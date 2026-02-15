import api from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface User {
  id: number
  email: string
  username?: string
  full_name?: string
  role: string
  is_active: boolean
  is_seller_approved?: boolean
  is_verified?: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/v1/auth/login', credentials)
    const data = response.data
    
    // Store token
    localStorage.setItem('access_token', data.access_token)
    
    return data
  },

  async register(userData: any): Promise<User> {
    const response = await api.post('/api/v1/auth/register', userData)
    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem('access_token')
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },

  async getCurrentUser(): Promise<User | null> {
    if (!this.isAuthenticated()) {
      return null
    }
    
    const response = await api.get('/api/v1/users/me')
    return response.data
  }
}
