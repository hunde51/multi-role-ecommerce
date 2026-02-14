import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authService, type User } from '../services/authService'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage, {
        serialize: (state) => JSON.stringify(state),
        deserialize: (str) => JSON.parse(str),
      }),
    },
    {
      name: 'auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: !!state.token,
      }),
    }
  )
)(

  (set, get) => ({
    login: async (email, password) => {
      set({ isLoading: true })
      try {
        const response = await authService.login({ email, password })
        const user = response.user
        const token = response.access_token
        
        set({ 
          user, 
          token, 
          isAuthenticated: true, 
          isLoading: false 
        })
      } catch (error) {
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false, 
          isLoading: false 
        })
        throw error
      }
    },

    register: async (userData) => {
      set({ isLoading: true })
      try {
        const user = await authService.register(userData)
        set({ 
          user, 
          isAuthenticated: true, 
          isLoading: false 
        })
      } catch (error) {
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false, 
          isLoading: false 
        })
        throw error
      }
    },

    logout: () => {
      authService.logout()
      set({ 
        user: null, 
        token: null, 
        isAuthenticated: false, 
        isLoading: false 
      })
    },

    setUser: (user) => set({ user }),

    setLoading: (isLoading) => set({ isLoading }),
  })
)
