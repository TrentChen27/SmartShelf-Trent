<template>
  <div class="store-management">
    <el-card>
      <!-- Header -->
      <template #header>
        <div class="header-actions">
          <h3>Store Management</h3>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            Add Store
          </el-button>
        </div>
      </template>

      <!-- Search Bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Search by store name, manager, or address"
          clearable
          style="max-width: 400px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- Stores Table -->
      <el-table
        :data="paginatedStores"
        v-loading="loading"
        stripe
        size="small"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="Store Name" min-width="150" show-overflow-tooltip />
        <el-table-column label="Manager" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.manager_name || 'Not Assigned' }}
          </template>
        </el-table-column>
        <el-table-column label="Address" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatAddress(row.address) }}
          </template>
        </el-table-column>
        <el-table-column label="Region" min-width="120">
          <template #default="{ row }">
            {{ row.region_name || 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="editStore(row)"
            >
              Edit
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="deleteStore(row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div v-if="filteredStores.length > 0" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredStores.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Store Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? 'Edit Store' : 'Add New Store'"
      width="650px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="storeForm"
        :rules="rules"
        label-position="top"
        size="large"
      >
        <!-- Store Name -->
        <div class="form-section">
          <h4 class="section-title">Store Information</h4>
          <el-form-item label="Store Name" prop="name">
            <el-input
              v-model="storeForm.name"
              placeholder="Enter store name"
            />
          </el-form-item>

          <el-alert type="info" :closable="false" show-icon>
            To assign or change the store manager, please go to the <strong>Employees</strong> section.
          </el-alert>
        </div>

        <!-- Address -->
        <div class="form-section">
          <h4 class="section-title">Address</h4>
          <el-form-item label="Address Line 1">
            <el-input
              v-model="storeForm.address.address_1"
              placeholder="Street address, P.O. box"
            />
          </el-form-item>

          <el-form-item label="Address Line 2">
            <el-input
              v-model="storeForm.address.address_2"
              placeholder="Apartment, suite, unit, building, floor, etc."
            />
          </el-form-item>

          <el-form-item label="City / State / ZIP">
            <el-row :gutter="10">
              <el-col :span="10">
                <el-input
                  v-model="storeForm.address.city"
                  placeholder="City"
                />
              </el-col>
              <el-col :span="6">
                <el-input
                  v-model="storeForm.address.state"
                  placeholder="State"
                  maxlength="2"
                />
              </el-col>
              <el-col :span="8">
                <el-input
                  v-model="storeForm.address.zipcode"
                  placeholder="ZIP Code"
                  maxlength="10"
                />
              </el-col>
            </el-row>
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false" size="large">Cancel</el-button>
        <el-button
          type="primary"
          @click="submitForm"
          :loading="saving"
          size="large"
        >
          {{ isEditing ? 'Update Store' : 'Create Store' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import axios from '../../api/axios'

// Data
const loading = ref(false)
const saving = ref(false)
const stores = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const showDialog = ref(false)
const isEditing = ref(false)
const formRef = ref(null)

const storeForm = ref({
  id: null,
  name: '',
  address: {
    address_1: '',
    address_2: '',
    city: '',
    state: '',
    zipcode: ''
  }
})

const rules = {
  name: [
    { required: true, message: 'Please enter store name', trigger: 'blur' },
    { min: 2, message: 'Store name must be at least 2 characters', trigger: 'blur' }
  ]
}

// Computed
const filteredStores = computed(() => {
  if (!searchQuery.value) {
    return stores.value
  }

  const query = searchQuery.value.toLowerCase()
  return stores.value.filter(store => {
    // Search by store name
    if (store.name?.toLowerCase().includes(query)) return true

    // Search by manager name
    if (store.manager_name?.toLowerCase().includes(query)) return true

    // Search by address
    if (store.address) {
      const addressStr = [
        store.address.address_1,
        store.address.address_2,
        store.address.city,
        store.address.state,
        store.address.zipcode
      ].filter(Boolean).join(' ').toLowerCase()

      if (addressStr.includes(query)) return true
    }

    // Search by region name
    if (store.region_name?.toLowerCase().includes(query)) return true

    return false
  })
})

const paginatedStores = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStores.value.slice(start, end)
})

// Methods
function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
}

function handleCurrentChange(newPage) {
  currentPage.value = newPage
}
function formatAddress(address) {
  if (!address) return 'No address'

  const parts = []
  if (address.address_1) parts.push(address.address_1)
  if (address.city) parts.push(address.city)
  if (address.state) parts.push(address.state)
  if (address.zipcode) parts.push(address.zipcode)

  return parts.join(', ') || 'No address'
}

async function loadStores() {
  loading.value = true
  try {
    const response = await axios.get('/stores')
    stores.value = response.data || []
  } catch (error) {
    console.error('Failed to load stores:', error)
    ElMessage.error('Failed to load stores')
  } finally {
    loading.value = false
  }
}

function openAddDialog() {
  isEditing.value = false
  resetForm()
  showDialog.value = true
}

function editStore(store) {
  isEditing.value = true

  storeForm.value = {
    id: store.id,
    name: store.name,
    address: {
      address_1: store.address?.address_1 || '',
      address_2: store.address?.address_2 || '',
      city: store.address?.city || '',
      state: store.address?.state || '',
      zipcode: store.address?.zipcode || ''
    }
  }

  showDialog.value = true
}

function resetForm() {
  storeForm.value = {
    id: null,
    name: '',
    address: {
      address_1: '',
      address_2: '',
      city: '',
      state: '',
      zipcode: ''
    }
  }
  formRef.value?.clearValidate()
}

async function submitForm() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  try {
    const data = {
      name: storeForm.value.name,
      address: storeForm.value.address
    }

    if (isEditing.value) {
      await axios.put(`/stores/${storeForm.value.id}`, data)
      ElMessage.success('Store updated successfully')
    } else {
      await axios.post('/stores', data)
      ElMessage.success('Store created successfully')
    }

    showDialog.value = false
    await loadStores()
  } catch (error) {
    console.error('Failed to save store:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to save store')
  } finally {
    saving.value = false
  }
}

async function deleteStore(store) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${store.name}"? This action cannot be undone.`,
      'Delete Store',
      {
        confirmButtonText: 'Yes, Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await axios.delete(`/stores/${store.id}`)
    ElMessage.success('Store deleted successfully')
    await loadStores()
  } catch (error) {
    if (error === 'cancel') return

    console.error('Failed to delete store:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to delete store')
  }
}

// Lifecycle
onMounted(() => {
  loadStores()
})
</script>

<style scoped>
.store-management {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.search-bar {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

</style>
