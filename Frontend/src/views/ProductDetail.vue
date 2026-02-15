<template>
  <div class="product-detail-page">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <el-icon :size="32"><Shop /></el-icon>
            <span class="logo-text">SmartShelf</span>
          </div>

          <div class="header-actions">
            <!-- Cart -->
            <el-badge :value="cartStore.totalItems" :hidden="cartStore.totalItems === 0" class="cart-badge">
              <el-button @click="cartDrawerVisible = true" type="primary" circle>
                <el-icon :size="20"><ShoppingCart /></el-icon>
              </el-button>
            </el-badge>

            <!-- Login/User -->
            <div v-if="!authStore.isAuthenticated">
              <el-button @click="$router.push('/login')">Login</el-button>
              <el-button type="primary" @click="$router.push('/register')">Register</el-button>
            </div>
            <el-dropdown v-else>
              <el-button>
                <el-icon><User /></el-icon>
                {{ authStore.user?.name }}
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goToDashboard">Dashboard</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">Logout</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </header>

    <!-- Product Detail -->
    <section class="product-detail">
      <div class="container">
        <div v-loading="loading" class="detail-content">
          <el-row :gutter="40" v-if="product">
            <!-- Product Image -->
            <el-col :xs="24" :md="12">
              <div class="product-image-container">
                <img
                  :src="product.image_url || FALLBACK_IMAGE"
                  :alt="product.product_name"
                  @error="handleImageError"
                  class="product-image"
                />
              </div>
            </el-col>

            <!-- Product Info -->
            <el-col :xs="24" :md="12">
              <div class="product-info-container">
                <!-- Back Button -->
                <el-button
                  text
                  @click="$router.back()"
                  class="back-link"
                >
                  <el-icon><ArrowLeft /></el-icon>
                  <span>Back to Products</span>
                </el-button>

                <el-tag v-if="product.kind" type="info" class="category-tag">
                  {{ product.kind }}
                </el-tag>
                
                <h1 class="product-title">{{ product.product_name }}</h1>
                
                <div class="product-price-section">
                  <span class="product-price">${{ (product.price / 100).toFixed(2) }}</span>
                </div>

                <el-divider />

                <div class="product-description-section">
                  <h3>Product Description</h3>
                  <p class="product-description">
                    {{ product.description || 'No description available.' }}
                  </p>
                </div>

                <el-divider />

                <!-- Store Selection & Stock -->
                <div class="store-stock-section">
                  <h3>Pickup Store</h3>

                  <!-- No store selected -->
                  <div v-if="!selectedStoreId">
                    <el-alert
                      title="Please select a store to check availability"
                      type="info"
                      :closable="false"
                      show-icon
                      class="store-alert"
                    />
                    <div v-if="availableStores.length > 0" class="available-stores">
                      <h4>Available at:</h4>
                      <el-space wrap>
                        <el-tag
                          v-for="store in availableStores"
                          :key="store.id"
                          size="large"
                          class="store-tag clickable"
                          @click="selectStore(store.id)"
                        >
                          <el-icon><Location /></el-icon>
                          {{ store.name }} <strong>({{ store.stock }} in stock)</strong>
                        </el-tag>
                      </el-space>
                    </div>
                    <el-empty
                      v-else
                      description="No stores have this product in stock"
                      :image-size="100"
                    />
                  </div>

                  <!-- Store selected -->
                  <div v-else class="selected-store-info">
                    <el-card shadow="hover" class="store-card">
                      <div class="store-card-content">
                        <div class="store-details">
                          <el-icon class="location-icon" :size="24"><Location /></el-icon>
                          <div class="store-text">
                            <div class="store-name">{{ selectedStoreName }}</div>
                            <el-tag
                              v-if="stockQuantity !== null"
                              :type="stockQuantity > 0 ? 'success' : 'danger'"
                              size="small"
                            >
                              {{ stockQuantity > 0 ? `${stockQuantity} in stock` : 'Out of Stock' }}
                            </el-tag>
                          </div>
                        </div>
                        <el-button
                          text
                          type="primary"
                          @click="changeStore"
                          class="change-store-btn"
                        >
                          Change Store
                        </el-button>
                      </div>
                    </el-card>

                    <!-- Show other stores when changing -->
                    <div v-if="showStoreList && availableStores.length > 1" class="other-stores">
                      <h4>Select another store:</h4>
                      <el-space wrap>
                        <el-tag
                          v-for="store in availableStores.filter(s => s.id !== selectedStoreId)"
                          :key="store.id"
                          size="large"
                          class="store-tag clickable"
                          @click="selectStore(store.id)"
                        >
                          <el-icon><Location /></el-icon>
                          {{ store.name }} <strong>({{ store.stock }} in stock)</strong>
                        </el-tag>
                      </el-space>
                    </div>
                  </div>
                </div>

                <el-divider />

                <!-- Quantity & Add to Cart (Only for customers) -->
                <div v-if="!authStore.isAuthenticated || authStore.userRole === 'customer'" class="purchase-section">
                  <div class="quantity-selector">
                    <label>Quantity:</label>
                    <el-input-number
                      v-model="quantity"
                      :min="1"
                      :max="stockQuantity || 1"
                      :disabled="!selectedStoreId || stockQuantity === 0"
                    />
                  </div>

                  <el-button
                    type="primary"
                    size="large"
                    :icon="ShoppingCart"
                    :disabled="!selectedStoreId || stockQuantity === 0"
                    @click="handleAddToCart"
                    class="add-to-cart-btn"
                  >
                    Add to Cart
                  </el-button>
                </div>

                <!-- Non-customer message -->
                <el-alert
                  v-else
                  title="Shopping Cart Not Available"
                  type="info"
                  :closable="false"
                  show-icon
                  style="margin-top: 16px"
                >
                  Shopping cart is only available for customer accounts.
                </el-alert>

                <!-- Additional Info -->
                <div class="additional-info">
                  <el-alert
                    title="Online Order, In-Store Pickup"
                    description="Select your preferred store and pick up your items when convenient."
                    type="success"
                    :closable="false"
                  />
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </section>

    <!-- Cart Drawer (Only for customers) -->
    <CartDrawer
      v-if="!authStore.isAuthenticated || authStore.userRole === 'customer'"
      v-model="cartDrawerVisible"
    />

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 SmartShelf. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Shop,
  ShoppingCart,
  User,
  ArrowLeft
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { getProductById, getProducts } from '../api/products'
import { getStores } from '../api/stores'
import CartDrawer from '../components/CartDrawer.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

// Data
const loading = ref(false)
const product = ref(null)
const stores = ref([])
const selectedStoreId = ref(null)
const stockQuantity = ref(null)
const quantity = ref(1)
const cartDrawerVisible = ref(false)
const showStoreList = ref(false)

// Placeholder image
const FALLBACK_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="20" fill="%23999"%3ENo Image%3C/text%3E%3C/svg%3E'

// Computed
const selectedStoreName = computed(() => {
  const store = stores.value.find(s => s.id === selectedStoreId.value)
  return store?.name || ''
})

const availableStores = computed(() => {
  if (!product.value || !product.value.stores_inventory) {
    return []
  }

  // Handle both object and array formats
  let inventoryData = product.value.stores_inventory
  
  // If it's an object, convert to array
  if (!Array.isArray(inventoryData)) {
    inventoryData = Object.entries(inventoryData).map(([storeId, inv]) => ({
      store_id: parseInt(storeId),
      stock: inv.stock
    }))
  }

  return stores.value
    .map(store => {
      const inventory = inventoryData.find(inv => inv.store_id === store.id)
      if (inventory && inventory.stock > 0) {
        return {
          ...store,
          stock: inventory.stock
        }
      }
      return null
    })
    .filter(store => store !== null)
})

// Methods
async function loadProduct() {
  loading.value = true
  try {
    const productId = route.params.id
    const response = await getProductById(productId)
    product.value = response.data
    
    console.log('Product loaded:', product.value)
    console.log('Stores inventory:', product.value.stores_inventory)
    
    // Update stock quantity if a store is selected
    if (selectedStoreId.value) {
      updateStockQuantity()
    }
  } catch (error) {
    console.error('Failed to load product:', error)
    product.value = null
  } finally {
    loading.value = false
  }
}

async function loadStores() {
  try {
    const response = await getStores()
    stores.value = response.data
    console.log('Stores loaded:', stores.value)
  } catch (error) {
    console.error('Failed to load stores:', error)
    stores.value = []
  }
}

async function loadStoreStock() {
  updateStockQuantity()
}

function updateStockQuantity() {
  if (!selectedStoreId.value || !product.value || !product.value.stores_inventory) {
    stockQuantity.value = null
    return
  }

  // Handle both object and array formats
  let inventoryData = product.value.stores_inventory
  
  // If it's an object, get the specific store's inventory
  if (!Array.isArray(inventoryData)) {
    const inventory = inventoryData[selectedStoreId.value]
    stockQuantity.value = inventory ? inventory.stock : 0
  } else {
    // If it's an array, find the matching store
    const inventory = inventoryData.find(inv => inv.store_id === selectedStoreId.value)
    stockQuantity.value = inventory ? inventory.stock : 0
  }
}

function selectStore(storeId) {
  selectedStoreId.value = storeId
  showStoreList.value = false
  updateStockQuantity()
}

function changeStore() {
  showStoreList.value = !showStoreList.value
}

function handleAddToCart() {
  if (!selectedStoreId.value) {
    ElMessage.warning('Please select a pickup store')
    return
  }

  if (stockQuantity.value === 0) {
    ElMessage.warning('This product is out of stock at the selected store')
    return
  }

  if (quantity.value > stockQuantity.value) {
    ElMessage.warning(`Only ${stockQuantity.value} items available`)
    return
  }

  // Get store info
  const store = stores.value.find(s => s.id === selectedStoreId.value)
  if (!store) {
    ElMessage.error('Store information not found')
    return
  }

  // Add stock information to product
  const productWithStock = {
    ...product.value,
    stock: stockQuantity.value
  }

  cartStore.addToCart(productWithStock, store, quantity.value)
  ElMessage.success(`Added ${quantity.value} item(s) to cart from ${store.name}`)
  quantity.value = 1
}

function handleImageError(e) {
  e.target.src = FALLBACK_IMAGE
}

// Refresh cart items stock when cart is opened
function goToDashboard() {
  router.push('/home')
}

function handleLogout() {
  authStore.clearAuth()
  cartStore.clearCart()
  ElMessage.success('Logged out successfully')
}

// Lifecycle
onMounted(async () => {
  await loadProduct()
  await loadStores()
})
</script>

<style scoped>
.product-detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* Header */
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.store-selector {
  width: 200px;
}

.cart-badge {
  margin-right: 0.5rem;
}

/* Product Detail */
.product-detail {
  flex: 1;
  padding: 2rem 0;
}

.detail-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-image-container {
  width: 100%;
  height: 0;
  padding-bottom: 100%; /* 1:1 aspect ratio */
  position: relative;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-info-container {
  padding: 1rem 0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  color: #409eff;
  transition: all 0.3s;
}

.back-link:hover {
  color: #66b1ff;
  transform: translateX(-4px);
}

.category-tag {
  margin-bottom: 1rem;
}

.product-title {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #333;
}

.product-price-section {
  margin-bottom: 1rem;
}

.product-price {
  font-size: 2.5rem;
  font-weight: bold;
  color: #409eff;
}

.product-description-section h3,
.store-stock-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #333;
}

.product-description {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
}

.store-alert {
  margin-bottom: 1rem;
}

/* Selected store card */
.selected-store-info {
  margin-top: 1rem;
}

.store-card {
  margin-bottom: 1rem;
}

.store-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.store-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.location-icon {
  color: #409eff;
}

.store-text {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.store-text .store-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.change-store-btn {
  font-size: 0.9rem;
}

/* Available stores list */
.available-stores,
.other-stores {
  margin-top: 1rem;
  padding: 1rem;
  background: #f5f7fa;
  border-radius: 8px;
}

.available-stores h4,
.other-stores h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  color: #666;
}

.store-tag {
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
}

.store-tag.clickable {
  cursor: pointer;
  user-select: none;
}

.store-tag.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.purchase-section {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.quantity-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quantity-selector label {
  font-weight: 500;
  color: #333;
}

.add-to-cart-btn {
  flex: 1;
}

.additional-info {
  margin-top: 2rem;
}

/* Footer */
.footer {
  background: #333;
  color: white;
  padding: 2rem 0;
  text-align: center;
  margin-top: auto;
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .product-image-container {
    padding-bottom: 75%; /* Slightly shorter on mobile */
  }

  .product-title {
    font-size: 1.5rem;
  }

  .product-price {
    font-size: 2rem;
  }

  .purchase-section {
    flex-direction: column;
    align-items: stretch;
  }

  .add-to-cart-btn {
    width: 100%;
  }
}
</style>
