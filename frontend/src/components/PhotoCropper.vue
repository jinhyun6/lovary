<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="cancel"></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col shadow-2xl">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">Adjust Photo</h2>
        <p class="text-sm text-gray-500 mt-1">Drag to move, use buttons to zoom</p>
      </div>
      
      <!-- Cropper -->
      <div class="flex-1 p-6 bg-gray-50 overflow-hidden">
        <div class="relative h-[500px] max-h-[60vh] flex items-center justify-center">
          <div 
            ref="cropperContainer"
            class="relative overflow-hidden rounded-lg shadow-lg bg-black"
            :style="{ width: '420px', height: '360px' }"
            @mousedown="startDrag"
            @touchstart="startDrag"
          >
            <img 
              ref="imageEl"
              :src="imageSrc"
              class="absolute cursor-move"
              :style="imageStyle"
              @load="onImageLoad"
              draggable="false"
            />
            <div class="absolute inset-0 border-2 border-white/50 pointer-events-none"></div>
          </div>
        </div>
        
        <!-- Zoom Controls -->
        <div class="flex justify-center gap-4 mt-4">
          <button
            @click="zoom(-0.1)"
            class="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </button>
          <span class="px-4 py-2 bg-white rounded-lg shadow">{{ Math.round(scale * 100) }}%</span>
          <button
            @click="zoom(0.1)"
            class="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
        <button
          @click="cancel"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="apply"
          class="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all transform hover:-translate-y-0.5"
        >
          Apply
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isOpen: boolean
  imageSrc: string
}>()

const emit = defineEmits<{
  close: []
  crop: [blob: Blob]
}>()

// Crop area dimensions (7:6 ratio for calendar)
// Make the output larger for better quality
const CROP_WIDTH = 700
const CROP_HEIGHT = 600

// Refs
const cropperContainer = ref<HTMLElement>()
const imageEl = ref<HTMLImageElement>()

// Image state
const imageWidth = ref(0)
const imageHeight = ref(0)
const scale = ref(1)
const posX = ref(0)
const posY = ref(0)

// Drag state
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartPosX = ref(0)
const dragStartPosY = ref(0)

const imageStyle = computed(() => ({
  width: `${imageWidth.value * scale.value}px`,
  height: `${imageHeight.value * scale.value}px`,
  left: `${posX.value}px`,
  top: `${posY.value}px`
}))

const onImageLoad = (event: Event) => {
  const img = event.target as HTMLImageElement
  imageWidth.value = img.naturalWidth
  imageHeight.value = img.naturalHeight
  
  // Calculate minimum scale to cover the entire crop area
  const displayWidth = 420
  const displayHeight = 360
  const scaleX = displayWidth / img.naturalWidth
  const scaleY = displayHeight / img.naturalHeight
  
  // Use the larger scale to ensure image covers entire area
  scale.value = Math.max(scaleX, scaleY)
  
  // Center the image
  centerImage()
  constrainPosition()
}

const centerImage = () => {
  posX.value = (420 - imageWidth.value * scale.value) / 2
  posY.value = (360 - imageHeight.value * scale.value) / 2
}

const zoom = (delta: number) => {
  // Calculate minimum scale to ensure image always covers crop area
  const minScaleX = 420 / imageWidth.value
  const minScaleY = 360 / imageHeight.value
  const minScale = Math.max(minScaleX, minScaleY)
  
  const newScale = Math.max(minScale, Math.min(3, scale.value + delta))
  const scaleRatio = newScale / scale.value
  
  // Zoom towards center
  const centerX = 420 / 2
  const centerY = 360 / 2
  
  posX.value = centerX - (centerX - posX.value) * scaleRatio
  posY.value = centerY - (centerY - posY.value) * scaleRatio
  
  scale.value = newScale
  constrainPosition()
}

const startDrag = (event: MouseEvent | TouchEvent) => {
  isDragging.value = true
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  dragStartX.value = clientX
  dragStartY.value = clientY
  dragStartPosX.value = posX.value
  dragStartPosY.value = posY.value
  
  event.preventDefault()
}

const onDrag = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  posX.value = dragStartPosX.value + (clientX - dragStartX.value)
  posY.value = dragStartPosY.value + (clientY - dragStartY.value)
  
  constrainPosition()
}

const endDrag = () => {
  isDragging.value = false
}

const constrainPosition = () => {
  const imgWidth = imageWidth.value * scale.value
  const imgHeight = imageHeight.value * scale.value
  
  // Ensure image covers the entire crop area
  const maxX = 0
  const minX = 420 - imgWidth
  const maxY = 0
  const minY = 360 - imgHeight
  
  posX.value = Math.min(maxX, Math.max(minX, posX.value))
  posY.value = Math.min(maxY, Math.max(minY, posY.value))
}

const cancel = () => {
  emit('close')
}

const apply = () => {
  // Get the cropper container DOM element
  if (!cropperContainer.value) return
  
  // Use html2canvas or similar approach - but simpler
  // Create canvas matching the visible area
  const canvas = document.createElement('canvas')
  canvas.width = CROP_WIDTH
  canvas.height = CROP_HEIGHT
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // Fill with black background (same as preview)
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, CROP_WIDTH, CROP_HEIGHT)
  
  // Calculate scale factor for output
  const scaleFactor = CROP_WIDTH / 420
  
  // Draw the image EXACTLY as shown in preview, just scaled up
  ctx.save()
  ctx.scale(scaleFactor, scaleFactor)
  
  // Draw image with same position and scale as preview
  ctx.drawImage(
    imageEl.value!,
    posX.value,
    posY.value, 
    imageWidth.value * scale.value,
    imageHeight.value * scale.value
  )
  
  ctx.restore()
  
  // Convert to blob
  canvas.toBlob((blob) => {
    if (blob) {
      emit('crop', blob)
    }
  }, 'image/jpeg', 0.95)
}

// Event listeners
onMounted(() => {
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', endDrag)
  document.addEventListener('touchmove', onDrag)
  document.addEventListener('touchend', endDrag)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', endDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', endDrag)
})
</script>

<style scoped>
/* Prevent text selection during drag */
.cursor-move {
  user-select: none;
  -webkit-user-drag: none;
}
</style>