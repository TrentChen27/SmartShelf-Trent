<template>
  <div class="checkout-container">
    <el-card class="checkout-card">
      <template #header>
        <div class="checkout-header">
          <el-icon><ShoppingCart /></el-icon>
          <h2>Checkout</h2>
        </div>
      </template>

      <!-- Empty Cart State -->
      <div v-if="cartStore.items.length === 0" class="empty-state">
        <el-empty description="Your cart is empty">
          <el-button v-if="authStore.userRole === 'customer'" type="primary" @click="router.push('/')">
            Continue Shopping
          </el-button>
          <el-button v-else type="primary" @click="router.push('/home')">
            Back to Dashboard
          </el-button>
        </el-empty>
      </div>

      <!-- Checkout Content -->
      <div v-else class="checkout-content">
        <!-- Order Summary -->
        <div class="order-summary">
          <h3>Order Summary</h3>

          <!-- Group by Store -->
          <div v-for="storeGroup in cartStore.itemsByStore" :key="storeGroup.store_id" class="store-section">
            <div class="store-header">
              <el-icon><Shop /></el-icon>
              <span class="store-name">{{ storeGroup.store_name }}</span>
              <el-tag size="small" type="info">Pickup Location</el-tag>
            </div>

            <!-- Items in this store -->
            <div class="items-list">
              <div v-for="item in storeGroup.items" :key="`${item.id}-${item.store_id}`" class="item-row">
                <img :src="item.image_url" :alt="item.product_name" class="item-image" />
                <div class="item-details">
                  <div class="item-name">{{ item.product_name }}</div>
                  <div class="item-meta">
                    <span>Qty: {{ item.quantity }}</span>
                    <span class="separator">×</span>
                    <span>${{ formatPrice(item.price) }}</span>
                  </div>
                </div>
                <div class="item-subtotal">
                  ${{ formatPrice(item.price * item.quantity) }}
                </div>
              </div>
            </div>

            <!-- Store Subtotal -->
            <div class="store-subtotal">
              <span>Store Subtotal:</span>
              <span class="amount">${{ formatPrice(calculateStoreTotal(storeGroup)) }}</span>
            </div>
          </div>

          <!-- Grand Total -->
          <el-divider />
          <div class="grand-total">
            <span>Total Amount:</span>
            <span class="total-amount">${{ formatPrice(cartStore.totalPrice) }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <el-button v-if="authStore.userRole === 'customer'" size="large" @click="router.push('/')">
            <el-icon><ArrowLeft /></el-icon>
            Continue Shopping
          </el-button>
          <el-button size="large" @click="handleBackToCart">
            <el-icon><ShoppingCart /></el-icon>
            Back to Cart
          </el-button>
          <el-button
            type="primary"
            size="large"
            @click="handlePlaceOrder"
            :loading="processing"
          >
            <el-icon><CreditCard /></el-icon>
            Place Orders & Pay
          </el-button>
        </div>

        <!-- Important Notes -->
        <el-alert
          type="info"
          :closable="false"
          show-icon
          class="checkout-note"
        >
          <template #title>Important Notes</template>
          <ul>
            <li>Separate orders will be created for each store</li>
            <li>You will need to pick up items from their respective stores</li>
            <li>Payment is required to complete the order</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- Batch Payment Dialog -->
    <BatchOrderPayment
      v-model="showPaymentDialog"
      :orders="pendingOrders"
      @success="handlePaymentSuccess"
      @cancel="handlePaymentCancel"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ShoppingCart, Shop, ArrowLeft, CreditCard } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { createOrder } from '../api/orders'
import BatchOrderPayment from '../components/payment/BatchOrderPayment.vue'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const processing = ref(false)
const showPaymentDialog = ref(false)
const pendingOrders = ref([])

// Format price
function formatPrice(cents) {
  return (cents / 100).toFixed(2)
}

// Calculate store total
function calculateStoreTotal(storeGroup) {
  return storeGroup.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
}

// Handle back to cart
function handleBackToCart() {
  // Set a flag in localStorage to open cart drawer on HomePage
  localStorage.setItem('openCartDrawer', 'true')
  router.push('/')
}

// Handle place order
async function handlePlaceOrder() {
  if (!authStore.isAuthenticated) {
    ElMessage.error('Please login to place order')
    router.push('/login')
    return
  }

  // Verify role is customer
  if (authStore.userRole !== 'customer') {
    ElMessage.error('Only customers can place orders')
    return
  }

  processing.value = true

  try {
    // Save cart items by store before creating orders
    const cartItemsByStore = cartStore.itemsByStore.map(storeGroup => ({
      store_id: storeGroup.store_id,
      items: [...storeGroup.items]
    }))

    // Create orders for each store
    const orderPromises = cartItemsByStore.map(storeGroup => {
      const orderData = {
        store_id: storeGroup.store_id,
        items: storeGroup.items.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          price: item.price
        }))
      }
      return createOrder(orderData)
    })

    // Wait for all orders to be created
    const results = await Promise.all(orderPromises)
    const createdOrders = results.map(res => res.data)

    ElMessage.success(`${createdOrders.length} order(s) created successfully!`)

    // Remove ordered items from cart immediately after order creation
    cartItemsByStore.forEach(storeGroup => {
      storeGroup.items.forEach(item => {
        cartStore.removeFromCart(item.id, item.store_id)
      })
    })

    // Store orders for payment processing
    pendingOrders.value = createdOrders

    // Open batch payment dialog
    processing.value = false
    showPaymentDialog.value = true

  } catch (error) {
    console.error('Failed to create orders:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to create orders')
    processing.value = false
  }
}

// Handle payment success
function handlePaymentSuccess() {
  completeCheckout()
}

// Handle payment cancel
function handlePaymentCancel() {
  ElMessage.warning('Payment cancelled. You can complete payment from the Orders page.')
  router.push('/home')
}

// Complete checkout
function completeCheckout() {
  ElMessage.success('All orders placed and paid successfully!')

  // Cart already cleared after order creation
  // Navigate to orders page
  setTimeout(() => {
    router.push('/home')
  }, 1000)
}
</script>

<style scoped>
.checkout-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

.checkout-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.checkout-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.checkout-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.checkout-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-summary h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.store-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.store-header {
  background-color: #f5f7fa;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.store-name {
  flex: 1;
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.items-list {
  padding: 16px;
  background: white;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fafafa;
}

.item-row:last-child {
  margin-bottom: 0;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  background: #f5f7fa;
}

.item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 500;
  color: #333;
  font-size: 15px;
}

.item-meta {
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.separator {
  color: #999;
}

.item-subtotal {
  font-weight: 600;
  color: #409eff;
  font-size: 16px;
}

.store-subtotal {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  border-top: 1px solid #e0e0e0;
  font-weight: 500;
}

.store-subtotal .amount {
  color: #409eff;
  font-weight: 600;
}

.grand-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  padding: 8px 0;
}

.total-amount {
  color: #409eff;
  font-size: 28px;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-buttons .el-button {
  width: 100%;
}

.checkout-note {
  margin-top: 8px;
}

.checkout-note ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.checkout-note li {
  margin: 4px 0;
}

@media (max-width: 768px) {
  .checkout-container {
    margin: 20px auto;
    padding: 0 12px;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .checkout-header h2 {
    font-size: 20px;
  }

  .item-row {
    flex-wrap: wrap;
  }

  .item-subtotal {
    width: 100%;
    text-align: right;
    margin-top: 8px;
  }
}
</style>
