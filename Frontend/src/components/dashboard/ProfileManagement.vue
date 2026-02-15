<template>
  <div class="profile-management">
    <el-card v-loading="loading">
      <template #header>
        <div class="header-title">
          <h3>Personal Profile</h3>
          <el-tag v-if="userType" :type="userType === 'customer' ? 'success' : 'primary'">
            {{ userType === 'customer' ? 'Customer' : 'Employee' }}
          </el-tag>
        </div>
      </template>

      <!-- Customer Profile -->
      <template v-if="isCustomer">
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules"
          label-position="left"
          class="profile-form"
        >
          <el-row :gutter="40">
            <!-- Left Column -->
            <el-col :span="12">
              <h4 class="section-title">Account Information</h4>

              <el-form-item label="Name" label-width="140px">
                <el-input v-model="form.name" disabled />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Email support@smartshelf.com to change your name
                </div>
              </el-form-item>

              <el-form-item label="Email" prop="email" label-width="140px">
                <el-input v-model="form.email" />
              </el-form-item>

              <el-form-item label="Customer Type" label-width="140px" v-if="form.customer">
                <el-tag :type="form.customer?.kind === 0 ? 'success' : 'warning'" size="large">
                  {{ form.customer?.kind === 0 ? 'Home Customer' : 'Business Customer' }}
                </el-tag>
              </el-form-item>
            </el-col>

            <!-- Right Column -->
            <el-col :span="12">
              <!-- Home Customer Details -->
              <template v-if="form.customer?.kind === 0">
                <h4 class="section-title">Home Customer Details</h4>
                
                <el-form-item label="Gender" prop="gender" label-width="140px">
                  <el-select v-model="form.gender" placeholder="Select gender">
                    <el-option label="Male" value="Male" />
                    <el-option label="Female" value="Female" />
                    <el-option label="Non-binary" value="Non-binary" />
                    <el-option label="PreferNoToSay" value="PreferNoToSay" />
                  </el-select>
                </el-form-item>

                <el-form-item label="Age" prop="age" label-width="140px">
                  <el-input
                    v-model.number="form.age"
                    type="number"
                    :min="18"
                    :max="120"
                    placeholder="Enter your age"
                  />
                </el-form-item>

                <el-form-item label="Marital Status" prop="marriage_status" label-width="140px">
                  <el-select v-model="form.marriage_status" placeholder="Select status">
                    <el-option label="Single" :value="0" />
                    <el-option label="Married" :value="1" />
                    <el-option label="Divorced" :value="2" />
                    <el-option label="Widowed" :value="3" />
                  </el-select>
                </el-form-item>

                <el-form-item label="Annual Income" prop="income" label-width="140px">
                  <el-input-number 
                    v-model="form.income" 
                    :min="0" 
                    :step="1000"
                    :controls="false"
                    style="width: 100%"
                  >
                    <template #prefix>$</template>
                  </el-input-number>
                </el-form-item>
              </template>

              <!-- Business Customer Details -->
              <template v-else-if="form.customer?.kind === 1">
                <h4 class="section-title">Business Details</h4>
                
                <el-form-item label="Company Name" prop="company_name" label-width="140px">
                  <el-input v-model="form.company_name" placeholder="Company name" />
                </el-form-item>

                <el-form-item label="Business Category" prop="category" label-width="140px">
                  <el-input v-model="form.category" placeholder="e.g., Retail, Restaurant" />
                </el-form-item>

                <el-form-item label="Gross Income" prop="gross_income" label-width="140px">
                  <el-input-number 
                    v-model="form.gross_income" 
                    :min="0" 
                    :step="10000"
                    :controls="false"
                    style="width: 100%"
                  >
                    <template #prefix>$</template>
                  </el-input-number>
                </el-form-item>

              </template>
            </el-col>
          </el-row>

          <!-- Address Section -->
          <el-divider />
          <el-row :gutter="40">
            <el-col :span="24">
              <h4 class="section-title">Address Information</h4>
            </el-col>

            <el-col :span="12">
              <el-form-item label="Address Line 1" prop="address_1" label-width="140px">
                <el-input
                  v-model="form.address_1"
                  placeholder="Street address, P.O. box"
                />
              </el-form-item>

              <el-form-item label="Address Line 2" label-width="140px">
                <el-input
                  v-model="form.address_2"
                  placeholder="Apartment, suite, unit, building, floor, etc."
                />
              </el-form-item>

              <el-form-item label="City" prop="city" label-width="140px">
                <el-input
                  v-model="form.city"
                  placeholder="City"
                />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="State" prop="state" label-width="140px">
                <el-input
                  v-model="form.state"
                  placeholder="State"
                  maxlength="2"
                />
              </el-form-item>

              <el-form-item label="ZIP Code" prop="zipcode" label-width="140px">
                <el-input
                  v-model="form.zipcode"
                  placeholder="ZIP Code"
                  maxlength="10"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Assigned Salesperson Section -->
          <el-divider />
          <el-row>
            <el-col :span="24">
              <h4 class="section-title">Your Assigned Sales Representative</h4>

              <!-- Has assigned sales -->
              <template v-if="form.assigned_sales">
                <el-card class="sales-card" shadow="hover">
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="Sales Name" label-align="right">
                      <el-icon><User /></el-icon>
                      <strong>{{ form.assigned_sales.name }}</strong>
                    </el-descriptions-item>
                    <el-descriptions-item label="Sales Email" label-align="right">
                      <el-icon><Message /></el-icon>
                      <a :href="`mailto:${form.assigned_sales.email}`" class="contact-link">
                        {{ form.assigned_sales.email }}
                      </a>
                    </el-descriptions-item>
                    <el-descriptions-item label="Store Affiliation" label-align="right">
                      <el-icon><Shop /></el-icon>
                      <strong>{{ form.assigned_sales.store_name }}</strong>
                    </el-descriptions-item>
                  </el-descriptions>
                  <div class="sales-hint">
                    <el-icon><InfoFilled /></el-icon>
                    <div>
                      <div>Your sales representative can help you with orders, product recommendations, and account management.</div>
                      <div style="margin-top: 8px;">
                        To request a different sales representative, please email
                        <a href="mailto:sales@smartshelf.com" class="contact-link">sales@smartshelf.com</a>
                      </div>
                    </div>
                  </div>
                </el-card>
              </template>

              <!-- No assigned sales -->
              <template v-else>
                <el-alert
                  type="info"
                  :closable="false"
                  show-icon
                >
                  <template #title>No Sales Representative Assigned</template>
                  <div>
                    You don't have a dedicated sales representative yet. A sales representative will be automatically assigned to you when you place your first order.
                  </div>
                </el-alert>
              </template>
            </el-col>
          </el-row>

          <el-divider />

          <!-- Password Section -->
          <el-row :gutter="40">
            <el-col :span="24">
              <div class="password-section-header">
                <h4 class="section-title">Security & Password</h4>
                <el-button
                  :type="showPasswordChange ? 'default' : 'primary'"
                  size="small"
                  @click="togglePasswordChange"
                >
                  <el-icon><Edit /></el-icon>
                  {{ showPasswordChange ? 'Cancel Password Change' : 'Change Password' }}
                </el-button>
              </div>

              <el-alert
                type="warning"
                :closable="false"
                style="margin-bottom: 20px"
              >
                <template #title>
                  <strong>Authentication Required</strong>
                </template>
                To save any changes to your profile, you must enter your current password for verification.
              </el-alert>
            </el-col>

            <el-col :span="12">
              <el-form-item label="Current Password" prop="currentPassword" label-width="140px" required>
                <el-input
                  v-model="form.currentPassword"
                  type="password"
                  placeholder="Required to save changes"
                  show-password
                />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Enter your current password to verify your identity
                </div>
              </el-form-item>
            </el-col>

            <!-- Password Change Fields (Collapsible) -->
            <el-col :span="12" v-if="showPasswordChange">
              <el-form-item label="New Password" prop="passwd" label-width="140px">
                <el-input
                  v-model="form.passwd"
                  type="password"
                  placeholder="Enter new password"
                  show-password
                />
              </el-form-item>

              <el-form-item label="Confirm New Password" prop="confirmPassword" label-width="140px">
                <el-input
                  v-model="form.confirmPassword"
                  type="password"
                  placeholder="Re-enter new password"
                  show-password
                  :disabled="!form.passwd"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider />

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="saving" size="large">
              <el-icon><Check /></el-icon>
              Save Changes
            </el-button>
            <el-button @click="handleReset" size="large">
              <el-icon><Refresh /></el-icon>
              Reset
            </el-button>
          </el-form-item>
        </el-form>
      </template>

      <!-- Employee Profile -->
      <template v-else-if="isEmployee">
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules"
          label-position="left"
          class="profile-form"
        >
          <el-row :gutter="40">
            <!-- Left Column -->
            <el-col :span="12">
              <h4 class="section-title">Account Information</h4>

              <el-form-item label="Name" label-width="140px">
                <el-input v-model="form.name" disabled />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Contact HR to change your name
                </div>
              </el-form-item>

              <el-form-item label="Email" prop="email" label-width="140px">
                <el-input v-model="form.email" disabled />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Contact IT to change your email
                </div>
              </el-form-item>
            </el-col>

            <!-- Right Column -->
            <el-col :span="12">
              <h4 class="section-title">Employee Information</h4>

              <el-form-item label="Employee ID" label-width="140px">
                <el-input :value="String(form.employee?.id)" disabled />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Contact HR to modify employee details
                </div>
              </el-form-item>

              <el-form-item label="Job Title" label-width="140px">
                <el-input :value="form.employee?.job_title || ''" disabled />
              </el-form-item>

              <el-form-item label="Salary" label-width="140px">
                <el-input :value="formatCurrency(form.employee?.salary)" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Store and Management Info (for Salesperson, Store Manager, or Regional Manager) -->
          <template v-if="form.salesperson || form.store_info || form.region_info">
            <el-divider />
            <el-row>
              <el-col :span="24">
                <h4 class="section-title">{{ form.region_info ? 'Regional Management Information' : 'Store & Management Information' }}</h4>

                <el-card class="sales-card" shadow="hover">
                  <el-descriptions :column="1" border>
                    <!-- Store Information -->
                    <el-descriptions-item label="Store Assignment" label-align="right" v-if="form.store_info">
                      <el-icon><Shop /></el-icon>
                      <strong>{{ form.store_info?.name || 'Unknown Store' }}</strong>
                    </el-descriptions-item>

                    <!-- Store Manager (only show if user is NOT the store manager) -->
                    <el-descriptions-item label="Store Manager" label-align="right" v-if="form.store_manager && !isStoreManager">
                      <el-icon><User /></el-icon>
                      <strong>{{ form.store_manager.name }}</strong>
                    </el-descriptions-item>
                    <el-descriptions-item label="Store Manager Email" label-align="right" v-if="form.store_manager && !isStoreManager">
                      <el-icon><Message /></el-icon>
                      <a :href="`mailto:${form.store_manager.email}`" class="contact-link">
                        {{ form.store_manager.email }}
                      </a>
                    </el-descriptions-item>

                    <!-- Region (for both store managers and regional managers) -->
                    <el-descriptions-item label="Region" label-align="right" v-if="form.region_manager || form.region_info">
                      <el-icon><Location /></el-icon>
                      <strong>{{ form.region_manager?.region_name || form.region_info?.region_name || 'Unknown Region' }}</strong>
                    </el-descriptions-item>

                    <!-- Region Manager (only show if user is NOT the region manager) -->
                    <el-descriptions-item label="Region Manager" label-align="right" v-if="form.region_manager && !isRegionManager">
                      <el-icon><User /></el-icon>
                      <strong>{{ form.region_manager.name }}</strong>
                    </el-descriptions-item>
                    <el-descriptions-item label="Region Manager Email" label-align="right" v-if="form.region_manager && !isRegionManager">
                      <el-icon><Message /></el-icon>
                      <a :href="`mailto:${form.region_manager.email}`" class="contact-link">
                        {{ form.region_manager.email }}
                      </a>
                    </el-descriptions-item>
                  </el-descriptions>

                  <div class="sales-hint">
                    <el-icon><InfoFilled /></el-icon>
                    <div>
                      <div v-if="isRegionManager">
                        As a regional manager, you oversee all stores in your region. You can manage store operations, employee assignments, and inventory across your region.
                      </div>
                      <div v-else-if="isStoreManager">
                        As a store manager, your region manager can assist you with operational questions and strategic guidance.
                      </div>
                      <div v-else>
                        Your store manager and region manager can assist you with operational questions and performance reviews.
                      </div>
                      <div style="margin-top: 8px;">
                        For organizational changes or reassignment requests, please contact
                        <a href="mailto:hr@smartshelf.com" class="contact-link">hr@smartshelf.com</a>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </template>

          <el-divider />

          <!-- Password Section -->
          <el-row :gutter="40">
            <el-col :span="24">
              <div class="password-section-header">
                <h4 class="section-title">Security & Password</h4>
                <el-button
                  :type="showPasswordChange ? 'default' : 'primary'"
                  size="small"
                  @click="togglePasswordChange"
                >
                  <el-icon><Edit /></el-icon>
                  {{ showPasswordChange ? 'Cancel Password Change' : 'Change Password' }}
                </el-button>
              </div>

              <el-alert
                type="warning"
                :closable="false"
                style="margin-bottom: 20px"
              >
                <template #title>
                  <strong>Authentication Required</strong>
                </template>
                To save any changes to your profile, you must enter your current password for verification.
              </el-alert>
            </el-col>

            <el-col :span="12">
              <el-form-item label="Current Password" prop="currentPassword" label-width="140px" required>
                <el-input
                  v-model="form.currentPassword"
                  type="password"
                  placeholder="Required to save changes"
                  show-password
                />
                <div class="field-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Enter your current password to verify your identity
                </div>
              </el-form-item>
            </el-col>

            <!-- Password Change Fields (Collapsible) -->
            <el-col :span="12" v-if="showPasswordChange">
              <el-form-item label="New Password" prop="passwd" label-width="140px">
                <el-input
                  v-model="form.passwd"
                  type="password"
                  placeholder="Enter new password"
                  show-password
                />
              </el-form-item>

              <el-form-item label="Confirm New Password" prop="confirmPassword" label-width="140px">
                <el-input
                  v-model="form.confirmPassword"
                  type="password"
                  placeholder="Re-enter new password"
                  show-password
                  :disabled="!form.passwd"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider />

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="saving" size="large">
              <el-icon><Check /></el-icon>
              Save Changes
            </el-button>
            <el-button @click="handleReset" size="large">
              <el-icon><Refresh /></el-icon>
              Reset
            </el-button>
          </el-form-item>
        </el-form>
      </template>

      <!-- No Profile Data -->
      <template v-else>
        <el-empty description="No profile data available" />
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Check, Refresh, User, Message, Shop, Edit, Location } from '@element-plus/icons-vue'
import { getProfile, updateProfile } from '../../api/auth'

// Refs
const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)
const originalData = ref(null)
const showPasswordChange = ref(false)

// Form data
const form = ref({
  name: '',
  email: '',
  currentPassword: '',
  passwd: '',
  confirmPassword: '',
  customer: null,
  customer_details: null,
  employee: null,
  salesperson: null,
  store_info: null,
  store_manager: null,
  region_manager: null,
  region_info: null,
  // Customer fields
  gender: '',
  age: null,
  marriage_status: null,
  income: null,
  company_name: '',
  category: '',
  gross_income: null,
  // Address fields
  address_1: '',
  address_2: '',
  city: '',
  state: '',
  zipcode: ''
})

// Custom validator for password confirmation
const validateConfirmPassword = (rule, value, callback) => {
  if (form.value.passwd && value !== form.value.passwd) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

// Validation rules
const rules = {
  email: [
    { required: true, message: 'Please input email', trigger: 'blur' },
    { type: 'email', message: 'Please input valid email', trigger: 'blur' }
  ],
  currentPassword: [
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  passwd: [
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// Computed
const userType = computed(() => {
  if (form.value.customer) return 'customer'
  if (form.value.employee) return 'employee'
  return null
})

const isCustomer = computed(() => userType.value === 'customer')
const isEmployee = computed(() => userType.value === 'employee')

// Check if the current user is a store manager
const isStoreManager = computed(() => {
  if (!form.value.employee || !form.value.store_info) return false
  // If employee has store_info and store_manager with same email, they are the manager
  return form.value.store_manager?.email === form.value.email
})

// Check if the current user is a region manager
const isRegionManager = computed(() => {
  if (!form.value.employee) return false
  // Check if user has region_info or if region_manager email matches their own
  return form.value.region_info != null || form.value.region_manager?.email === form.value.email
})

// Methods
function togglePasswordChange() {
  showPasswordChange.value = !showPasswordChange.value
  // Clear password fields when hiding
  if (!showPasswordChange.value) {
    form.value.passwd = ''
    form.value.confirmPassword = ''
  }
}

function formatCurrency(amount) {
  if (amount == null) return 'N/A'
  return `$${Number(amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

async function loadProfile() {
  loading.value = true
  try {
    const response = await getProfile()
    const data = response.data || response

    // Store original data for reset
    originalData.value = JSON.parse(JSON.stringify(data))

    // Populate form
    form.value = {
      name: data.name || '',
      email: data.email || '',
      currentPassword: '',
      passwd: '',
      confirmPassword: '',
      customer: data.customer || null,
      customer_details: data.customer_details || null,
      employee: data.employee || null,
      salesperson: data.salesperson || null,
      assigned_sales: data.assigned_sales || null,
      // Employee/Salesperson fields
      store_info: data.store_info || null,
      store_manager: data.store_manager || null,
      region_manager: data.region_manager || null,
      region_info: data.region_info || null,
      // Customer fields
      gender: data.customer_details?.gender || '',
      age: data.customer_details?.age || null,
      marriage_status: data.customer_details?.marriage_status ?? null,
      income: data.customer_details?.income || null,
      company_name: data.customer_details?.company_name || '',
      category: data.customer_details?.category || '',
      gross_income: data.customer_details?.gross_income || null,
      // Address fields
      address_1: data.customer?.address?.address_1 || '',
      address_2: data.customer?.address?.address_2 || '',
      city: data.customer?.address?.city || '',
      state: data.customer?.address?.state || '',
      zipcode: data.customer?.address?.zipcode || ''
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to load profile')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // IMPORTANT: Current password is REQUIRED for ALL changes
    if (!form.value.currentPassword) {
      ElMessage.error('Please enter your current password to verify your identity')
      return
    }

    // Validate password change if user wants to change password
    if (form.value.passwd || form.value.confirmPassword) {
      if (!form.value.passwd) {
        ElMessage.error('Please enter a new password')
        return
      }
      if (form.value.passwd !== form.value.confirmPassword) {
        ElMessage.error('New passwords do not match')
        return
      }
      if (form.value.passwd.length < 6) {
        ElMessage.error('New password must be at least 6 characters')
        return
      }
    }
    
    saving.value = true
    try {
      const updateData = {
        email: form.value.email
      }
      
      // Only include password if changed
      if (form.value.currentPassword && form.value.passwd) {
        updateData.current_password = form.value.currentPassword
        updateData.passwd = form.value.passwd
      }

      // Add customer-specific fields
      if (isCustomer.value) {
        if (form.value.customer?.kind === 0) {
          // Home customer
          updateData.gender = form.value.gender
          updateData.age = form.value.age
          updateData.marriage_status = form.value.marriage_status
          updateData.income = form.value.income
        } else if (form.value.customer?.kind === 1) {
          // Business customer
          updateData.company_name = form.value.company_name
          updateData.category = form.value.category
          updateData.gross_income = form.value.gross_income
        }

        // Add address fields for all customers
        updateData.address_1 = form.value.address_1
        updateData.address_2 = form.value.address_2
        updateData.city = form.value.city
        updateData.state = form.value.state
        updateData.zipcode = form.value.zipcode
      }

      await updateProfile(updateData)
      ElMessage.success('Profile updated successfully')
      
      // Reload profile
      await loadProfile()
      
      // Clear password fields
      form.value.currentPassword = ''
      form.value.passwd = ''
      form.value.confirmPassword = ''
    } catch (error) {
      console.error('Failed to update profile:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to update profile')
    } finally {
      saving.value = false
    }
  })
}

function handleReset() {
  if (originalData.value) {
    form.value = {
      name: originalData.value.name || '',
      email: originalData.value.email || '',
      currentPassword: '',
      passwd: '',
      confirmPassword: '',
      customer: originalData.value.customer || null,
      customer_details: originalData.value.customer_details || null,
      employee: originalData.value.employee || null,
      salesperson: originalData.value.salesperson || null,
      assigned_sales: originalData.value.assigned_sales || null,
      // Employee/Salesperson fields
      store_info: originalData.value.store_info || null,
      store_manager: originalData.value.store_manager || null,
      region_manager: originalData.value.region_manager || null,
      // Customer fields
      gender: originalData.value.customer_details?.gender || '',
      age: originalData.value.customer_details?.age || null,
      marriage_status: originalData.value.customer_details?.marriage_status ?? null,
      income: originalData.value.customer_details?.income || null,
      company_name: originalData.value.customer_details?.company_name || '',
      category: originalData.value.customer_details?.category || '',
      gross_income: originalData.value.customer_details?.gross_income || null,
      // Address fields
      address_1: originalData.value.customer?.address?.address_1 || '',
      address_2: originalData.value.customer?.address?.address_2 || '',
      city: originalData.value.customer?.address?.city || '',
      state: originalData.value.customer?.address?.state || '',
      zipcode: originalData.value.customer?.address?.zipcode || ''
    }
    ElMessage.info('Form reset to original values')
  }
}

// Lifecycle
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}

.header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.profile-form {
  padding: 20px 0;
}

.section-title {
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.field-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
  line-height: 1.4;
}

.field-hint .el-icon {
  font-size: 14px;
  flex-shrink: 0;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-divider) {
  margin: 30px 0;
}

:deep(.el-button) {
  min-width: 120px;
}

/* Income input-number text alignment */
:deep(.el-input-number .el-input__inner) {
  text-align: left !important;
}

/* Sales Card Styles */
.sales-card {
  margin-top: 12px;
  border: 1px solid #e4e7ed;
}

.sales-card :deep(.el-descriptions__label) {
  font-weight: 600;
  width: 180px;
  vertical-align: middle;
}

.sales-card :deep(.el-descriptions__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sales-card :deep(.el-descriptions__cell) {
  padding: 12px 16px;
}

.sales-card :deep(.el-descriptions-item__container) {
  align-items: center;
}

.sales-card .el-icon {
  color: #409eff;
  font-size: 16px;
}

.contact-link {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.contact-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.sales-hint {
  margin-top: 16px;
  padding: 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.sales-hint .el-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

/* Address Card Styles */
.address-card {
  margin-top: 12px;
  border: 1px solid #e4e7ed;
}

.address-card :deep(.el-descriptions__label) {
  font-weight: 600;
  width: 180px;
  vertical-align: middle;
}

.address-card :deep(.el-descriptions__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.address-card :deep(.el-descriptions__cell) {
  padding: 12px 16px;
}

.address-card :deep(.el-descriptions-item__container) {
  align-items: center;
}

.address-card .el-icon {
  color: #67c23a;
  font-size: 16px;
}

.address-hint {
  margin-top: 16px;
  padding: 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #67c23a;
  border-radius: 4px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.address-hint .el-icon {
  color: #67c23a;
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

/* Password Section Header */
.password-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.password-section-header .section-title {
  margin: 0;
  padding: 0;
  border: none;
}

.password-section-header .el-button {
  min-width: auto;
  padding: 8px 16px;
}
</style>
