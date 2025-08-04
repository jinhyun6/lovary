<template>
  <div class="calendar-puzzle-container">
    <!-- Days of week header -->
    <div class="calendar-header">
      <div v-for="day in daysOfWeek" :key="day" class="day-header">
        {{ day }}
      </div>
    </div>
    
    <!-- Calendar grid -->
    <div 
      class="calendar-grid"
      @mouseenter="showDates = true"
      @mouseleave="showDates = false"
    >
      <div
        v-for="cell in calendarCells"
        :key="`${cell.row}-${cell.col}`"
        :class="[
          'calendar-cell',
          cell.isValid ? 'valid-cell' : 'empty-cell',
          cell.status,
          { 'today': cell.isToday }
        ]"
        @click="cell.isValid && handleCellClick(cell, $event)"
      >
        <!-- Date number in top-left corner -->
        <div v-if="cell.isValid" class="date-number">{{ cell.day }}</div>
        
        <!-- Anniversary name in center -->
        <div v-if="cell.isValid && cell.anniversary" class="anniversary-name">
          {{ cell.anniversary }}
        </div>
        
        <!-- Puzzle view -->
        <div v-if="cell.isValid" class="puzzle-piece">
          <!-- Future dates - show image full size -->
          <div v-if="cell.status === 'future'" class="puzzle-back">
            <img src="/heart-music-icon.png" alt="" class="heart-music-icon" />
          </div>
          
          <!-- Past/Today dates - photo piece -->
          <div 
            v-else 
            class="photo-piece"
            :class="{ 'incomplete': !cell.isComplete }"
            :style="getPhotoStyle(cell)"
          >
            <div v-if="!cell.isComplete" class="incomplete-overlay"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { diaryApi } from '@/api/diary'

interface CalendarCell {
  row: number
  col: number
  day: number | null
  isValid: boolean
  status: 'past' | 'today' | 'future' | null
  isComplete: boolean
  isToday: boolean
  date?: string
  anniversary?: string
}

const props = defineProps<{
  year: number
  month: number
  photoUrl?: string
  anniversaries?: Record<number, { name: string, date: string }>
}>()

const emit = defineEmits<{
  dayClick: [date: { year: number, month: number, day: number }]
}>()

const showDates = ref(false)
const monthData = ref<Record<number, any>>({})
const daysOfWeek = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

const calendarCells = computed(() => {
  const cells: CalendarCell[] = []
  const firstDay = new Date(props.year, props.month - 1, 1).getDay()
  const daysInMonth = new Date(props.year, props.month, 0).getDate()
  
  // Calculate exact number of rows needed
  const totalCells = Math.ceil((firstDay + daysInMonth) / 7) * 7
  
  let dayCounter = 1
  
  for (let i = 0; i < totalCells; i++) {
    const row = Math.floor(i / 7)
    const col = i % 7
    
    if (i >= firstDay && dayCounter <= daysInMonth) {
      const dayData = monthData.value[dayCounter] || {}
      const anniversary = props.anniversaries?.[dayCounter]
      cells.push({
        row,
        col,
        day: dayCounter,
        isValid: true,
        status: dayData.status || 'future',
        isComplete: dayData.is_complete || false,
        isToday: dayData.status === 'today',
        date: dayData.date,
        anniversary: anniversary?.name
      })
      dayCounter++
    } else {
      cells.push({
        row,
        col,
        day: null,
        isValid: false,
        status: null,
        isComplete: false,
        isToday: false
      })
    }
  }
  
  return cells
})

const getPhotoStyle = (cell: CalendarCell) => {
  if (!props.photoUrl || !cell.isValid) return {}
  
  // Only apply photo style to past/today cells, not future cells
  if (cell.status === 'future') return {}
  
  // The cropped image is 700x600 (7:6 ratio)
  // We scale it up 7x horizontally and 6x vertically so each cell shows 1/7 x 1/6
  
  // For background-position with percentages:
  // 0% = align start, 100% = align end
  // With 700% size, we have 6 "steps" to move the image
  const stepX = cell.col * (100 / 6)
  const stepY = cell.row * (100 / 5)
  
  return {
    backgroundImage: `url(${props.photoUrl})`,
    backgroundSize: '700% 600%',
    backgroundPosition: `${stepX}% ${stepY}%`,
    backgroundRepeat: 'no-repeat'
  }
}

const handleCellClick = (cell: CalendarCell, event: MouseEvent) => {
  if (cell.day) {
    // Allow anniversary clicks on all dates (including future)
    // But only allow diary clicks on non-future dates
    if (event.shiftKey || cell.status !== 'future') {
      emit('dayClick', {
        year: props.year,
        month: props.month,
        day: cell.day
      })
    }
  }
}

const loadMonthData = async () => {
  try {
    monthData.value = await diaryApi.getMonthDiaries(props.year, props.month)
  } catch (error) {
    console.error('Failed to load month data:', error)
  }
}

onMounted(() => {
  loadMonthData()
})

// Watch for props changes
watch(() => [props.year, props.month], () => {
  loadMonthData()
})

// Force re-render when photo URL changes
watch(() => props.photoUrl, () => {
  // Photo URL changed, component will re-render automatically
})
</script>

<style scoped>
.calendar-puzzle-container {
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 8px;
}

.day-header {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  letter-spacing: 0.05em;
  padding: 8px 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  padding: 1px;
}

.calendar-cell {
  position: relative;
  aspect-ratio: 1;
  cursor: pointer;
  background: #ffffff;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.calendar-cell:first-child {
  border-top-left-radius: 15px;
}

.calendar-cell:nth-child(7) {
  border-top-right-radius: 15px;
}

.calendar-cell:nth-last-child(7) {
  border-bottom-left-radius: 15px;
}

.calendar-cell:last-child {
  border-bottom-right-radius: 15px;
}

.empty-cell {
  cursor: default;
  background: #fafafa;
}

.valid-cell:hover {
  transform: scale(0.98);
}

.date-number {
  position: absolute;
  top: 4px;
  left: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  z-index: 10;
}

.anniversary-name {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  color: #8b5cf6;
  text-align: center;
  padding: 4px;
  z-index: 10;
  pointer-events: none;
}

.puzzle-piece {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.puzzle-back {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
}

/* Heart music icon image - full size */
.heart-music-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-piece {
  width: 100%;
  height: 100%;
  transition: all 0.3s ease;
  position: relative;
}

.incomplete-overlay {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(135deg, 
      rgba(255, 255, 255, 0.65) 0%, 
      rgba(245, 245, 245, 0.75) 50%, 
      rgba(255, 255, 255, 0.65) 100%
    );
  backdrop-filter: blur(3px) saturate(0.8);
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.05);
}

.incomplete-overlay::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 15px,
      rgba(0, 0, 0, 0.02) 15px,
      rgba(0, 0, 0, 0.02) 30px
    );
}

.today {
  position: relative;
  overflow: visible;
}

.today::after {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: inherit;
  z-index: -1;
  opacity: 0.8;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .calendar-puzzle-container {
    padding: 20px;
    border-radius: 20px;
  }
  
  .date-number {
    font-size: 16px;
  }
  
  .day-header {
    font-size: 11px;
  }
}
</style>