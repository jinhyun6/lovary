<template>
  <div 
    v-if="isOpen" 
    class="modal-overlay"
    @click.self="$emit('close')"
  >
    <div class="modal-content">
      <button 
        @click="$emit('close')"
        class="close-button"
      >
        ✕
      </button>
      
      <h2 class="modal-title">기념일 설정</h2>
      <p class="modal-date">{{ formattedDate }}</p>
      
      <form @submit.prevent="saveAnniversary" class="anniversary-form">
        <input
          v-model="anniversaryName"
          type="text"
          placeholder="기념일 이름을 입력하세요 (예: 첫 만남)"
          class="anniversary-input"
          maxlength="20"
        />
        
        <div class="button-group">
          <button
            type="submit"
            :disabled="!anniversaryName.trim() || isSaving"
            class="save-button"
          >
            {{ isSaving ? '저장 중...' : '저장' }}
          </button>
          
          <button
            v-if="hasAnniversary"
            type="button"
            @click="deleteAnniversary"
            :disabled="isSaving"
            class="delete-button"
          >
            삭제
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { anniversaryApi } from '@/api/anniversary'

const props = defineProps<{
  isOpen: boolean
  date: { year: number, month: number, day: number } | null
  currentAnniversary?: string
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const anniversaryName = ref('')
const isSaving = ref(false)

const formattedDate = computed(() => {
  if (!props.date) return ''
  return `${props.date.year}년 ${props.date.month}월 ${props.date.day}일`
})

const hasAnniversary = computed(() => {
  return !!props.currentAnniversary
})

const saveAnniversary = async () => {
  if (!props.date || !anniversaryName.value.trim()) return
  
  isSaving.value = true
  try {
    const dateStr = `${props.date.year}-${String(props.date.month).padStart(2, '0')}-${String(props.date.day).padStart(2, '0')}`
    await anniversaryApi.createOrUpdate({
      date: dateStr,
      name: anniversaryName.value.trim()
    })
    
    emit('saved')
    emit('close')
  } catch (error) {
    alert('기념일 저장에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

const deleteAnniversary = async () => {
  if (!confirm('이 기념일을 삭제하시겠습니까?')) return
  
  isSaving.value = true
  try {
    // Note: We need to get the anniversary ID somehow
    // For now, we'll just clear the name and save
    anniversaryName.value = ''
    await saveAnniversary()
  } catch (error) {
    alert('기념일 삭제에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    anniversaryName.value = props.currentAnniversary || ''
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
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.3s ease;
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
  top: 1rem;
  right: 1rem;
  background: #f3f4f6;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  transition: all 0.2s;
}

.close-button:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #111827;
}

.modal-date {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.anniversary-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.anniversary-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
}

.anniversary-input:focus {
  outline: none;
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
}

.button-group {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.save-button {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.delete-button {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-button:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.delete-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>