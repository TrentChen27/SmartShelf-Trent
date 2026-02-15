<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <el-icon :size="48" color="#409eff"><Shop /></el-icon>
          <h1>SmartShelf</h1>
          <p>Login to your account</p>
        </div>

        <div class="login-form">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            @submit.prevent="handleSubmit"
            @keyup.enter="handleSubmit"
          >
            <el-form-item label="Email" prop="email">
              <el-input
                v-model="form.email"
                type="email"
                placeholder="Enter your email"
                size="large"
                :prefix-icon="Message"
                :disabled="loading"
              />
            </el-form-item>

            <el-form-item label="Password" prop="passwd">
              <el-input
                v-model="form.passwd"
                type="password"
                placeholder="Enter your password"
                size="large"
                :prefix-icon="Lock"
                show-password
                :disabled="loading"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="submit-btn"
                native-type="submit"
              >
                Login
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="auth-footer">
          <span>Don't have an account?</span>
          <router-link to="/register">Register here</router-link>
        </div>

        <div class="back-home">
          <router-link to="/">
            <el-icon><ArrowLeft /></el-icon>
            Back to Home
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Shop, Message, Lock, ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { login } from '../api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  email: '',
  passwd: ''
})

const rules = {
  email: [
    { required: true, message: 'Please input email', trigger: 'blur' },
    { type: 'email', message: 'Please input valid email', trigger: 'blur' }
  ],
  passwd: [
    { required: true, message: 'Please input password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleSubmit = () => {
  if (!formRef.value) {
    return
  }

  formRef.value.validate(async (valid) => {
    if (!valid) {
      return false
    }

    loading.value = true

    try {
      // Trim whitespace from email and password
      const email = form.value.email.trim()
      const passwd = form.value.passwd.trim()

      const response = await login({
        email: email,
        passwd: passwd
      })

      if (!response || !response.token) {
        throw new Error('Invalid response from server')
      }

      // Save auth data
      authStore.setAuth(response.token, response.user, response.role)

      // Show success message
      ElMessage({
        type: 'success',
        message: 'Login successful!',
        duration: 2000
      })

      // Wait a bit then redirect
      setTimeout(() => {
        const redirectParam = route.query.redirect
        const redirectPath = typeof redirectParam === 'string' ? redirectParam : '/home'
        router.push(redirectPath)
      }, 500)

    } catch (err) {
      let errorMsg = 'Login failed'
      if (err.response?.data?.error) {
        errorMsg = err.response.data.error
      } else if (err.message) {
        errorMsg = err.message
      }

      ElMessage({
        type: 'error',
        message: errorMsg,
        duration: 3000,
        showClose: true
      })

      // Clear password on error
      form.value.passwd = ''

    } finally {
      loading.value = false
    }
  })
}

onMounted(() => {
  const authState =
    typeof authStore.isAuthenticated === 'object' && authStore.isAuthenticated !== null
      ? authStore.isAuthenticated.value
      : authStore.isAuthenticated
  if (authState) {
    const redirectParam = route.query.redirect
    const redirectPath = typeof redirectParam === 'string' ? redirectParam : '/home'
    router.replace(redirectPath)
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 1rem;
}

.auth-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  margin: 1rem 0 0.5rem;
  font-size: 2rem;
  color: #333;
}

.auth-header p {
  color: #666;
  margin: 0;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.auth-footer a {
  color: #409eff;
  text-decoration: none;
  margin-left: 0.5rem;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.back-home {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.back-home a {
  color: #666;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.back-home a:hover {
  color: #409eff;
}

/* Shake animation for login error */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.shake-error {
  animation: shake 0.5s;
}
</style>
