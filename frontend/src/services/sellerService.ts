import api from './api'

export interface SellerApplication {
  store_name: string
  seller_bio: string
  seller_address: string
  seller_tax_id?: string
  terms_accepted: boolean
}

export interface SellerApplicationResponse {
  id: number
  email: string
  store_name: string
  seller_bio: string
  seller_address: string
  seller_tax_id?: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  updated_at?: string
}

export interface SellerProfile {
  id: number
  email: string
  username?: string
  full_name?: string
  store_name?: string
  seller_bio?: string
  seller_address?: string
  seller_tax_id?: string
  is_seller_approved: boolean
  seller_verified: boolean
  total_sales: number
  total_products: number
  seller_rating: number
  created_at: string
}

export const sellerService = {
  async applyAsSeller(application: SellerApplication): Promise<SellerApplicationResponse> {
    const response = await api.post('/api/v1/sellers/apply', application)
    return response.data
  },

  async getApplicationStatus(): Promise<SellerApplicationResponse> {
    const response = await api.get('/api/v1/sellers/application-status')
    return response.data
  },

  async getSellerProfile(): Promise<SellerProfile> {
    const response = await api.get('/api/v1/sellers/profile')
    return response.data
  }
}
