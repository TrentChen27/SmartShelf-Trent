<template>
  <div class="order-management">
    <!-- Filters -->
    <div class="filters">
      <el-input
        v-model="searchQuery"
        :placeholder="role === 'customer' ? 'Search by product name...' : 'Search by customer name, email, or product'"
        clearable
        style="width: 300px"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-if="role === 'sales'"
        v-model="selectedCustomer"
        placeholder="All Customers"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="All Customers" :value="null" />
        <!-- TODO: Load customers from API -->
      </el-select>

      <el-select
        v-if="role === 'manager'"
        v-model="selectedSales"
        placeholder="All Sales"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="All Sales" :value="null" />
        <el-option
          v-for="sales in salesList"
          :key="sales.id"
          :label="sales.name"
          :value="sales.id"
        />
      </el-select>

      <el-select
        v-if="role === 'region'"
        v-model="selectedStore"
        placeholder="All Stores"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="All Stores" :value="null" />
        <el-option
          v-for="store in storesList"
          :key="store.id"
          :label="store.name"
          :value="store.id"
        />
      </el-select>

      <el-select
        v-model="statusFilter"
        placeholder="All Status"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="All Status" :value="null" />
        <el-option label="Ordered" :value="0" />
        <el-option label="Pending" :value="1" />
        <el-option label="Complete" :value="2" />
        <el-option label="Cancelled" :value="3" />
      </el-select>

      <el-select
        v-model="paymentFilter"
        placeholder="All Payment Status"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="All Payment Status" :value="null" />
        <el-option label="Paid" :value="true" />
        <el-option label="Unpaid" :value="false" />
      </el-select>
    </div>

    <!-- Orders List -->
    <div class="orders-section">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="orders.length === 0" class="empty-state">
        <el-empty :description="emptyMessage">
          <el-button v-if="role === 'customer'" type="primary" @click="$router.push('/')">
            Start Shopping
          </el-button>
        </el-empty>
      </div>

      <div v-else class="orders-list">
        <el-collapse v-model="expandedOrders" accordion>
          <el-collapse-item v-for="order in orders" :key="order.id" :name="order.id">
            <template #title>
              <div class="order-summary">
                <div class="order-summary-left">
                  <span class="order-id">Order #{{ order.id }}</span>
                  <span class="order-date-compact">{{ formatDateCompact(order.order_date) }}</span>
                  <span v-if="role !== 'customer' && order.customer_name" class="customer-name-compact">
                    {{ order.customer_name }}
                  </span>
                  <span class="order-items-preview">{{ getOrderItemsPreview(order) }}</span>
                </div>
                <div class="order-summary-right">
                  <span class="order-total-compact">${{ (order.total_amount / 100).toFixed(2) }}</span>
                  <el-tag :type="getStatusType(order.pickup_status)" size="small">
                    {{ getStatusText(order.pickup_status) }}
                  </el-tag>
                  <el-tag :type="getPaymentStatusType(order.payment_status)" size="small">
                    {{ getPaymentStatusText(order.payment_status) }}
                  </el-tag>
                </div>
              </div>
            </template>

            <!-- Expanded Order Details -->
            <div class="order-details-expanded">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="Order Date">
                  {{ formatDate(order.order_date) }}
                </el-descriptions-item>
                <el-descriptions-item label="Pickup Store">
                  <el-icon><Location /></el-icon>
                  {{ order.store?.name || `Store #${order.store_id}` }}
                </el-descriptions-item>
                <el-descriptions-item v-if="order.pickup_status === 2 && order.pickup_date" label="Pickup Date" :span="2">
                  {{ formatDate(order.pickup_date) }}
                </el-descriptions-item>
                <el-descriptions-item v-if="role !== 'customer' && order.customer_name" label="Customer">
                  {{ order.customer_name }}
                </el-descriptions-item>
                <el-descriptions-item v-if="role !== 'customer' && order.sales_name" label="Sales Person">
                  {{ order.sales_name }}
                </el-descriptions-item>
                <el-descriptions-item v-if="role !== 'customer' && order.customer_address" label="Customer Address" :span="2">
                  <el-icon><LocationFilled /></el-icon>
                  {{ formatCustomerAddress(order.customer_address) }}
                </el-descriptions-item>
              </el-descriptions>

              <el-divider content-position="left">Order Items</el-divider>

              <div class="order-items">
                <div v-for="item in order.items" :key="item.id" class="order-item">
                  <div class="item-image-wrapper">
                    <img
                      :src="item.product?.image_url || '/placeholder.png'"
                      :alt="item.product?.product_name"
                      class="item-image"
                    />
                  </div>
                  <div class="item-info">
                    <span class="item-name">{{ item.product?.product_name || `Product #${item.product_id}` }}</span>
                    <span class="item-quantity">Qty: {{ item.quantity }}</span>
                  </div>
                  <div class="item-price">${{ (item.sub_price / 100).toFixed(2) }}</div>
                </div>
              </div>

              <div class="order-total">
                <span>Total Amount:</span>
                <span class="total-amount">${{ (order.total_amount / 100).toFixed(2) }}</span>
              </div>

              <!-- Customer Actions -->
              <div v-if="role === 'customer'" class="order-actions">
                <el-button
                  v-if="order.pickup_status === 0 && !order.payment_status"
                  type="primary"
                  @click="openPaymentDialog(order)"
                >
                  <el-icon><CreditCard /></el-icon>
                  Pay Now
                </el-button>
                <el-button
                  v-if="order.pickup_status === 0 || order.pickup_status === 1"
                  type="danger"
                  @click="handleCancelOrder(order.id)"
                >
                  Cancel Order
                </el-button>
              </div>

              <!-- Sales Actions (Only sales can manage orders) -->
              <div v-else-if="role === 'sales'" class="order-actions">
                <el-button
                  v-if="order.pickup_status === 1"
                  type="success"
                  @click="handleUpdateStatus(order.id, 2)"
                >
                  Mark as Complete
                </el-button>
                <el-button
                  v-if="order.pickup_status === 0 || order.pickup_status === 1"
                  type="danger"
                  @click="handleUpdateStatus(order.id, 3)"
                >
                  Cancel Order
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="pagination">
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
    </div>

    <!-- Payment Dialog -->
    <CreditCardPayment
      v-model="paymentDialogVisible"
      :order="selectedOrder"
      @success="handlePaymentSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location, LocationFilled, CreditCard, Search } from '@element-plus/icons-vue'
import { getOrders, cancelOrder, updateOrderStatus } from '../../api/orders'
import CreditCardPayment from '../payment/CreditCardPayment.vue'
import axios from '../../api/axios'

const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (value) => ['customer', 'sales', 'manager', 'region'].includes(value)
  }
})

// Data
const loading = ref(false)
const orders = ref([])
const salesList = ref([])
const storesList = ref([])
const searchQuery = ref('')
const selectedCustomer = ref(null)
const selectedSales = ref(null)
const selectedStore = ref(null)
const statusFilter = ref(null)
const paymentFilter = ref(null)

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Collapse state
const expandedOrders = ref([])

const paymentDialogVisible = ref(false)
const selectedOrder = ref(null)

// Computed
const emptyMessage = computed(() => {
  if (props.role === 'customer') {
    return 'No orders yet'
  }
  return 'No orders found'
})

// Methods
async function loadSalesList() {
  if (props.role !== 'manager') return

  try {
    const response = await axios.get('/employees')
    const employees = response.data.employees || []
    // Filter to only get salespeople (not managers or regional managers)
    salesList.value = employees
      .filter(emp => emp.is_salesperson && !emp.is_region_manager)
      .map(emp => ({
        id: emp.id,
        name: emp.name
      }))
  } catch (error) {
    console.error('Failed to load sales list:', error)
  }
}

async function loadStoresList() {
  if (props.role !== 'region') return

  try {
    const response = await axios.get('/stores')
    storesList.value = response.data || []
  } catch (error) {
    console.error('Failed to load stores list:', error)
  }
}

async function loadOrders() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }

    // Add filters based on role
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCustomer.value) params.customer_id = selectedCustomer.value
    if (selectedSales.value) params.sales_id = selectedSales.value
    if (selectedStore.value) params.store_id = selectedStore.value
    if (statusFilter.value !== null) params.status = statusFilter.value
    if (paymentFilter.value !== null) params.payment_status = paymentFilter.value

    const response = await getOrders(params)
    orders.value = response.data.orders || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Failed to load orders:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to load orders')
    orders.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1  // Reset to first page when searching
  loadOrders()
}

function handleFilterChange() {
  currentPage.value = 1  // Reset to first page when filter changes
  loadOrders()
}

function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1  // Reset to first page when changing page size
  loadOrders()
}

function handleCurrentChange(newPage) {
  currentPage.value = newPage
  loadOrders()
}

async function handleCancelOrder(orderId) {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to cancel this order? This action cannot be undone.',
      'Cancel Order',
      {
        confirmButtonText: 'Yes, Cancel Order',
        cancelButtonText: 'No, Keep Order',
        type: 'warning'
      }
    )

    await cancelOrder(orderId)
    ElMessage.success('Order cancelled successfully')
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to cancel order:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to cancel order')
    }
  }
}

function openPaymentDialog(order) {
  selectedOrder.value = order
  paymentDialogVisible.value = true
}

async function handlePaymentSuccess() {
  ElMessage.success('Payment successful! Your order has been paid.')
  await loadOrders()
}

async function handleUpdateStatus(orderId, status) {
  try {
    let statusText = ''
    switch (status) {
      case 2: statusText = 'complete'; break
      case 3: statusText = 'cancelled'; break
      default: statusText = 'updated'
    }

    await ElMessageBox.confirm(
      `Mark this order as ${statusText}?`,
      'Update Order Status',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await updateOrderStatus(orderId, status)
    ElMessage.success(`Order marked as ${statusText}`)
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to update order status:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to update order status')
    }
  }
}


function formatDate(dateStr) {
  if (!dateStr) return 'N/A'

  // Parse the date
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr // Return as-is if invalid

  // Only show date, no time
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatDateCompact(dateStr) {
  if (!dateStr) return 'N/A'

  // Handle string dates that may already be formatted
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) {
    // If it's already a string like "2025-06-15", extract just the date part
    const dateOnly = dateStr.split(' ')[0]
    return dateOnly
  }

  // Only show date, no time
  return date.toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric'
  })
}

// Get order items preview for collapsed view
function getOrderItemsPreview(order) {
  if (!order.items || order.items.length === 0) return ''

  const itemNames = order.items.map(item =>
    item.product?.product_name || `Product #${item.product_id}`
  )

  return itemNames.join(', ')
}

// Combined status based on both pickup_status and payment_status
function getCombinedStatusType(order) {
  const { pickup_status, payment_status } = order

  // Cancelled
  if (pickup_status === 3) {
    return 'info'
  }

  // Complete (always paid)
  if (pickup_status === 2) {
    return 'success'
  }

  // Pending (paid, waiting for pickup)
  if (pickup_status === 1 && payment_status) {
    return 'primary'
  }

  // Ordered but unpaid
  if (pickup_status === 0 && !payment_status) {
    return 'warning'
  }

  return ''
}

function getCombinedStatusText(order) {
  const { pickup_status, payment_status } = order

  // Cancelled
  if (pickup_status === 3) {
    return payment_status ? 'Cancelled (Paid)' : 'Cancelled (Unpaid)'
  }

  // Complete (always paid)
  if (pickup_status === 2) {
    return 'Complete (Paid)'
  }

  // Pending (paid, waiting for pickup)
  if (pickup_status === 1 && payment_status) {
    return 'Pending (Paid)'
  }

  // Ordered but unpaid
  if (pickup_status === 0 && !payment_status) {
    return 'Ordered (Unpaid)'
  }

  // Fallback for unexpected states
  return 'Unknown'
}

function getStatusType(status) {
  switch (status) {
    case 0: return 'warning' // Ordered
    case 1: return 'primary' // Pending
    case 2: return 'success' // Complete
    case 3: return 'info'    // Cancelled
    default: return ''
  }
}

function getStatusText(status) {
  switch (status) {
    case 0: return 'Ordered'
    case 1: return 'Pending'
    case 2: return 'Complete'
    case 3: return 'Cancelled'
    default: return 'Unknown'
  }
}

function getPaymentStatusType(paid) {
  return paid ? 'success' : 'warning'
}

function getPaymentStatusText(paid) {
  return paid ? 'Paid' : 'Unpaid'
}

function formatCustomerAddress(address) {
  if (!address) return 'N/A'
  const parts = []
  if (address.address_1) parts.push(address.address_1)
  if (address.address_2) parts.push(address.address_2)
  if (address.city) parts.push(address.city)
  if (address.state) parts.push(address.state)
  if (address.zipcode) parts.push(address.zipcode)
  return parts.join(', ') || 'N/A'
}

// Lifecycle
onMounted(() => {
  loadSalesList()
  loadStoresList()
  loadOrders()
})
</script>

<style scoped>
.order-management {
  padding: 1rem 0;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.orders-section {
  min-height: 400px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 3rem;
  font-size: 16px;
  color: #666;
}

.empty-state {
  padding: 3rem;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Override Element Plus collapse item title styles */
.orders-list :deep(.el-collapse-item__header) {
  overflow: hidden;
  width: 100%;
}

.orders-list :deep(.el-collapse-item__arrow) {
  flex-shrink: 0;
}

/* Order Summary (Collapsed State) */
.order-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 2rem;
  gap: 0.5rem;
  overflow: hidden;
  min-width: 0;
}

.order-summary-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1 1 0;
  min-width: 0;
  overflow: hidden;
}

.order-id {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  flex: 0 0 auto;
  white-space: nowrap;
  width: auto;
  max-width: 120px;
}

.order-date-compact {
  color: #909399;
  font-size: 13px;
  flex: 0 0 auto;
  white-space: nowrap;
  width: auto;
  max-width: 100px;
}

.customer-name-compact {
  color: #606266;
  font-size: 13px;
  flex: 0 0 auto;
  white-space: nowrap;
  width: auto;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.order-items-preview {
  color: #909399;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1 1 auto;
  min-width: 0;
  width: 0;
}

.order-summary-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
  justify-content: flex-end;
  margin-left: auto;
}

.order-summary-right .el-button {
  margin-left: 0.25rem;
  flex: 0 0 auto;
  white-space: nowrap;
}

.order-summary-right .el-tag {
  flex: 0 0 auto;
  white-space: nowrap;
}

.order-total-compact {
  font-weight: 600;
  font-size: 16px;
  color: #409eff;
  min-width: 90px;
  text-align: right;
  flex: 0 0 auto;
  white-space: nowrap;
}

/* Expanded Order Details */
.order-details-expanded {
  padding: 1rem 0;
}

.customer-address {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.customer-address .el-icon {
  color: #67c23a;
  font-size: 14px;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.item-image-wrapper {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-name {
  font-weight: 500;
}

.item-quantity {
  font-size: 14px;
  color: #666;
}

.item-price {
  font-weight: 600;
  color: #409eff;
}

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 2px solid #eee;
  font-size: 18px;
  font-weight: 600;
}

.total-amount {
  color: #409eff;
  font-size: 24px;
}

.order-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .order-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding-right: 0;
  }

  .order-summary-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    max-width: 100%;
  }

  .order-summary-right {
    width: 100%;
    justify-content: space-between;
  }

  .order-total-compact {
    min-width: auto;
  }

  .order-items-preview {
    max-width: 100%;
  }

  .filters {
    flex-direction: column;
  }

  .filters .el-select,
  .filters .el-input {
    width: 100%;
  }

  .order-actions {
    flex-direction: column;
  }

  .order-actions .el-button {
    width: 100%;
  }
}
</style>
