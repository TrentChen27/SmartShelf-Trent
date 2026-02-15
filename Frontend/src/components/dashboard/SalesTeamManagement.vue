<template>
  <div class="sales-team-management">
    <el-card>
      <!-- Header with Add Button -->
      <template #header>
        <div class="header-actions">
          <h3>Employee Management</h3>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            Add Employee
          </el-button>
        </div>
      </template>

      <!-- Filters -->
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="Search by name or email..."
          clearable
          style="width: 220px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="roleFilter"
          placeholder="All Roles"
          clearable
          style="width: 160px"
          @change="handleFilterChange"
        >
          <el-option label="All Roles" :value="null" />
          <el-option label="Regional Manager" value="region_manager" />
          <el-option label="Store Manager" value="store_manager" />
          <el-option label="Sales" value="sales" />
          <el-option label="Employee" value="employee" />
        </el-select>

        <el-select
          v-model="storeFilter"
          placeholder="All Stores"
          clearable
          style="width: 160px"
          @change="handleFilterChange"
        >
          <el-option label="All Stores" :value="null" />
          <el-option
            v-for="store in stores"
            :key="store.id"
            :label="store.name"
            :value="store.id"
          />
        </el-select>
      </div>

      <!-- Employees Table -->
      <el-table
        :data="displayedEmployees"
        v-loading="loading"
        stripe
        size="small"
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="50" />
        <el-table-column prop="name" label="Name" min-width="120" show-overflow-tooltip />
        <el-table-column prop="email" label="Email" min-width="180" show-overflow-tooltip />
        <el-table-column label="Salary" width="110" align="right" sortable :sort-method="sortBySalary">
          <template #default="{ row }">
            ${{ formatNumber(row.salary / 100) }}
          </template>
        </el-table-column>
        <el-table-column label="Role" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.is_region_manager" type="warning" size="small">Regional</el-tag>
            <el-tag v-else-if="row.is_manager" type="danger" size="small">Manager</el-tag>
            <el-tag v-else-if="row.is_salesperson" type="success" size="small">Sales</el-tag>
            <el-tag v-else type="info" size="small">Employee</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Store" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.is_region_manager">Regional</span>
            <span v-else>{{ row.store_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-tooltip
              v-if="isCurrentUser(row)"
              content="Cannot edit your own information"
              placement="top"
            >
              <el-button
                type="info"
                size="small"
                link
                disabled
                style="cursor: not-allowed"
              >
                Edit
              </el-button>
            </el-tooltip>
            <el-button
              v-else
              type="primary"
              size="small"
              link
              @click="editEmployee(row)"
            >
              Edit
            </el-button>
            <el-button
              v-if="userRole === 'region' && !isCurrentUser(row)"
              type="danger"
              size="small"
              link
              @click="deleteEmployee(row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="loadEmployees"
          @size-change="loadEmployees"
        />
      </div>
    </el-card>

    <!-- Add/Edit Employee Dialog -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEditing ? 'Edit Employee' : 'Add New Employee'"
      width="650px"
      @close="resetForm"
    >
      <el-form :model="employeeForm" :rules="rules" ref="formRef" label-position="top">
        <!-- Basic Information Section -->
        <div class="form-section">
          <h4 class="section-title">Basic Information</h4>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="Full Name" prop="name">
                <el-input
                  v-model="employeeForm.name"
                  placeholder="Enter full name"
                  size="large"
                  :disabled="isEditing"
                />
              </el-form-item>
            </el-col>

            <el-col :span="24">
              <el-form-item label="Email" prop="email">
                <el-input
                  v-model="employeeForm.email"
                  type="email"
                  placeholder="Enter email address"
                  size="large"
                  :disabled="isEditing"
                />
              </el-form-item>
            </el-col>

            <el-col :span="12" v-if="!isEditing">
              <el-form-item label="Password" prop="passwd">
                <el-input
                  v-model="employeeForm.passwd"
                  type="password"
                  placeholder="Enter password"
                  size="large"
                  show-password
                />
              </el-form-item>
            </el-col>

            <el-col :span="12" v-if="!isEditing">
              <el-form-item label="Confirm Password" prop="confirmPassword">
                <el-input
                  v-model="employeeForm.confirmPassword"
                  type="password"
                  placeholder="Confirm password"
                  size="large"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- Employment Details Section -->
        <div class="form-section">
          <h4 class="section-title">Employment Details</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Job Title" prop="job_title">
                <el-select
                  v-model="employeeForm.job_title"
                  placeholder="Select job title"
                  size="large"
                  style="width: 100%"
                >
                  <el-option label="Sales Representative" value="Sales Representative" />
                  <el-option label="Store Manager" value="Store Manager" />
                  <el-option label="Regional Manager" value="Regional Manager" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="Annual Salary" prop="salary">
                <el-input-number
                  v-model="employeeForm.salary"
                  :min="0"
                  :step="1000"
                  :controls="false"
                  size="large"
                  style="width: 100%"
                >
                  <template #prefix>$</template>
                </el-input-number>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- Role Assignment Section (Region Manager Only) -->
        <div class="form-section" v-if="userRole === 'region'">
          <h4 class="section-title">Role & Store Assignment</h4>

          <el-form-item label="Employee Role">
            <el-radio-group v-model="employeeForm.role_type" size="large" @change="handleRoleChange">
              <el-radio value="sales">Sales Representative</el-radio>
              <el-radio value="manager">Store Manager</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Assign to Store" prop="store_id" v-if="employeeForm.role_type">
            <el-select
              v-model="employeeForm.store_id"
              placeholder="Select store"
              size="large"
              style="width: 100%"
              @change="handleStoreChange"
              filterable
            >
              <el-option
                v-for="store in availableStores"
                :key="store.id"
                :value="store.id"
                :label="store.name"
                :disabled="store.has_manager && employeeForm.role_type === 'manager' && (!isEditing || employeeForm.original_store_id !== store.id)"
              >
                <div class="store-option">
                  <span class="store-option-name">{{ store.name }}</span>
                  <el-tag v-if="store.has_manager && employeeForm.role_type === 'manager'" size="small" type="warning">
                    Has Manager
                  </el-tag>
                  <el-tag v-if="isEditing && employeeForm.original_store_id === store.id" size="small" type="success">
                    Current Store
                  </el-tag>
                </div>
              </el-option>
            </el-select>
            <div class="field-hint" v-if="employeeForm.role_type === 'manager'">
              <el-icon><InfoFilled /></el-icon>
              Each store can only have one manager. Stores with existing managers are disabled.
            </div>
          </el-form-item>
        </div>

        <!-- Store Assignment Section (Store Manager Only) -->
        <div class="form-section" v-if="userRole === 'manager'">
          <h4 class="section-title">Store Assignment</h4>

          <el-alert type="info" :closable="false" show-icon>
            <template #title>As a store manager, you can only add sales representatives to your store.</template>
          </el-alert>

          <el-form-item label="Store" style="margin-top: 16px">
            <el-input
              :value="managerStoreName"
              size="large"
              disabled
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false" size="large">Cancel</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving" size="large">
          {{ isEditing ? 'Update Employee' : 'Create Employee' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, InfoFilled } from '@element-plus/icons-vue'
import axios from '../../api/axios'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

// Props
const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (value) => ['manager', 'region'].includes(value)
  }
})

// Data
const loading = ref(false)
const saving = ref(false)
const employees = ref([])
const stores = ref([])
const searchQuery = ref('')
const roleFilter = ref(null)
const storeFilter = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
let searchTimeout = null

const showAddDialog = ref(false)
const isEditing = ref(false)
const formRef = ref(null)

const employeeForm = ref({
  name: '',
  email: '',
  passwd: '',
  confirmPassword: '',
  job_title: '',
  salary: 0,
  role_type: 'sales', // 'sales' or 'manager'
  store_id: null,
  original_store_id: null // For tracking original store when editing
})

// Computed
const userRole = computed(() => props.role)

const managerStoreName = computed(() => {
  if (userRole.value === 'manager') {
    const myStore = stores.value.find(s => s.is_my_store)
    return myStore?.name || ''
  }
  return ''
})

const availableStores = computed(() => {
  if (userRole.value === 'manager') {
    // Manager can only assign to their own store
    return stores.value.filter(s => s.is_my_store)
  }
  // For region manager, mark stores that already have managers
  return stores.value.map(store => ({
    ...store,
    has_manager: employees.value.some(emp =>
      emp.is_manager && emp.store_id === store.id && emp.id !== employeeForm.value.id
    )
  }))
})

// Client-side filtering for role and store
const displayedEmployees = computed(() => {
  let filtered = [...employees.value]

  // Filter by role
  if (roleFilter.value) {
    filtered = filtered.filter(emp => {
      if (roleFilter.value === 'region_manager') return emp.is_region_manager
      if (roleFilter.value === 'store_manager') return emp.is_manager && !emp.is_region_manager
      if (roleFilter.value === 'sales') return emp.is_salesperson && !emp.is_manager && !emp.is_region_manager
      if (roleFilter.value === 'employee') return !emp.is_salesperson && !emp.is_manager && !emp.is_region_manager
      return true
    })
  }

  // Filter by store
  if (storeFilter.value) {
    filtered = filtered.filter(emp => {
      // Regional managers don't belong to any store
      if (emp.is_region_manager) return false
      // Match by store_id
      return emp.store_id === storeFilter.value
    })
  }

  return filtered
})

// Form validation rules
const rules = computed(() => {
  const baseRules = {
    name: [
      { required: true, message: 'Please enter full name', trigger: 'blur' },
      { min: 2, message: 'Name must be at least 2 characters', trigger: 'blur' }
    ],
    email: [
      { required: true, message: 'Please enter email address', trigger: 'blur' },
      { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
    ],
    job_title: [
      { required: true, message: 'Please enter job title', trigger: 'blur' }
    ],
    salary: [
      { required: true, message: 'Please enter salary', trigger: 'blur' },
      { type: 'number', min: 0, message: 'Salary must be positive', trigger: 'blur' }
    ]
  }

  // Password rules only for new employees
  if (!isEditing.value) {
    baseRules.passwd = [
      { required: true, message: 'Please enter password', trigger: 'blur' },
      { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
    ]
    baseRules.confirmPassword = [
      { required: true, message: 'Please confirm password', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          if (value !== employeeForm.value.passwd) {
            callback(new Error('Passwords do not match'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }

  // Store selection required for region manager or when role is selected
  if (userRole.value === 'region' && employeeForm.value.role_type) {
    baseRules.store_id = [
      { required: true, message: 'Please select a store', trigger: 'change' }
    ]
  }

  return baseRules
})

// Methods
function isCurrentUser(employee) {
  // Check if this employee is the current logged-in user
  return employee.online_id === authStore.user?.online_id
}

function formatNumber(num) {
  if (num == null || num === undefined) return 'N/A'
  return Number(num).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function sortBySalary(a, b) {
  return a.salary - b.salary
}

function handleSearch() {
  // Debounce search
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadEmployees()
  }, 500)
}

function handleFilterChange() {
  // Role and store filters are now client-side, no need to reload
  // Just let the computed property handle it
}

function handleRoleChange() {
  // Reset store selection when role changes
  employeeForm.value.store_id = null
}

function handleStoreChange() {
  // Validate that selected store doesn't have a manager already
  if (employeeForm.value.role_type === 'manager' && employeeForm.value.store_id) {
    const selectedStore = availableStores.value.find(s => s.id === employeeForm.value.store_id)
    if (selectedStore?.has_manager && employeeForm.value.original_store_id !== employeeForm.value.store_id) {
      ElMessage.warning('This store already has a manager')
      employeeForm.value.store_id = null
    }
  }
}

async function loadStores() {
  try {
    const response = await axios.get('/stores')
    stores.value = response.data || []

    // Mark manager's own store
    // For store managers, backend only returns their own store, so mark all as is_my_store
    if (userRole.value === 'manager') {
      stores.value = stores.value.map(s => ({
        ...s,
        is_my_store: true
      }))
    }
  } catch (error) {
    console.error('Failed to load stores:', error)
  }
}

async function loadEmployees() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    // Store filter is now client-side, don't send to backend
    // if (storeFilter.value) {
    //   params.store_id = storeFilter.value
    // }

    const response = await axios.get('/employees', { params })
    employees.value = response.data.employees || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Failed to load employees:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to load employees')
    employees.value = []
  } finally {
    loading.value = false
  }
}

function editEmployee(employee) {
  isEditing.value = true

  // Determine role type based on employee flags
  let roleType = 'sales'
  if (employee.is_manager && !employee.is_region_manager) {
    roleType = 'manager'
  }

  employeeForm.value = {
    id: employee.id,
    name: employee.name,
    email: employee.email,
    passwd: '',
    confirmPassword: '',
    job_title: employee.job_title,
    salary: employee.salary / 100, // Convert from cents
    role_type: roleType,
    store_id: employee.store_id || null,
    original_store_id: employee.store_id || null
  }
  showAddDialog.value = true
}

async function deleteEmployee(employee) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete employee "${employee.name}"? This action cannot be undone.`,
      'Delete Employee',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await axios.delete(`/employees/${employee.id}`)
    ElMessage.success('Employee deleted successfully')
    await loadEmployees()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete employee:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to delete employee')
    }
  }
}

async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      // Prepare data based on role
      const data = {
        name: employeeForm.value.name,
        email: employeeForm.value.email,
        job_title: employeeForm.value.job_title,
        salary: Math.round(employeeForm.value.salary * 100) // Convert to cents
      }

      // For store manager: automatically assign to their store as sales
      if (userRole.value === 'manager') {
        const myStore = stores.value.find(s => s.is_my_store)
        data.is_salesperson = true
        data.store_id = myStore?.id
        data.is_manager = false
      }
      // For region manager: use selected role and store
      else if (userRole.value === 'region') {
        data.is_salesperson = employeeForm.value.role_type === 'sales' || employeeForm.value.role_type === 'manager'
        data.store_id = employeeForm.value.store_id
        data.is_manager = employeeForm.value.role_type === 'manager'
      }

      // Include password for new employees only
      if (!isEditing.value) {
        data.passwd = employeeForm.value.passwd
      }

      if (isEditing.value) {
        await axios.put(`/employees/${employeeForm.value.id}`, data)
        ElMessage.success('Employee updated successfully')
      } else {
        await axios.post('/employees', data)
        ElMessage.success('Employee created successfully')
      }

      showAddDialog.value = false
      await loadEmployees()
    } catch (error) {
      console.error('Failed to save employee:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to save employee')
    } finally {
      saving.value = false
    }
  })
}

function resetForm() {
  isEditing.value = false
  employeeForm.value = {
    name: '',
    email: '',
    passwd: '',
    confirmPassword: '',
    job_title: '',
    salary: 0,
    role_type: 'sales',
    store_id: null,
    original_store_id: null
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// Lifecycle
onMounted(() => {
  loadStores()
  loadEmployees()
})
</script>

<style scoped>
.sales-team-management {
  padding: 1rem 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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

.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.store-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.store-option-name {
  flex: 1;
}
</style>
