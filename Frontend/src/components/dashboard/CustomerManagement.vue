<template>
  <div class="customer-management">
    <el-card>
      <template #header>
        <div class="header-title">
          <h3>Customer Management</h3>
        </div>
      </template>

      <!-- Filters -->
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="Search by name or email"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="customerTypeFilter"
          placeholder="Customer Type"
          clearable
          style="width: 200px"
          @change="loadCustomers"
        >
          <el-option label="All Types" :value="null" />
          <el-option label="Home Customer" :value="0" />
          <el-option label="Business Customer" :value="1" />
        </el-select>

        <el-dropdown @command="handleColumnToggle">
          <el-button>
            <el-icon><Setting /></el-icon>
            Columns
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="col in availableColumns"
                :key="col.key"
                :command="col.key"
              >
                <el-checkbox :model-value="visibleColumns.includes(col.key)">
                  {{ col.label }}
                </el-checkbox>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- Customers Table -->
      <el-table
        :data="filteredAndSortedCustomers"
        v-loading="loading"
        stripe
        size="small"
        style="width: 100%; margin-top: 20px"
        @sort-change="handleSortChange"
      >
        <el-table-column
          prop="id"
          label="ID"
          min-width="60"
          sortable="custom"
          v-if="visibleColumns.includes('id')"
        />
        <el-table-column
          prop="name"
          label="Name"
          min-width="120"
          show-overflow-tooltip
          sortable="custom"
          :filters="getUniqueFilters('name')"
          :filter-method="filterHandler"
          column-key="name"
          v-if="visibleColumns.includes('name')"
        />
        <el-table-column
          prop="email"
          label="Email"
          min-width="180"
          show-overflow-tooltip
          sortable="custom"
          v-if="visibleColumns.includes('email')"
        />
        <el-table-column
          label="Type"
          min-width="80"
          column-key="type"
          :filters="[
            { text: 'Home', value: 0 },
            { text: 'Business', value: 1 }
          ]"
          :filter-method="filterHandler"
          v-if="visibleColumns.includes('type')"
        >
          <template #default="{ row }">
            <el-tag :type="row.kind === 0 ? 'success' : 'warning'" size="small">
              {{ row.kind === 0 ? 'Home' : 'Biz' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- Home Customer Columns -->
        <el-table-column
          label="Gender"
          min-width="80"
          column-key="gender"
          :filters="[
            { text: 'Male', value: 'Male' },
            { text: 'Female', value: 'Female' },
            { text: 'Other', value: 'Other' }
          ]"
          :filter-method="filterHandler"
          v-if="visibleColumns.includes('gender')"
        >
          <template #default="{ row }">
            {{ row.kind === 0 && row.details ? row.details.gender || '-' : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="Age"
          min-width="60"
          sortable="custom"
          column-key="age"
          v-if="visibleColumns.includes('age')"
        >
          <template #default="{ row }">
            {{ row.kind === 0 && row.details ? row.details.age || '-' : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="Marital"
          min-width="80"
          column-key="marital"
          :filters="[
            { text: 'Single', value: 0 },
            { text: 'Married', value: 1 },
            { text: 'Divorced', value: 2 },
            { text: 'Widowed', value: 3 }
          ]"
          :filter-method="filterHandler"
          v-if="visibleColumns.includes('marital')"
        >
          <template #default="{ row }">
            {{ row.kind === 0 && row.details ? getMaritalStatusShort(row.details.marriage_status) : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="Income"
          min-width="100"
          align="right"
          sortable="custom"
          column-key="income"
          v-if="visibleColumns.includes('income')"
        >
          <template #default="{ row }">
            {{ row.kind === 0 && row.details ? '$' + formatNumberShort(row.details.income) : '-' }}
          </template>
        </el-table-column>

        <!-- Business Customer Columns -->
        <el-table-column
          label="Company"
          min-width="150"
          show-overflow-tooltip
          sortable="custom"
          :filters="getUniqueFilters('company')"
          :filter-method="filterHandler"
          column-key="company"
          v-if="visibleColumns.includes('company')"
        >
          <template #default="{ row }">
            {{ row.kind === 1 && row.details ? row.details.company_name || '-' : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="Category"
          min-width="100"
          show-overflow-tooltip
          :filters="getUniqueFilters('category')"
          :filter-method="filterHandler"
          column-key="category"
          v-if="visibleColumns.includes('category')"
        >
          <template #default="{ row }">
            {{ row.kind === 1 && row.details ? row.details.category || '-' : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="Gross Income"
          min-width="120"
          align="right"
          sortable="custom"
          column-key="grossIncome"
          v-if="visibleColumns.includes('grossIncome')"
        >
          <template #default="{ row }">
            {{ row.kind === 1 && row.details ? '$' + formatNumberShort(row.details.gross_income) : '-' }}
          </template>
        </el-table-column>

        <!-- Sales Column -->
        <el-table-column
          label="Sales"
          min-width="120"
          show-overflow-tooltip
          :filters="getUniqueFilters('sales')"
          :filter-method="filterHandler"
          column-key="sales"
          v-if="visibleColumns.includes('sales')"
        >
          <template #default="{ row }">
            <span v-if="row.sales_name">{{ row.sales_name }}</span>
            <el-tag v-else type="info" size="small">Unassigned</el-tag>
          </template>
        </el-table-column>

        <!-- Order Count Column -->
        <el-table-column
          label="Orders"
          min-width="80"
          align="center"
          sortable="custom"
          column-key="orderCount"
          v-if="visibleColumns.includes('orderCount')"
        >
          <template #default="{ row }">
            {{ row.order_count || 0 }}
          </template>
        </el-table-column>

        <!-- Total Spending Column -->
        <el-table-column
          label="Total Spending"
          min-width="130"
          align="right"
          sortable="custom"
          column-key="totalSpending"
          v-if="visibleColumns.includes('totalSpending')"
        >
          <template #default="{ row }">
            ${{ formatNumberShort(row.total_spending / 100) }}
          </template>
        </el-table-column>

        <!-- Address Column -->
        <el-table-column
          label="Address"
          min-width="200"
          show-overflow-tooltip
          v-if="visibleColumns.includes('address')"
        >
          <template #default="{ row }">
            <span v-if="row.address">
              {{ formatAddress(row.address) }}
            </span>
            <el-tag v-else type="info" size="small">No Address</el-tag>
          </template>
        </el-table-column>

        <!-- Actions Column -->
        <el-table-column label="Actions" width="90" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="viewCustomerDetails(row)"
            >
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Customer Details Dialog -->
    <el-dialog
      v-model="detailsDialogVisible"
      :title="`Customer Details - ${selectedCustomer?.name}`"
      width="700px"
    >
      <div v-if="selectedCustomer" class="customer-details">
        <!-- Statistics Section -->
        <el-card class="stats-card" shadow="never">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">Total Orders</div>
              <div class="stat-value">{{ selectedCustomer.order_count || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Total Spending</div>
              <div class="stat-value">${{ formatNumber((selectedCustomer.total_spending || 0) / 100) }}</div>
            </div>
          </div>
        </el-card>

        <!-- Edit Form -->
        <el-form :model="editForm" label-width="150px" style="margin-top: 20px">
          <el-form-item label="Customer ID">
            <el-input v-model="selectedCustomer.id" disabled />
          </el-form-item>
          <el-form-item label="Name">
            <el-input v-model="selectedCustomer.name" disabled />
          </el-form-item>
          <el-form-item label="Email">
            <el-input v-model="selectedCustomer.email" disabled />
          </el-form-item>
          <el-form-item label="Customer Type">
            <el-tag :type="selectedCustomer.kind === 0 ? 'success' : 'warning'">
              {{ selectedCustomer.kind === 0 ? 'Home Customer' : 'Business Customer' }}
            </el-tag>
          </el-form-item>

          <!-- Address Information -->
          <el-divider content-position="left">Address Information</el-divider>
          <el-form-item label="Address Line 1">
            <el-input v-model="editForm.address.address_1" :disabled="!isEditing" placeholder="Street address, P.O. box" />
          </el-form-item>
          <el-form-item label="Address Line 2">
            <el-input v-model="editForm.address.address_2" :disabled="!isEditing" placeholder="Apartment, suite, unit, building, floor, etc." />
          </el-form-item>
          <el-form-item label="City / State / ZIP">
            <el-row :gutter="10">
              <el-col :span="10">
                <el-input v-model="editForm.address.city" :disabled="!isEditing" placeholder="City" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="editForm.address.state" :disabled="!isEditing" placeholder="State" maxlength="2" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="editForm.address.zipcode" :disabled="!isEditing" placeholder="ZIP Code" maxlength="10" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-divider content-position="left">Customer Details</el-divider>

          <!-- Home Customer Details -->
          <template v-if="selectedCustomer.kind === 0">
            <el-form-item label="Gender">
              <el-select v-model="editForm.gender" :disabled="!isEditing">
                <el-option label="Male" value="Male" />
                <el-option label="Female" value="Female" />
                <el-option label="Non-binary" value="Non-binary" />
                <el-option label="PreferNoToSay" value="PreferNoToSay" />
              </el-select>
            </el-form-item>
            <el-form-item label="Age">
              <el-input-number v-model="editForm.age" :min="0" :max="150" :disabled="!isEditing" />
            </el-form-item>
            <el-form-item label="Marital Status">
              <el-select v-model="editForm.marriage_status" :disabled="!isEditing">
                <el-option label="Single" :value="0" />
                <el-option label="Married" :value="1" />
                <el-option label="Divorced" :value="2" />
                <el-option label="Widowed" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item label="Annual Income">
              <el-input-number v-model="editForm.income" :min="0" :step="1000" :disabled="!isEditing" />
            </el-form-item>
          </template>

          <!-- Business Customer Details -->
          <template v-if="selectedCustomer.kind === 1">
            <el-form-item label="Company Name">
              <el-input v-model="editForm.company_name" :disabled="!isEditing" />
            </el-form-item>
            <el-form-item label="Business Category">
              <el-input v-model="editForm.category" :disabled="!isEditing" />
            </el-form-item>
            <el-form-item label="Gross Income">
              <el-input-number v-model="editForm.gross_income" :min="0" :step="10000" :disabled="!isEditing" />
            </el-form-item>
          </template>

          <!-- Sales Assignment -->
          <el-form-item label="Assigned Sales">
            <el-select
              v-model="editForm.sales_id"
              :disabled="!isEditing"
              clearable
              placeholder="Select sales person"
            >
              <el-option
                v-for="sales in salesList"
                :key="sales.employee_id"
                :label="sales.name"
                :value="sales.employee_id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailsDialogVisible = false">Cancel</el-button>
          <el-button v-if="!isEditing" type="primary" @click="startEditing">
            Edit Customer
          </el-button>
          <el-button v-else type="success" @click="saveCustomer" :loading="saving">
            Save Changes
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Setting, ArrowDown } from '@element-plus/icons-vue'
import axios from '../../api/axios'

// Data
const loading = ref(false)
const customers = ref([])
const searchQuery = ref('')
const customerTypeFilter = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const detailsDialogVisible = ref(false)
const selectedCustomer = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const editForm = ref({})
const salesList = ref([])

// Sorting and filtering state
const sortColumn = ref('')
const sortOrder = ref('')
const activeFilters = ref({})

// Column visibility
const availableColumns = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'type', label: 'Type' },
  { key: 'gender', label: 'Gender (Home)' },
  { key: 'age', label: 'Age (Home)' },
  { key: 'marital', label: 'Marital (Home)' },
  { key: 'income', label: 'Income (Home)' },
  { key: 'company', label: 'Company (Biz)' },
  { key: 'category', label: 'Category (Biz)' },
  { key: 'grossIncome', label: 'Gross Income (Biz)' },
  { key: 'sales', label: 'Assigned Sales' },
  { key: 'orderCount', label: 'Order Count' },
  { key: 'totalSpending', label: 'Total Spending' },
  { key: 'address', label: 'Address' }
]

const visibleColumns = ref([
  'id', 'name', 'email', 'type', 'sales', 'orderCount', 'totalSpending', 'address'
])

// Computed - Filtered and Sorted Data
const filteredAndSortedCustomers = computed(() => {
  let result = [...customers.value]

  // Apply filters
  Object.keys(activeFilters.value).forEach(columnKey => {
    const filterValues = activeFilters.value[columnKey]
    if (filterValues && filterValues.length > 0) {
      result = result.filter(row => {
        return filterValues.some(filterValue => {
          switch (columnKey) {
            case 'name':
              return row.name === filterValue
            case 'type':
              return row.kind === filterValue
            case 'gender':
              return row.kind === 0 && row.details?.gender === filterValue
            case 'marital':
              return row.kind === 0 && row.details?.marriage_status === filterValue
            case 'company':
              return row.kind === 1 && row.details?.company_name === filterValue
            case 'category':
              return row.kind === 1 && row.details?.category === filterValue
            case 'sales':
              return row.sales_name === filterValue
            default:
              return true
          }
        })
      })
    }
  })

  // Apply sorting
  if (sortColumn.value && sortOrder.value) {
    result.sort((a, b) => {
      let aValue, bValue

      switch (sortColumn.value) {
        case 'id':
          aValue = a.id
          bValue = b.id
          break
        case 'name':
          aValue = a.name || ''
          bValue = b.name || ''
          break
        case 'email':
          aValue = a.email || ''
          bValue = b.email || ''
          break
        case 'age':
          aValue = a.kind === 0 && a.details ? a.details.age : 0
          bValue = b.kind === 0 && b.details ? b.details.age : 0
          break
        case 'income':
          aValue = a.kind === 0 && a.details ? a.details.income : 0
          bValue = b.kind === 0 && b.details ? b.details.income : 0
          break
        case 'company':
          aValue = a.kind === 1 && a.details ? a.details.company_name || '' : ''
          bValue = b.kind === 1 && b.details ? b.details.company_name || '' : ''
          break
        case 'grossIncome':
          aValue = a.kind === 1 && a.details ? a.details.gross_income : 0
          bValue = b.kind === 1 && b.details ? b.details.gross_income : 0
          break
        case 'orderCount':
          aValue = a.order_count || 0
          bValue = b.order_count || 0
          break
        case 'totalSpending':
          aValue = a.total_spending || 0
          bValue = b.total_spending || 0
          break
        default:
          return 0
      }

      // Handle string vs number comparison
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder.value === 'ascending'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      } else {
        return sortOrder.value === 'ascending'
          ? aValue - bValue
          : bValue - aValue
      }
    })
  }

  return result
})

// Methods
async function loadCustomers() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (customerTypeFilter.value !== null) {
      params.kind = customerTypeFilter.value
    }

    const response = await axios.get('/customers', { params })
    customers.value = response.data.customers || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Failed to load customers:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to load customers')
    customers.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadCustomers()
}

function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
  loadCustomers()
}

function handleCurrentChange(newPage) {
  currentPage.value = newPage
  loadCustomers()
}

async function viewCustomerDetails(customer) {
  try {
    loading.value = true
    // Fetch full customer details
    const response = await axios.get(`/customers/${customer.id}`)
    selectedCustomer.value = response.data

    // Initialize edit form with customer data
    const addressData = {
      address_1: response.data.address?.address_1 || '',
      address_2: response.data.address?.address_2 || '',
      city: response.data.address?.city || '',
      state: response.data.address?.state || '',
      zipcode: response.data.address?.zipcode || null
    }

    if (response.data.kind === 0) {
      // Home customer
      editForm.value = {
        address: addressData,
        gender: response.data.details?.gender || '',
        age: response.data.details?.age || 0,
        marriage_status: response.data.details?.marriage_status || 0,
        income: response.data.details?.income || 0,
        sales_id: response.data.sales_id
      }
    } else {
      // Business customer
      editForm.value = {
        address: addressData,
        company_name: response.data.details?.company_name || '',
        category: response.data.details?.category || '',
        gross_income: response.data.details?.gross_income || 0,
        sales_id: response.data.sales_id
      }
    }

    isEditing.value = false
    detailsDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load customer details:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to load customer details')
  } finally {
    loading.value = false
  }
}

function startEditing() {
  isEditing.value = true
}

async function saveCustomer() {
  try {
    saving.value = true
    await axios.put(`/customers/${selectedCustomer.value.id}`, editForm.value)
    ElMessage.success('Customer updated successfully')
    isEditing.value = false
    detailsDialogVisible.value = false
    await loadCustomers()
  } catch (error) {
    console.error('Failed to update customer:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to update customer')
  } finally {
    saving.value = false
  }
}

async function loadSalesList() {
  try {
    const response = await axios.get('/customers/sales-list')
    salesList.value = response.data.salespeople || []
  } catch (error) {
    console.error('Failed to load sales list:', error)
  }
}

function handleColumnToggle(key) {
  const index = visibleColumns.value.indexOf(key)
  if (index > -1) {
    visibleColumns.value.splice(index, 1)
  } else {
    visibleColumns.value.push(key)
  }
}

function handleSortChange({ column, prop, order }) {
  if (order) {
    sortColumn.value = column?.columnKey || prop || ''
    sortOrder.value = order
  } else {
    sortColumn.value = ''
    sortOrder.value = ''
  }
}

function filterHandler(value, row, column) {
  const columnKey = column.columnKey

  switch (columnKey) {
    case 'name':
      return row.name === value
    case 'type':
      return row.kind === value
    case 'gender':
      return row.kind === 0 && row.details?.gender === value
    case 'marital':
      return row.kind === 0 && row.details?.marriage_status === value
    case 'company':
      return row.kind === 1 && row.details?.company_name === value
    case 'category':
      return row.kind === 1 && row.details?.category === value
    case 'sales':
      return row.sales_name === value
    default:
      return true
  }
}

function getUniqueFilters(columnKey) {
  const uniqueValues = new Set()

  customers.value.forEach(customer => {
    let value = null

    switch (columnKey) {
      case 'name':
        value = customer.name
        break
      case 'company':
        if (customer.kind === 1 && customer.details?.company_name) {
          value = customer.details.company_name
        }
        break
      case 'category':
        if (customer.kind === 1 && customer.details?.category) {
          value = customer.details.category
        }
        break
      case 'sales':
        if (customer.sales_name) {
          value = customer.sales_name
        }
        break
    }

    if (value) {
      uniqueValues.add(value)
    }
  })

  return Array.from(uniqueValues).sort().map(val => ({
    text: val,
    value: val
  }))
}

function formatNumber(num) {
  if (num == null || num === undefined) return 'N/A'
  return Number(num).toLocaleString('en-US')
}

function formatNumberShort(num) {
  if (num == null || num === undefined) return '-'
  const n = Number(num)
  if (n >= 1000000) {
    return (n / 1000000).toFixed(1) + 'M'
  } else if (n >= 1000) {
    return (n / 1000).toFixed(1) + 'K'
  }
  return n.toLocaleString('en-US')
}

function formatAddress(address) {
  if (!address) return 'N/A'
  const parts = []
  if (address.address_1) parts.push(address.address_1)
  if (address.address_2) parts.push(address.address_2)
  if (address.city) parts.push(address.city)
  if (address.state) parts.push(address.state)
  if (address.zipcode) parts.push(address.zipcode)
  return parts.join(', ') || 'N/A'
}

function getMaritalStatus(status) {
  const statusMap = {
    0: 'Single',
    1: 'Married',
    2: 'Divorced',
    3: 'Widowed'
  }
  return statusMap[status] || 'N/A'
}

function getMaritalStatusShort(status) {
  const statusMap = {
    0: 'Single',
    1: 'Married',
    2: 'Div',
    3: 'Widow'
  }
  return statusMap[status] || '-'
}

// Lifecycle
onMounted(() => {
  loadCustomers()
  loadSalesList()
})
</script>

<style scoped>
.customer-management {
  padding: 1rem 0;
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

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.customer-details {
  margin: 20px 0;
}

.stats-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 20px;
}

.stats-card :deep(.el-card__body) {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
