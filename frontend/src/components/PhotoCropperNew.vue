<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="cancel"></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col shadow-2xl">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">Adjust Photo</h2>
        <p class="text-sm text-gray-500 mt-1">Drag to move, scroll to zoom</p>
      </div>
      
      <!-- Cropper -->
      <div class="flex-1 p-6 bg-gray-50 overflow-hidden">
        <div class="flex items-center justify-center" style="height: 500px;">
          <img 
            ref="imageElement"
            :src="imageSrc"
            class="max-w-full max-h-full block"
            style="visibility: hidden;"
          />
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
          class="px-6 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors"
        >
          Apply
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

const props = defineProps<{
  isOpen: boolean
  imageSrc: string
}>()

const emit = defineEmits<{
  close: []
  crop: [blob: Blob]
}>()

const imageElement = ref<HTMLImageElement>()
let cropper: Cropper | null = null

// Initialize cropper when modal opens
watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.imageSrc) {
    await nextTick()
    
    if (imageElement.value && !cropper) {
      cropper = new Cropper(imageElement.value, {
        aspectRatio: 7 / 6, // Calendar ratio
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 1,
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: false,
        cropBoxResizable: false,
        toggleDragModeOnDblclick: false,
        minCropBoxWidth: 420,
        minCropBoxHeight: 360,
        ready() {
          // Make image visible after cropper is ready
          if (imageElement.value) {
            imageElement.value.style.visibility = 'visible'
          }
        }
      })
    }
  } else if (!newVal && cropper) {
    // Destroy cropper when modal closes
    cropper.destroy()
    cropper = null
  }
})

const cancel = () => {
  emit('close')
}

const apply = () => {
  if (!cropper) return
  
  // Get cropped canvas with exact size we want
  const canvas = cropper.getCroppedCanvas({
    width: 700,
    height: 600,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high'
  })
  
  // Convert to blob
  canvas.toBlob((blob) => {
    if (blob) {
      emit('crop', blob)
    }
  }, 'image/jpeg', 0.95)
}

// Cleanup on unmount
onBeforeUnmount(() => {
  if (cropper) {
    cropper.destroy()
    cropper = null
  }
})
</script>

<style scoped>
/* Override some Cropper.js styles for better appearance */
:deep(.cropper-container) {
  max-height: 500px;
}

:deep(.cropper-view-box) {
  outline: 2px solid rgba(59, 130, 246, 0.5);
  outline-offset: -2px;
}

:deep(.cropper-face) {
  background-color: transparent;
}
</style>