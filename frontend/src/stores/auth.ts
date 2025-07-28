import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const router = useRouter()

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ username: email, password })
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      router.push('/diary')
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const register = async (email: string, password: string) => {
    try {
      await authApi.register({ email, password })
      // Auto login after register
      await login(email, password)
    } catch (error) {
      console.error('Register failed:', error)
      throw error
    }
  }

  const logout = () => {
    token.value = null
    localStorage.removeItem('token')
    router.push('/')
  }

  const isAuthenticated = () => {
    return !!token.value
  }

  return {
    token,
    login,
    register,
    logout,
    isAuthenticated
  }
})