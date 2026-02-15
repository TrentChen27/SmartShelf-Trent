<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <el-icon :size="48" color="#409eff"><Shop /></el-icon>
          <h1>SmartShelf</h1>
          <p>Create your account</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="rules"
          label-position="top"
          class="register-form"
        >
          <!-- Basic Info Section -->
          <div class="form-section">
            <h3 class="section-title">Basic Information</h3>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="Full Name" prop="name">
                  <el-input
                    v-model="registerForm.name"
                    placeholder="Enter your full name"
                    size="large"
                    :prefix-icon="User"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="24">
                <el-form-item label="Email" prop="email">
                  <el-input
                    v-model="registerForm.email"
                    type="email"
                    placeholder="Enter your email"
                    size="large"
                    :prefix-icon="Message"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Password" prop="passwd">
                  <el-input
                    v-model="registerForm.passwd"
                    type="password"
                    placeholder="Enter password"
                    size="large"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Confirm Password" prop="confirmPassword">
                  <el-input
                    v-model="registerForm.confirmPassword"
                    type="password"
                    placeholder="Confirm password"
                    size="large"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
              </el-col>

              <el-col :span="24">
                <el-form-item label="Customer Type" prop="kind">
                  <el-radio-group v-model="registerForm.kind" size="large">
                    <el-radio :label="0">Home Customer</el-radio>
                    <el-radio :label="1">Business Customer</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- Home Customer Fields -->
          <div v-if="registerForm.kind === 0" class="form-section">
            <h3 class="section-title">Personal Details</h3>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Gender" prop="gender">
                  <el-select v-model="registerForm.gender" placeholder="Select gender" size="large" style="width: 100%">
                    <el-option label="Male" value="male" />
                    <el-option label="Female" value="female" />
                    <el-option label="Non-binary" value="Non-binary" />
                    <el-option label="PreferNoToSay" value="PreferNoToSay" />
                  </el-select>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Age" prop="age">
                  <el-input
                    v-model.number="registerForm.age"
                    type="number"
                    placeholder="Enter age"
                    size="large"
                    min="18"
                    max="120"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Marital Status" prop="marriage_status">
                  <el-select v-model="registerForm.marriage_status" placeholder="Select status" size="large" style="width: 100%">
                    <el-option label="Single" :value="0" />
                    <el-option label="Married" :value="1" />
                    <el-option label="Divorced" :value="2" />
                    <el-option label="Widowed" :value="3" />
                  </el-select>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Annual Income ($)" prop="income">
                  <el-input
                    v-model.number="registerForm.income"
                    type="number"
                    placeholder="Enter annual income"
                    size="large"
                    min="0"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- Business Customer Fields -->
          <div v-if="registerForm.kind === 1" class="form-section">
            <h3 class="section-title">Business Details</h3>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="Company Name" prop="company_name">
                  <el-input
                    v-model="registerForm.company_name"
                    placeholder="Enter company name"
                    size="large"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Business Category" prop="category">
                  <el-input
                    v-model="registerForm.category"
                    placeholder="e.g., Retail, Restaurant"
                    size="large"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Gross Annual Income ($)" prop="gross_income">
                  <el-input
                    v-model.number="registerForm.gross_income"
                    type="number"
                    placeholder="Enter gross income"
                    size="large"
                    min="0"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleRegister"
              class="submit-btn"
            >
              Register
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          <span>Already have an account?</span>
          <router-link to="/login">Login here</router-link>
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Shop, User, Message, Lock, ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { register } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  name: '',
  email: '',
  passwd: '',
  confirmPassword: '',
  kind: 0,
  // Home customer fields
  gender: '',
  age: null,
  marriage_status: null,
  income: null,
  // Business customer fields
  company_name: '',
  category: '',
  gross_income: null
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.passwd) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const rules = {
  name: [
    { required: true, message: 'Please input your name', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please input email', trigger: 'blur' },
    { type: 'email', message: 'Please input valid email', trigger: 'blur' }
  ],
  passwd: [
    { required: true, message: 'Please input password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm password', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  kind: [
    { required: true, message: 'Please select customer type', trigger: 'change' }
  ]
}

async function handleRegister() {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // Trim whitespace from email and password
      const email = registerForm.email.trim()
      const passwd = registerForm.passwd.trim()

      // Prepare data based on customer type
      const data = {
        email: email,
        passwd: passwd,
        name: registerForm.name,
        kind: registerForm.kind
      }

      if (registerForm.kind === 0) {
        // Home customer
        data.gender = registerForm.gender
        data.age = registerForm.age
        data.marriage_status = registerForm.marriage_status
        data.income = registerForm.income
      } else {
        // Business customer
        data.company_name = registerForm.company_name
        data.category = registerForm.category
        data.gross_income = registerForm.gross_income
      }

      const response = await register(data)

      ElMessage.success('Registration successful! Please login.')
      router.push('/login')
    } catch (error) {
      console.error('Registration failed:', error)
      ElMessage.error('Registration failed. Please try again.')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.auth-container {
  width: 100%;
  max-width: 900px;
  padding: 1rem;
}

.auth-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.2rem;
  color: #409eff;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.register-form :deep(.el-input__inner[type="number"]::-webkit-inner-spin-button),
.register-form :deep(.el-input__inner[type="number"]::-webkit-outer-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}

.register-form :deep(.el-input__inner[type="number"]) {
  -moz-appearance: textfield;
  appearance: textfield;
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
</style>
