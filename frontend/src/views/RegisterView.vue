<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="container mx-auto px-6 py-12 flex flex-col items-center justify-center min-h-screen">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Create Account
        </h1>
      </div>
      
      <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Name
            </label>
            <input
              v-model="name"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
              placeholder="Your name"
            />
          </div>
          
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
              minlength="6"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>
          
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full px-6 py-3 bg-gray-800 text-white font-medium rounded-xl hover:bg-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isLoading ? 'Creating account...' : 'Sign up' }}
          </button>
          
          <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        </form>
        
        <div class="mt-8 pt-8 border-t border-gray-100">
          <p class="text-center text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="text-gray-800 hover:text-gray-900 font-medium">
              Login
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
const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    await authApi.register({ 
      email: email.value, 
      password: password.value,
      name: name.value
    })
    // Auto login after register
    const response = await authApi.login({ username: email.value, password: password.value })
    localStorage.setItem('token', response.access_token)
    
    // 로그인과 동일한 네비게이션 패턴 사용
    await new Promise(resolve => setTimeout(resolve, 100))
    await router.push('/diary')
    
    // 추가 안전장치
    setTimeout(() => {
      if (window.location.pathname === '/register') {
        window.location.href = '/diary'
      }
    }, 1000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>