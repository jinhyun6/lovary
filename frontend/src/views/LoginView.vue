<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="container mx-auto px-6 py-12 flex flex-col items-center justify-center min-h-screen">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Welcome Back
        </h1>
      </div>
      
      <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
              placeholder="your@email.com"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>
          
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full px-6 py-3 bg-gray-800 text-white font-medium rounded-xl hover:bg-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isLoading ? 'Logging in...' : 'Login' }}
          </button>
          
          <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        </form>
        
        <div class="mt-8 pt-8 border-t border-gray-100">
          <p class="text-center text-sm text-gray-600">
            Don't have an account?
            <router-link to="/register" class="text-gray-800 hover:text-gray-900 font-medium">
              Sign up
            </router-link>
          </p>
        </div>
      </div>
      
      <router-link to="/" class="mt-8 text-gray-500 hover:text-gray-700 text-sm">
        ← Back to home
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    console.log('Starting login process...')
    const response = await authApi.login({ username: email.value, password: password.value })
    console.log('Login API response:', response)
    console.log('Token received:', !!response.access_token)
    
    localStorage.setItem('token', response.access_token)
    const savedToken = localStorage.getItem('token')
    console.log('Token saved to localStorage:', savedToken)
    console.log('Current URL before navigation:', window.location.href)
    console.log('Router current route:', router.currentRoute.value.path)
    
    // 네비게이션 전에 약간의 지연 추가
    await new Promise(resolve => setTimeout(resolve, 100))
    
    console.log('Attempting navigation to /diary...')
    await router.push('/diary')
    console.log('Router.push completed')
    console.log('Current URL after navigation:', window.location.href)
    console.log('Router current route after nav:', router.currentRoute.value.path)
    
    // 추가 안전장치: 네비게이션이 실패한 경우 직접 리다이렉트
    setTimeout(() => {
      console.log('Checking navigation result...')
      console.log('Current pathname:', window.location.pathname)
      if (window.location.pathname === '/login' || window.location.pathname === '/') {
        console.log('Navigation failed, forcing redirect to /diary')
        window.location.href = '/diary'
      }
    }, 1000)
  } catch (err: any) {
    console.error('Login error:', err)
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>