import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { authService } from '../services/authService'
import type { User } from '../services/authService'

const Navigation: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initUser = async () => {
      try {
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch (error) {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    initUser()
  }, [])

  const handleLogout = async () => {
    await authService.logout()
    setUser(null)
    navigate('/login')
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  if (loading) {
    return (
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="animate-pulse bg-gray-200 h-8 w-32 rounded"></div>
            </div>
          </div>
        </div>
      </nav>
    )
  }

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              DigitalMarket
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/products"
              className={`text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/products') ? 'bg-gray-100' : ''
              }`}
            >
              Browse Products
            </Link>

            {user ? (
              <>
                {/* Seller-specific links */}
                {user.role === 'seller' && user.is_seller_approved && (
                  <>
                    <Link
                      to="/dashboard/products"
                      className={`text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium ${
                        isActive('/dashboard/products') ? 'bg-gray-100' : ''
                      }`}
                    >
                      Seller Dashboard
                    </Link>
                    <Link
                      to="/dashboard/products/new"
                      className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Add Product
                    </Link>
                  </>
                )}

                {/* Customer who wants to become seller */}
                {user.role === 'buyer' && (
                  <Link
                    to="/become-seller"
                    className="bg-green-600 text-white hover:bg-green-700 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Become a Seller
                  </Link>
                )}

                {/* Pending seller application */}
                {user.role === 'seller' && !user.is_seller_approved && (
                  <div className="text-yellow-600 px-3 py-2 rounded-md text-sm font-medium bg-yellow-50">
                    Application Pending
                  </div>
                )}

                {/* Admin links */}
                {user.role === 'admin' && (
                  <>
                    <Link
                      to="/admin/sellers"
                      className={`text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium ${
                        isActive('/admin/sellers') ? 'bg-gray-100' : ''
                      }`}
                    >
                      Admin Dashboard
                    </Link>
                  </>
                )}
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => navigate('/menu')}
              className="text-gray-700 hover:text-gray-900 p-2 rounded-md"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* User menu (desktop) */}
          {user && (
            <div className="hidden md:flex items-center space-x-4">
              <div className="relative group">
                <button className="flex items-center text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  <span className="mr-2">{user.username || user.email}</span>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {/* Dropdown menu */}
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  <Link
                    to="/dashboard/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Profile
                  </Link>
                  {user.role === 'seller' && user.is_seller_approved && (
                    <Link
                      to="/dashboard/sales"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Sales Analytics
                    </Link>
                  )}
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navigation
