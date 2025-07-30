<template>
  <div 
    v-if="isOpen" 
    class="modal-overlay"
    @click.self="$emit('close')"
  >
    <div class="modal-content" :class="{ 'fullscreen': selectedDiary || showWriteForm }">
      <button 
        @click="handleClose"
        class="close-button"
      >
        ✕
      </button>
      
      <!-- Title List View -->
      <div v-if="!selectedDiary && !showWriteForm">
        <h2 class="modal-title">{{ formattedDate }}</h2>
        
        <div class="diaries-list">
          <!-- My Diary Title -->
          <div class="diary-item">
            <h3 class="diary-author">{{ data?.my_name || '나' }}의 일기</h3>
            <div v-if="data?.my_diary" class="diary-title-card" @click="openDiary('my', data.my_diary)">
              <h4 class="diary-title-text">{{ data.my_diary.title }}</h4>
              <span class="diary-arrow">→</span>
            </div>
            <div v-else-if="data?.can_write" class="diary-action-card" @click="showWriteForm = true">
              <span class="diary-action-text">일기 작성하기</span>
              <span class="diary-arrow">+</span>
            </div>
            <div v-else-if="!data?.my_diary && !data?.can_write" class="diary-expired-card">
              <span class="diary-expired-text">작성하지 않았어요</span>
            </div>
          </div>
          
          <!-- Partner's Diary Title -->
          <div class="diary-item" v-if="current_user?.partner_id">
            <h3 class="diary-author">{{ data?.partner_name || '상대방' }}의 일기</h3>
            <div v-if="data?.partner_diary && data?.my_diary" class="diary-title-card" @click="openDiary('partner', data.partner_diary)">
              <h4 class="diary-title-text">{{ data.partner_diary.title }}</h4>
              <span class="diary-arrow">→</span>
            </div>
            <div v-else-if="data?.partner_diary && !data?.my_diary" class="diary-locked-card">
              <span class="diary-locked-text">당신의 일기를 먼저 작성해주세요 💕</span>
            </div>
            <div v-else-if="!data?.can_write" class="diary-waiting-card">
              <span class="diary-waiting-text">작성하지 않았어요</span>
            </div>
            <div v-else class="diary-waiting-card">
              <span class="diary-waiting-text">아직 작성하지 않았어요</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Full Screen Diary View -->
      <div v-if="selectedDiary && !isEditing" class="fullscreen-diary">
        <button @click="selectedDiary = null" class="back-button">
          ← 목록으로
        </button>
        <div class="diary-header">
          <h3 class="diary-author-name">{{ selectedAuthor }}의 일기</h3>
          <h2 class="diary-full-title">{{ selectedDiary.title }}</h2>
        </div>
        <div class="diary-full-content">
          <p>{{ selectedDiary.content }}</p>
        </div>
        <!-- Edit button for own diary if within edit time -->
        <button 
          v-if="isMyDiary && data?.can_write" 
          @click="startEdit"
          class="edit-button"
        >
          수정하기
        </button>
      </div>
      
      <!-- Write/Edit Form (Full Screen) -->
      <div v-if="showWriteForm || isEditing" class="fullscreen-diary">
        <button @click="cancelEdit" class="back-button">
          ← {{ isEditing ? '취소' : '목록으로' }}
        </button>
        <div class="diary-header">
          <h3 class="diary-author-name">{{ data?.my_name || '나' }}의 일기</h3>
        </div>
        <form @submit.prevent="submitDiary" class="diary-write-form">
          <input
            v-model="newDiary.title"
            type="text"
            placeholder="제목"
            required
            class="diary-input"
          />
          <textarea
            v-model="newDiary.content"
            placeholder="오늘은 어떤 하루였나요?"
            required
            rows="20"
            class="diary-textarea"
          ></textarea>
          <button 
            type="submit"
            :disabled="isSubmitting"
            class="submit-button"
          >
            {{ isSubmitting ? '저장 중...' : (isEditing ? '수정' : '저장') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { diaryApi } from '@/api/diary'
import { usersApi } from '@/api/users'

interface DiaryData {
  date: string
  my_diary?: any
  partner_diary?: any
  my_name: string
  partner_name: string
  can_write: boolean
}

const props = defineProps<{
  isOpen: boolean
  date: { year: number, month: number, day: number } | null
}>()

const emit = defineEmits<{
  close: []
  diarySubmitted: []
}>()

const data = ref<DiaryData | null>(null)
const current_user = ref<any>(null)
const newDiary = ref({
  title: '',
  content: ''
})
const isSubmitting = ref(false)
const selectedDiary = ref<any>(null)
const selectedAuthor = ref('')
const showWriteForm = ref(false)
const isEditing = ref(false)
const editingDiaryId = ref<number | null>(null)

const formattedDate = computed(() => {
  if (!props.date) return ''
  return `${props.date.year}년 ${props.date.month}월 ${props.date.day}일`
})

const isMyDiary = computed(() => {
  return selectedDiary.value && selectedAuthor.value === (data.value?.my_name || '나')
})

const loadUserData = async () => {
  try {
    current_user.value = await usersApi.getMe()
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

const loadDiaryData = async () => {
  if (!props.date) return
  
  try {
    data.value = await diaryApi.getDayDiaries(
      props.date.year,
      props.date.month,
      props.date.day
    )
  } catch (error) {
    console.error('Failed to load diary data:', error)
  }
}

const openDiary = (type: 'my' | 'partner', diary: any) => {
  selectedDiary.value = diary
  selectedAuthor.value = type === 'my' ? (data.value?.my_name || '나') : (data.value?.partner_name || '상대방')
}

const handleClose = () => {
  selectedDiary.value = null
  selectedAuthor.value = ''
  showWriteForm.value = false
  emit('close')
}

const submitDiary = async () => {
  if (!data.value?.can_write && !isEditing.value) return
  
  isSubmitting.value = true
  try {
    if (isEditing.value && editingDiaryId.value) {
      // Update existing diary
      await diaryApi.updateDiary(editingDiaryId.value, {
        title: newDiary.value.title,
        content: newDiary.value.content
      })
    } else {
      // Create new diary
      await diaryApi.createDiary({
        title: newDiary.value.title,
        content: newDiary.value.content
      })
    }
    
    // Reload data
    await loadDiaryData()
    
    // Reset form and go back to list
    newDiary.value = { title: '', content: '' }
    showWriteForm.value = false
    isEditing.value = false
    editingDiaryId.value = null
    selectedDiary.value = null
    
    emit('diarySubmitted')
  } catch (error: any) {
    alert(error.response?.data?.detail || '일기 저장에 실패했습니다.')
  } finally {
    isSubmitting.value = false
  }
}

const startEdit = () => {
  if (!selectedDiary.value || !data.value?.can_write) return
  
  newDiary.value = {
    title: selectedDiary.value.title,
    content: selectedDiary.value.content
  }
  editingDiaryId.value = selectedDiary.value.id
  isEditing.value = true
}

const cancelEdit = () => {
  if (isEditing.value) {
    isEditing.value = false
    editingDiaryId.value = null
    newDiary.value = { title: '', content: '' }
  } else {
    showWriteForm.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadUserData()
    loadDiaryData()
  } else {
    // Reset state when modal closes
    selectedDiary.value = null
    selectedAuthor.value = ''
    showWriteForm.value = false
    isEditing.value = false
    editingDiaryId.value = null
    newDiary.value = { title: '', content: '' }
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 3rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.3s ease;
}

.modal-content.fullscreen {
  max-width: 900px;
  height: 90vh;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.close-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: #f3f4f6;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.2s;
}

.close-button:hover {
  background: #e5e7eb;
  color: #374151;
}

.back-button {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.2s;
}

.back-button:hover {
  color: #374151;
}

.modal-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: #111827;
  letter-spacing: -0.02em;
}

.diaries-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.diary-item {
  background: #f9fafb;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.diary-author {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #6b7280;
  letter-spacing: -0.01em;
}

.diary-title-card,
.diary-action-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.diary-title-card:hover,
.diary-action-card:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
  transform: translateY(-1px);
}

.diary-title-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.diary-action-text {
  font-size: 1.125rem;
  color: #6366f1;
  font-weight: 500;
}

.diary-arrow {
  color: #9ca3af;
  font-size: 1.25rem;
  transition: transform 0.2s;
}

.diary-title-card:hover .diary-arrow,
.diary-action-card:hover .diary-arrow {
  transform: translateX(4px);
}

.diary-expired-card,
.diary-locked-card,
.diary-waiting-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  text-align: center;
}

.diary-expired-text,
.diary-waiting-text {
  color: #9ca3af;
  font-size: 0.975rem;
}

.diary-locked-text {
  color: #ef4444;
  font-weight: 500;
  font-size: 0.975rem;
}

.diary-locked-card {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #fecaca;
}

/* Full Screen Diary View */
.fullscreen-diary {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.diary-header {
  margin-bottom: 2rem;
}

.diary-author-name {
  font-size: 1rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.diary-full-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.diary-full-content {
  flex: 1;
  overflow-y: auto;
  background: #f9fafb;
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid #e5e7eb;
}

.diary-full-content p {
  font-size: 1.125rem;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
}

/* Write Form */
.diary-write-form {
  height: calc(100% - 5rem);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.diary-input,
.diary-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
  background: white;
}

.diary-input:focus,
.diary-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.diary-textarea {
  flex: 1;
  resize: none;
  line-height: 1.6;
}

.submit-button {
  background: #1f2937;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-end;
}

.submit-button:hover:not(:disabled) {
  background: #111827;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-button {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  background: transparent;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.edit-button:hover {
  background: #f9fafb;
  color: #374151;
  border-color: #d1d5db;
}

@media (max-width: 768px) {
  .modal-content {
    padding: 2rem;
  }
  
  .diary-full-title {
    font-size: 2rem;
  }
}
</style>