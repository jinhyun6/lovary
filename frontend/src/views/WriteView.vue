<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800">일기 작성</h1>
        <router-link 
          to="/diary"
          class="text-gray-600 hover:text-gray-800"
        >
          돌아가기
        </router-link>
      </div>
    </nav>
    
    <div class="max-w-2xl mx-auto px-4 py-8">
      <form @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow p-6">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-medium mb-2">
            제목
          </label>
          <input
            v-model="title"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            placeholder="오늘의 제목"
          />
        </div>
        
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-medium mb-2">
            내용
          </label>
          <textarea
            v-model="content"
            required
            rows="10"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            placeholder="오늘 하루는 어땠나요?"
          ></textarea>
        </div>
        
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full bg-pink-500 text-white py-2 rounded-lg hover:bg-pink-600 transition disabled:opacity-50"
        >
          {{ isLoading ? '저장 중...' : '일기 저장' }}
        </button>
        <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { diaryApi } from '@/api/diary'

const router = useRouter()
const title = ref('')
const content = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    await diaryApi.createDiary({ title: title.value, content: content.value })
    router.push('/diary')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '일기 저장에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>