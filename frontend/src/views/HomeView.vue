<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="container mx-auto px-6 py-12 flex flex-col items-center justify-center min-h-screen">
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-4">
          Lovary
        </h1>
        <p class="text-lg text-gray-600">Share your daily moments with your loved one</p>
      </div>
      
      <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <div class="space-y-4">
          <router-link 
            to="/login" 
            class="block w-full px-6 py-3 bg-gray-800 text-white text-center font-medium rounded-xl hover:bg-gray-900 transition-colors"
          >
            Login
          </router-link>
          <router-link 
            to="/register" 
            class="block w-full px-6 py-3 bg-white border-2 border-gray-200 text-gray-700 text-center font-medium rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all"
          >
            Create Account
          </router-link>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-100">
          <p class="text-center text-sm text-gray-500">
            Write daily diaries and unlock beautiful memories together
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>