<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <nav class="bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div class="max-w-4xl mx-auto px-6 py-5 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800">Profile</h1>
        <router-link to="/diary" class="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors">
          ← Back
        </router-link>
      </div>
    </nav>

    <div class="max-w-2xl mx-auto px-6 py-12 space-y-8">
      <!-- User Info -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-800 mb-6">My Information</h2>
        <form @submit.prevent="updateProfile" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">
              Name
            </label>
            <input
              v-model="name"
              type="text"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
              placeholder="Enter your name"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">
              Daily Reminder
            </label>
            <input
              v-model="reminderTime"
              type="time"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
            />
          </div>
          <button
            type="submit"
            :disabled="isUpdating"
            class="px-6 py-2.5 bg-gray-800 text-white text-sm font-medium rounded-xl hover:bg-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isUpdating ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- Notifications -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-800 mb-6">Notifications</h2>
        <button
          @click="enableNotifications"
          :disabled="notificationsEnabled"
          class="px-6 py-2.5 text-sm font-medium rounded-xl transition-colors"
          :class="notificationsEnabled 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'"
        >
          {{ notificationsEnabled ? 'Notifications Enabled' : 'Enable Push Notifications' }}
        </button>
      </div>

      <!-- Partner Connection -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-800 mb-6">Partner Connection</h2>
        
        <div v-if="!user?.partner_id">
          <!-- Partner Search -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-600 mb-2">
              Find Partner by Email
            </label>
            <div class="flex gap-3">
              <input
                v-model="searchEmail"
                type="email"
                class="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent transition-all"
                placeholder="partner@email.com"
              />
              <button
                @click="searchPartner"
                :disabled="isSearching"
                class="px-6 py-3 bg-gray-800 text-white text-sm font-medium rounded-xl hover:bg-gray-900 transition-colors disabled:opacity-50"
              >
                Search
              </button>
            </div>
          </div>

          <!-- Search Results -->
          <div v-if="searchResults.length > 0" class="mb-6">
            <h3 class="text-sm font-medium text-gray-600 mb-3">Search Results</h3>
            <div class="space-y-2">
              <div
                v-for="result in searchResults"
                :key="result.id"
                class="flex justify-between items-center p-4 border border-gray-200 rounded-xl"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ result.name || 'No name' }}</p>
                  <p class="text-sm text-gray-500">{{ result.email }}</p>
                </div>
                <button
                  @click="sendRequest(result.email)"
                  class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Connect
                </button>
              </div>
            </div>
          </div>

          <!-- Received Requests -->
          <div v-if="receivedRequests.length > 0">
            <h3 class="text-sm font-medium text-gray-600 mb-3">Connection Requests</h3>
            <div class="space-y-2">
              <div
                v-for="request in receivedRequests"
                :key="request.id"
                class="flex justify-between items-center p-4 border border-gray-200 rounded-xl"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ request.requester.name || 'No name' }}</p>
                  <p class="text-sm text-gray-500">{{ request.requester.email }}</p>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="acceptRequest(request.id)"
                    class="px-4 py-2 text-sm font-medium text-green-700 border border-green-300 rounded-lg hover:bg-green-50 transition-colors"
                  >
                    Accept
                  </button>
                  <button
                    @click="rejectRequest(request.id)"
                    class="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    Decline
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Sent Requests -->
          <div v-if="sentRequests.length > 0" class="mt-4">
            <h3 class="text-sm font-medium text-gray-600 mb-3">Pending Requests</h3>
            <div class="space-y-2">
              <div
                v-for="request in sentRequests"
                :key="request.id"
                class="flex justify-between items-center p-4 border border-gray-200 rounded-xl"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ request.recipient.name || 'No name' }}</p>
                  <p class="text-sm text-gray-500">{{ request.recipient.email }}</p>
                </div>
                <span class="text-sm text-gray-400">Pending</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else>
          <div class="p-4 bg-gray-50 rounded-xl mb-4">
            <p class="text-sm font-medium text-gray-600 mb-2">Connected with</p>
            <div v-if="user?.partner" class="space-y-1">
              <p class="font-medium text-gray-800">{{ user.partner.name || 'No name' }}</p>
              <p class="text-sm text-gray-500">{{ user.partner.email }}</p>
            </div>
          </div>
          <button
            @click="disconnectPartner"
            class="w-full px-4 py-2 text-sm font-medium text-red-600 border border-red-300 rounded-xl hover:bg-red-50 transition-colors"
          >
            Disconnect Partner
          </button>
        </div>
      </div>

      <!-- Account Management -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-800 mb-6">Account Management</h2>
        <p class="text-sm text-gray-600 mb-4">
          Delete your account and all associated data. This action cannot be undone.
        </p>
        <button
          @click="deleteAccount"
          class="px-6 py-2.5 bg-red-600 text-white text-sm font-medium rounded-xl hover:bg-red-700 transition-colors"
        >
          Delete Account
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usersApi, type User, type PartnerRequest } from '@/api/users'

const router = useRouter()
const user = ref<User | null>(null)
const name = ref('')
const reminderTime = ref('')
const isUpdating = ref(false)
const notificationsEnabled = ref(false)

const searchEmail = ref('')
const isSearching = ref(false)
const searchResults = ref<Array<{id: number, email: string, name?: string}>>([])
const partnerRequests = ref<PartnerRequest[]>([])

const receivedRequests = computed(() => 
  partnerRequests.value.filter(req => req.recipient_id === user.value?.id)
)

const sentRequests = computed(() => 
  partnerRequests.value.filter(req => req.requester_id === user.value?.id)
)

const loadUserData = async () => {
  try {
    user.value = await usersApi.getMe()
    name.value = user.value.name || ''
    reminderTime.value = user.value.reminder_time || ''
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

const loadPartnerRequests = async () => {
  try {
    partnerRequests.value = await usersApi.getPartnerRequests()
  } catch (error) {
    console.error('Failed to load partner requests:', error)
  }
}

const updateProfile = async () => {
  isUpdating.value = true
  try {
    await usersApi.updateMe({
      name: name.value || undefined,
      reminder_time: reminderTime.value || undefined
    })
    alert('Profile updated successfully!')
  } catch (error) {
    alert('Failed to update profile.')
  } finally {
    isUpdating.value = false
  }
}

const enableNotifications = async () => {
  try {
    const permission = await Notification.requestPermission()
    if (permission === 'granted') {
      // Register service worker if not already registered
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register('/sw.js')
        
        // Get push subscription
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: import.meta.env.VITE_VAPID_PUBLIC_KEY
        })
        
        // Save subscription to backend
        await usersApi.savePushSubscription(subscription.toJSON())
        notificationsEnabled.value = true
        alert('Push notifications enabled!')
      }
    }
  } catch (error) {
    console.error('Failed to enable notifications:', error)
    alert('Failed to enable push notifications.')
  }
}

const searchPartner = async () => {
  if (!searchEmail.value) return
  
  isSearching.value = true
  try {
    searchResults.value = await usersApi.searchUsers(searchEmail.value)
  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    isSearching.value = false
  }
}

const sendRequest = async (email: string) => {
  try {
    await usersApi.sendPartnerRequest(email)
    alert('Connection request sent!')
    searchResults.value = []
    searchEmail.value = ''
    await loadPartnerRequests()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Failed to send request.')
  }
}

const acceptRequest = async (requestId: number) => {
  try {
    await usersApi.acceptPartnerRequest(requestId)
    alert('Partner connected successfully!')
    await loadUserData()
    await loadPartnerRequests()
  } catch (error) {
    alert('Failed to accept request.')
  }
}

const rejectRequest = async (requestId: number) => {
  try {
    await usersApi.rejectPartnerRequest(requestId)
    await loadPartnerRequests()
  } catch (error) {
    alert('Failed to reject request.')
  }
}

const disconnectPartner = async () => {
  if (!confirm('Are you sure you want to disconnect from your partner?')) return
  
  try {
    await usersApi.disconnectPartner()
    alert('Partner disconnected successfully.')
    await loadUserData()
  } catch (error) {
    alert('Failed to disconnect partner.')
  }
}

const deleteAccount = async () => {
  if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) return
  if (!confirm('This will permanently delete all your diaries, photos, and data. Are you absolutely sure?')) return
  
  try {
    await usersApi.deleteAccount()
    localStorage.removeItem('token')
    router.push('/')
  } catch (error) {
    alert('Failed to delete account.')
  }
}

onMounted(() => {
  loadUserData()
  loadPartnerRequests()
  
  // Check if notifications are already enabled
  if ('Notification' in window && Notification.permission === 'granted') {
    notificationsEnabled.value = true
  }
})
</script>