import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(loadUserFromStorage())
  const userRole = ref(localStorage.getItem('userRole') || null)
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  function loadUserFromStorage() {
    const stored = localStorage.getItem('user')
    if (!stored) return null
    try {
      return JSON.parse(stored)
    } catch (error) {
      console.warn('Failed to parse stored user data:', error)
      localStorage.removeItem('user')
      return null
    }
  }

  function setAuth(authToken, userData, role) {
    token.value = authToken
    user.value = userData
    userRole.value = role
    isInitialized.value = true

    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('userRole', role)
  }

  function clearAuth() {
    token.value = null
    user.value = null
    userRole.value = null
    isInitialized.value = true

    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('userRole')
  }

  function initializeAuth() {
    if (isInitialized.value) {
      return
    }

    token.value = localStorage.getItem('token') || null
    user.value = loadUserFromStorage()
    userRole.value = localStorage.getItem('userRole') || null
    isInitialized.value = true
  }

  return {
    token,
    user,
    userRole,
    isAuthenticated,
    isInitialized,
    setAuth,
    clearAuth,
    initializeAuth
  }
})
