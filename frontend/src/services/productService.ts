import api from './api'
import type { AxiosProgressEvent } from 'axios'

export interface Product {
  id: number
  title: string
  description: string
  short_description?: string
  price: number
  compare_at_price?: number
  category?: string
  tags?: string
  sku?: string
  status: 'draft' | 'pending' | 'active' | 'suspended' | 'archived'
  is_active: boolean
  is_featured: boolean
  stock_quantity: number
  download_limit: number
  file_url?: string
  file_name?: string
  file_size?: number
  file_type?: string
  thumbnail_url?: string
  preview_url?: string
  sample_file_url?: string
  sold_count: number
  average_rating: number
  review_count: number
  seller_id: number
  created_at: string
  updated_at: string
  published_at?: string
}

export interface ProductList {
  id: number
  title: string
  short_description?: string
  price: number
  compare_at_price?: number
  thumbnail_url?: string
  seller_name?: string
  seller_rating: number
  sold_count: number
  average_rating: number
  review_count: number
  is_featured: boolean
  created_at: string
}

export interface ProductCreate {
  title: string
  description: string
  short_description?: string
  price: number
  compare_at_price?: number
  category?: string
  tags?: string
  sku?: string
  status: 'draft' | 'pending' | 'active' | 'suspended' | 'archived'
  is_active: boolean
  is_featured: boolean
  stock_quantity: number
  download_limit: number
}

export interface ProductUpdate {
  title?: string
  description?: string
  short_description?: string
  price?: number
  compare_at_price?: number
  category?: string
  tags?: string
  sku?: string
  status?: 'draft' | 'pending' | 'active' | 'suspended' | 'archived'
  is_active?: boolean
  is_featured?: boolean
  stock_quantity?: number
  download_limit?: number
}

export interface ProductFileUpload {
  file_url: string
  file_name: string
  file_size: number
  file_type: string
}

export interface ProductFilters {
  category?: string
  search?: string
  sort_by?: 'created_at' | 'price' | 'sold_count' | 'rating'
  sort_order?: 'asc' | 'desc'
  skip?: number
  limit?: number
}

export const productService = {
  async getMyProducts(filters?: ProductFilters): Promise<Product[]> {
    const params = new URLSearchParams()
    
    if (filters?.skip) params.append('skip', filters.skip.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())
    
    const response = await api.get(`/api/v1/products/me?${params}`)
    return response.data
  },

  async getPublicProducts(filters?: ProductFilters): Promise<ProductList[]> {
    const params = new URLSearchParams()
    
    if (filters?.category) params.append('category', filters.category)
    if (filters?.search) params.append('search', filters.search)
    if (filters?.sort_by) params.append('sort_by', filters.sort_by)
    if (filters?.sort_order) params.append('sort_order', filters.sort_order)
    if (filters?.skip) params.append('skip', filters.skip.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())
    
    const response = await api.get(`/api/v1/products?${params}`)
    return response.data
  },

  async getProduct(id: number): Promise<Product> {
    const response = await api.get(`/api/v1/products/${id}`)
    return response.data
  },

  async createProduct(
    productData: ProductCreate,
    file: File,
    thumbnail?: File,
    onProgress?: (progress: number) => void
  ): Promise<Product> {
    const formData = new FormData()
    
    // Add product fields
    Object.entries(productData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value.toString())
      }
    })
    
    // Add files
    formData.append('file', file)
    if (thumbnail) {
      formData.append('thumbnail', thumbnail)
    }
    
    const response = await api.post('/api/v1/products', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  },

  async updateProduct(
    id: number,
    productData: ProductUpdate,
    file?: File,
    thumbnail?: File,
    onProgress?: (progress: number) => void
  ): Promise<Product> {
    const formData = new FormData()
    
    // Add product fields
    Object.entries(productData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value.toString())
      }
    })
    
    // Add files if provided
    if (file) formData.append('file', file)
    if (thumbnail) formData.append('thumbnail', thumbnail)
    
    const response = await api.put(`/api/v1/products/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  },

  async deleteProduct(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/v1/products/${id}`)
    return response.data
  },

  async uploadFile(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ProductFileUpload> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/v1/products/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  }
}
