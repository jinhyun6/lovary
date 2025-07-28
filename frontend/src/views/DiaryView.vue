<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Navigation -->
    <nav class="bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Couple Diary
        </h1>
        <div class="flex items-center space-x-6">
          <router-link 
            to="/profile"
            class="text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            Profile
          </router-link>
          <button 
            @click="handleLogout"
            class="text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
    
    <div class="max-w-6xl mx-auto px-6 py-12">
      <!-- Month Navigation -->
      <div class="flex items-center justify-between mb-12">
        <button 
          @click="changeMonth(-1)"
          class="group flex items-center space-x-2 px-4 py-2 rounded-xl hover:bg-white hover:shadow-sm transition-all"
        >
          <svg class="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span class="text-gray-600 group-hover:text-gray-900 font-medium">Previous</span>
        </button>
        
        <h2 class="text-3xl font-bold text-gray-800">
          {{ currentYear }}.{{ String(currentMonth).padStart(2, '0') }}
        </h2>
        
        <button 
          @click="changeMonth(1)"
          class="group flex items-center space-x-2 px-4 py-2 rounded-xl hover:bg-white hover:shadow-sm transition-all"
        >
          <span class="text-gray-600 group-hover:text-gray-900 font-medium">Next</span>
          <svg class="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
      
      <!-- Instructions -->
      <div class="mb-6 text-center">
        <p class="text-sm text-gray-500">
          클릭: 일기 작성 | Shift+클릭: 기념일 설정
        </p>
      </div>
      
      <!-- Photo Upload Section -->
      <div v-if="!monthlyPhoto" class="mb-12 text-center">
        <div 
          class="inline-flex flex-col items-center space-y-4 p-8 bg-white rounded-2xl shadow-sm transition-all"
          :class="{ 'ring-4 ring-gray-300 ring-opacity-50 bg-gray-50': isDragging }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
        >
          <svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-gray-500 font-medium">
            {{ isDragging ? 'Drop your photo here' : 'Drag & drop a photo or click to select' }}
          </p>
          <label class="relative group cursor-pointer">
            <span class="px-6 py-3 bg-gray-800 text-white font-medium rounded-xl inline-block group-hover:bg-gray-900 transition-colors">
              Upload Photo
            </span>
            <input 
              type="file" 
              accept="image/*,.heic,.heif"
              @change="handlePhotoUpload"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </label>
        </div>
      </div>
      
      <!-- Calendar Puzzle -->
      <div 
        class="relative"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
      >
        <CalendarPuzzle
          :year="currentYear"
          :month="currentMonth"
          :photo-url="monthlyPhoto?.photo_url"
          :anniversaries="anniversaries"
          @day-click="handleDayClick"
        />
        
        <!-- Edit Photo Button -->
        <div v-if="monthlyPhoto" class="absolute bottom-4 left-4">
          <label class="group cursor-pointer flex items-center gap-2 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow-md hover:shadow-lg transition-all">
            <svg class="w-4 h-4 text-gray-600 group-hover:text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            <span class="text-sm font-medium text-gray-600 group-hover:text-gray-800">Edit Photo</span>
            <input 
              type="file" 
              accept="image/*,.heic,.heif"
              @change="handlePhotoUpload"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </label>
        </div>
        
        <!-- Drag overlay when dragging over calendar -->
        <div 
          v-if="isDragging && monthlyPhoto" 
          class="absolute inset-0 bg-blue-500 bg-opacity-20 rounded-3xl flex items-center justify-center pointer-events-none"
        >
          <div class="bg-white px-6 py-4 rounded-xl shadow-lg">
            <p class="text-lg font-medium text-gray-800">Drop to replace photo</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Diary Modal -->
    <DiaryModal
      :is-open="isModalOpen"
      :date="selectedDate"
      @close="isModalOpen = false"
      @diary-submitted="handleDiarySubmitted"
    />
    
    <!-- Photo Cropper -->
    <PhotoCropper
      :is-open="isCropperOpen"
      :image-src="cropperImage"
      @close="isCropperOpen = false"
      @crop="handleCrop"
    />
    
    <!-- Anniversary Modal -->
    <AnniversaryModal
      :is-open="isAnniversaryModalOpen"
      :date="anniversaryDate"
      :current-anniversary="currentAnniversary"
      @close="isAnniversaryModalOpen = false"
      @saved="handleAnniversarySaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CalendarPuzzle from '@/components/CalendarPuzzle.vue'
import DiaryModal from '@/components/DiaryModal.vue'
import PhotoCropper from '@/components/PhotoCropperNew.vue'
import AnniversaryModal from '@/components/AnniversaryModal.vue'
import { photosApi } from '@/api/photos'
import { anniversaryApi } from '@/api/anniversary'

const router = useRouter()

// Date management
const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth() + 1)

// Photo management
const monthlyPhoto = ref<any>(null)

// Modal management
const isModalOpen = ref(false)
const selectedDate = ref<{ year: number, month: number, day: number } | null>(null)

// Anniversary modal
const isAnniversaryModalOpen = ref(false)
const anniversaryDate = ref<{ year: number, month: number, day: number } | null>(null)
const currentAnniversary = ref<string>('')
const anniversaries = ref<Record<number, { name: string, date: string }>>({})

// Drag and drop state
const isDragging = ref(false)

// Cropper state
const isCropperOpen = ref(false)
const cropperImage = ref('')
const pendingFile = ref<File | null>(null)

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/')
}

const changeMonth = (delta: number) => {
  currentMonth.value += delta
  
  if (currentMonth.value > 12) {
    currentMonth.value = 1
    currentYear.value++
  } else if (currentMonth.value < 1) {
    currentMonth.value = 12
    currentYear.value--
  }
  
  loadMonthlyPhoto()
  loadAnniversaries()
}

const loadMonthlyPhoto = async () => {
  try {
    monthlyPhoto.value = await photosApi.getMonthlyPhoto(currentYear.value, currentMonth.value)
  } catch (error) {
    console.error('Failed to load monthly photo:', error)
  }
}

const loadAnniversaries = async () => {
  try {
    anniversaries.value = await anniversaryApi.getMonthAnniversaries(currentYear.value, currentMonth.value)
  } catch (error) {
    console.error('Failed to load anniversaries:', error)
  }
}

const handleAnniversarySaved = () => {
  loadAnniversaries()
}

const handlePhotoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Reset input value to allow selecting the same file again
  target.value = ''
  
  // Open cropper instead of direct upload
  openCropper(file)
}

const handleDayClick = (date: { year: number, month: number, day: number }) => {
  // Check if shift key is pressed for anniversary edit
  if ((window.event as MouseEvent)?.shiftKey) {
    anniversaryDate.value = date
    currentAnniversary.value = anniversaries.value[date.day]?.name || ''
    isAnniversaryModalOpen.value = true
  } else {
    selectedDate.value = date
    isModalOpen.value = true
  }
}

const handleDiarySubmitted = () => {
  // Trigger calendar refresh
  // The CalendarPuzzle component will handle this internally
}

const handleDragOver = (event: DragEvent) => {
  isDragging.value = true
}

const handleDragLeave = (event: DragEvent) => {
  isDragging.value = false
}

const handleDrop = async (event: DragEvent) => {
  isDragging.value = false
  
  const files = event.dataTransfer?.files
  if (!files || files.length === 0) return
  
  const file = files[0]
  if (!file.type.startsWith('image/')) {
    alert('Please drop an image file')
    return
  }
  
  // Open cropper instead of direct upload
  openCropper(file)
}

const openCropper = (file: File) => {
  pendingFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    cropperImage.value = result
    isCropperOpen.value = true
  }
  reader.onerror = (error) => {
    console.error('Error reading file:', error)
    alert('Error reading image file')
  }
  reader.readAsDataURL(file)
}

const handleCrop = async (blob: Blob) => {
  if (!pendingFile.value) return
  
  // Create a new File object from the cropped blob
  const croppedFile = new File([blob], pendingFile.value.name, {
    type: 'image/jpeg',
    lastModified: Date.now()
  })
  
  try {
    await photosApi.uploadMonthlyPhoto(currentYear.value, currentMonth.value, croppedFile)
    await loadMonthlyPhoto()
    isCropperOpen.value = false
    pendingFile.value = null
    cropperImage.value = ''
  } catch (error: any) {
    alert(error.response?.data?.detail || '사진 업로드에 실패했습니다.')
  }
}

onMounted(() => {
  loadMonthlyPhoto()
  loadAnniversaries()
})
</script>