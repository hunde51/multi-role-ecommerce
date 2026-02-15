import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { SellerApplication } from '../services/sellerService'
import { sellerService } from '../services/sellerService'

const SellerApplicationPage: React.FC = () => {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<SellerApplication>({
    store_name: '',
    seller_bio: '',
    seller_address: '',
    seller_tax_id: '',
    terms_accepted: false
  })
  const [errors, setErrors] = useState<Partial<SellerApplication>>({})

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
    
    // Clear error for this field
    if (errors[name as keyof SellerApplication]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<SellerApplication> = {}

    if (!formData.store_name || formData.store_name.length < 2) {
      newErrors.store_name = 'Store name must be at least 2 characters'
    }
    if (!formData.seller_bio || formData.seller_bio.length < 10) {
      newErrors.seller_bio = 'Description must be at least 10 characters'
    }
    if (!formData.seller_address || formData.seller_address.length < 5) {
      newErrors.seller_address = 'Address must be at least 5 characters'
    }
    if (!formData.terms_accepted) {
      newErrors.terms_accepted = 'You must accept the terms and conditions' as any
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      setIsSubmitting(true)
      await sellerService.applyAsSeller(formData)
      alert('Seller application submitted successfully!')
      navigate('/dashboard')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit application')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Become a Seller
            </h1>
            <p className="text-gray-600">
              Start selling your digital products on our platform. Fill out the application below to get started.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Store Name */}
            <div>
              <label htmlFor="store_name" className="block text-sm font-medium text-gray-700 mb-2">
                Store Name *
              </label>
              <input
                type="text"
                id="store_name"
                name="store_name"
                value={formData.store_name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your store name"
              />
              {errors.store_name && (
                <p className="mt-1 text-sm text-red-600">{errors.store_name}</p>
              )}
            </div>

            {/* Seller Bio */}
            <div>
              <label htmlFor="seller_bio" className="block text-sm font-medium text-gray-700 mb-2">
                Store Description *
              </label>
              <textarea
                id="seller_bio"
                name="seller_bio"
                rows={4}
                value={formData.seller_bio}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe your store and what kind of products you sell..."
              />
              {errors.seller_bio && (
                <p className="mt-1 text-sm text-red-600">{errors.seller_bio}</p>
              )}
            </div>

            {/* Seller Address */}
            <div>
              <label htmlFor="seller_address" className="block text-sm font-medium text-gray-700 mb-2">
                Business Address *
              </label>
              <textarea
                id="seller_address"
                name="seller_address"
                rows={3}
                value={formData.seller_address}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your business address"
              />
              {errors.seller_address && (
                <p className="mt-1 text-sm text-red-600">{errors.seller_address}</p>
              )}
            </div>

            {/* Tax ID (Optional) */}
            <div>
              <label htmlFor="seller_tax_id" className="block text-sm font-medium text-gray-700 mb-2">
                Tax ID / VAT Number (Optional)
              </label>
              <input
                type="text"
                id="seller_tax_id"
                name="seller_tax_id"
                value={formData.seller_tax_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your tax ID or VAT number"
              />
              {errors.seller_tax_id && (
                <p className="mt-1 text-sm text-red-600">{errors.seller_tax_id}</p>
              )}
            </div>

            {/* Terms and Conditions */}
            <div className="bg-gray-50 p-4 rounded-md">
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Terms and Conditions
              </h3>
              <div className="text-sm text-gray-600 space-y-2 mb-4">
                <p>• You must be the legal owner of all products you sell</p>
                <p>• Products must comply with our content guidelines</p>
                <p>• You are responsible for customer support and product quality</p>
                <p>• We charge a 10% commission on all sales</p>
                <p>• Payments are processed within 7 days of purchase</p>
                <p>• We reserve the right to remove any products that violate our terms</p>
              </div>
              
              <div className="flex items-start">
                <input
                  type="checkbox"
                  id="terms_accepted"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleInputChange}
                  className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="terms_accepted" className="ml-2 text-sm text-gray-700">
                  I have read and agree to the terms and conditions *
                </label>
              </div>
              {errors.terms_accepted && (
                <p className="mt-1 text-sm text-red-600">{errors.terms_accepted}</p>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !formData.terms_accepted}
                className="px-6 py-2 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default SellerApplicationPage
