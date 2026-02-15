<template>
  <!-- Cart Drawer -->
  <el-drawer
    v-model="visible"
    title="Shopping Cart"
    direction="rtl"
    size="400px"
    @open="handleOpen"
  >
    <!-- Empty Cart -->
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <el-empty description="Your cart is empty">
        <el-button v-if="authStore.userRole === 'customer'" type="primary" @click="visible = false">Continue Shopping</el-button>
        <el-button v-else type="primary" @click="visible = false">Close</el-button>
      </el-empty>
    </div>

    <!-- Cart Items -->
    <div v-else class="cart-content">
      <!-- Group by Store -->
      <div v-for="storeGroup in cartStore.itemsByStore" :key="storeGroup.store_id" class="store-group">
        <div class="store-header">
          <el-icon><Shop /></el-icon>
          <span>Pickup Store: {{ storeGroup.store_name }}</span>
        </div>

        <div class="cart-items">
          <div v-for="item in storeGroup.items" :key="`${item.id}-${item.store_id}`" class="cart-item">
            <img :src="item.image_url" :alt="item.product_name" class="item-image" />
            <div class="item-info">
              <div class="item-name">{{ item.product_name }}</div>
              <div class="item-price">${{ (item.price / 100).toFixed(2) }}</div>
              
              <!-- Stock Status -->
              <div v-if="item.stock === 0" class="stock-warning">
                <el-icon><WarningFilled /></el-icon>
                Out of Stock
              </div>
              <div v-else-if="item.quantity > item.stock" class="stock-warning">
                <el-icon><WarningFilled /></el-icon>
                Only {{ item.stock }} available
              </div>
              <div v-else class="stock-info">
                In Stock: {{ item.stock }}
              </div>

              <div class="item-controls">
                <el-input-number
                  v-model="item.quantity"
                  :min="1"
                  :max="item.stock"
                  size="small"
                  @change="(val) => cartStore.updateQuantity(item.id, item.store_id, val)"
                />
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  circle
                  @click="cartStore.removeFromCart(item.id, item.store_id)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cart Footer -->
      <div class="cart-footer">
        <div class="total">
          <span>Total:</span>
          <span class="total-price">${{ (cartStore.totalPrice / 100).toFixed(2) }}</span>
        </div>
        
        <!-- Checkout Button -->
        <el-button
          type="primary"
          size="large"
          class="checkout-btn"
          @click="handleCheckout"
        >
          <template v-if="!authStore.isAuthenticated">
            Login to Checkout
          </template>
          <template v-else>
            Proceed to Checkout
          </template>
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Shop, Delete, WarningFilled } from '@element-plus/icons-vue'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import axios from '../api/axios'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Refresh cart stock when drawer opens
const handleOpen = async () => {
  await refreshCartStock()
}

// Refresh stock for all items in cart
const refreshCartStock = async () => {
  if (cartStore.items.length === 0) return

  try {
    // Get unique product IDs
    const productIds = [...new Set(cartStore.items.map(item => item.id))]

    // Fetch current stock for all products
    const response = await axios.get('/products')
    const products = response.data

    // Update stock for each cart item
    cartStore.items.forEach(item => {
      const product = products.find(p => p.id === item.id)
      if (product && product.stores_inventory) {
        const storeInventory = product.stores_inventory.find(
          inv => inv.store_id === item.store_id
        )
        if (storeInventory) {
          cartStore.updateItemStock(item.id, item.store_id, storeInventory.stock)
        }
      }
    })
  } catch (error) {
    console.error('Failed to refresh cart stock:', error)
  }
}

// Handle checkout
const handleCheckout = () => {
  // Check if user is logged in
  if (!authStore.isAuthenticated) {
    visible.value = false
    router.push('/login')
    return
  }

  // Check for stock issues
  const outOfStockItems = cartStore.items.filter(item => item.stock === 0)
  const overQuantityItems = cartStore.items.filter(item => item.quantity > item.stock)

  if (outOfStockItems.length > 0) {
    ElMessage.error('Some items in your cart are out of stock. Please remove them to continue.')
    return
  }

  if (overQuantityItems.length > 0) {
    ElMessage.error('Some items exceed available stock. Please adjust quantities.')
    return
  }

  // Navigate to checkout page
  visible.value = false
  router.push('/checkout')
}
</script>

<style scoped>
.empty-cart {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.store-group {
  margin-bottom: 24px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.store-header {
  background-color: #f5f5f5;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
}

.cart-items {
  padding: 12px;
}

.cart-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #e0e0e0;
}

.cart-item:last-child {
  margin-bottom: 0;
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 4px;
  background: #f5f7fa;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.item-price {
  color: #409eff;
  font-weight: 600;
  font-size: 16px;
}

.stock-info {
  font-size: 12px;
  color: #67c23a;
}

.stock-warning {
  font-size: 12px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.cart-footer {
  margin-top: auto;
  padding: 16px 0;
  border-top: 2px solid #e0e0e0;
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 0 4px;
}

.total-price {
  color: #409eff;
  font-size: 24px;
}

.checkout-btn {
  width: 100%;
}
</style>
