<template>
  <div class="home-page">
    <!-- Top Navigation Bar -->
    <header class="header">
        <div class="header-content">
          <!-- Logo/Brand Name -->
          <div class="brand">
            <el-icon :size="28" color="#409EFF"><Shop /></el-icon>
            <h1>SmartShelf</h1>
          </div>

        <!-- Right Side Navigation -->
        <div class="header-actions">
          <!-- Store Selection -->
          <el-select
            v-model="selectedStoreId"
            placeholder="All Stores"
            class="store-selector"
            @change="handleStoreChange"
            clearable
          >
            <el-option
              v-for="store in stores"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>

          <!-- Shopping Cart (Only for customers) -->
          <el-badge
            v-if="!isAuthenticated || authStore.userRole === 'customer'"
            :value="cartStore.totalItems"
            :hidden="cartStore.totalItems === 0"
            class="action-badge"
          >
            <el-button
              class="icon-button cart-button"
              @click="cartDrawerVisible = true"
              circle
              size="large"
            >
              <el-icon :size="20"><ShoppingCart /></el-icon>
            </el-button>
          </el-badge>

          <!-- Profile Menu -->
          <template v-if="isAuthenticated">
            <el-dropdown @command="handleProfileCommand" trigger="click">
              <div class="profile-dropdown-trigger">
                <el-avatar 
                  :size="40"
                  class="user-avatar"
                >
                  {{ userInitial }}
                </el-avatar>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item disabled class="user-info-item">
                    <div class="user-profile-header">
                      <el-avatar :size="50" class="dropdown-avatar">
                        {{ userInitial }}
                      </el-avatar>
                      <div class="user-details">
                        <span class="username">{{ userDisplayName }}</span>
                        <span class="user-email">{{ userEmail }}</span>
                      </div>
                    </div>
                  </el-dropdown-item>
                  <el-dropdown-item divided command="dashboard" :icon="Monitor">
                    Dashboard
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" :icon="SwitchButton" class="logout-item">
                    Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <div v-else class="auth-links">
            <el-button type="text" @click="goToLogin" class="auth-link">Login</el-button>
            <el-button type="primary" plain @click="goToRegister" class="auth-link">
              Register
            </el-button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Hero Section / Introduction -->
      <section class="hero-section">
        <div class="hero-content">
          <h2 class="hero-title">Welcome to SmartShelf</h2>
          <p class="hero-subtitle">
            Order Online, Pick Up In-Store - Your Convenient Shopping Solution
          </p>
          <div class="hero-features">
            <div class="feature-item">
              <el-icon :size="24" color="#409EFF"><ShoppingBag /></el-icon>
              <span>Browse Products</span>
            </div>
            <div class="feature-item">
              <el-icon :size="24" color="#67C23A"><Location /></el-icon>
              <span>Choose Your Store</span>
            </div>
            <div class="feature-item">
              <el-icon :size="24" color="#E6A23C"><Box /></el-icon>
              <span>Pick Up at Your Convenience</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Products Section -->
      <section class="products-section">
        <!-- Section Header -->
        <div class="section-header">
          <h3 class="section-title">Available Products</h3>
          
          <!-- Filter and Display Controls -->
          <div class="controls">
            <!-- Category Filter -->
            <el-select
              v-model="selectedCategory"
              placeholder="All Categories"
              class="category-selector"
              @change="handleCategoryChange"
              clearable
            >
              <el-option
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>

            <!-- Sort By Price -->
            <el-select
              v-model="sortByPrice"
              placeholder="Sort by Price"
              class="sort-selector"
              @change="handleSortChange"
              clearable
            >
              <el-option label="Price: Low to High" value="asc" />
              <el-option label="Price: High to Low" value="desc" />
            </el-select>

            <!-- Search -->
            <el-input
              v-model="searchQuery"
              placeholder="Search products..."
              :prefix-icon="Search"
              class="search-input"
              @input="handleSearch"
              clearable
            />
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <!-- Empty State -->
        <div v-else-if="displayProducts.length === 0" class="empty-state">
          <el-empty description="No products available">
            <el-button type="primary" @click="resetFilters">Reset Filters</el-button>
          </el-empty>
        </div>

        <!-- Products Grid -->
        <div v-else class="products-grid">
          <div v-for="product in displayProducts" :key="product.id" class="product-card">
            <!-- Product Image -->
            <div class="product-image-wrapper" @click="goToProductDetail(product.id)">
              <img
                :src="product.image_url || '/placeholder-product.png'"
                :alt="product.product_name"
                class="product-image"
              />
              <!-- Out of Stock Badge -->
              <div v-if="!hasStock(product)" class="out-of-stock-badge">
                Out of Stock
              </div>
            </div>

            <!-- Product Info -->
            <div class="product-info">
              <h4 class="product-name" @click="goToProductDetail(product.id)">
                {{ product.product_name }}
              </h4>
              <p class="product-description">
                {{ truncateText(product.description, 80) }}
              </p>

              <!-- Price and Stock -->
              <div class="product-footer">
                <div class="price-section">
                  <span class="product-price">${{ (product.price / 100).toFixed(2) }}</span>
                </div>

                <!-- Stock Info for Selected Store -->
                <div v-if="selectedStoreId && product.stores_inventory" class="stock-info">
                  <template v-for="inv in product.stores_inventory" :key="inv.store_id">
                    <span v-if="inv.store_id === selectedStoreId" class="stock-text">
                      <el-icon><Box /></el-icon>
                      Stock: {{ inv.stock }}
                    </span>
                  </template>
                </div>
                <div v-else-if="product.stores_inventory" class="stock-info">
                  <span class="stock-text">
                    <el-icon><Shop /></el-icon>
                    Available in {{ getAvailableStoresCount(product) }} store(s)
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="product-actions">
                <el-button
                  type="primary"
                  :icon="View"
                  @click="goToProductDetail(product.id)"
                  class="view-detail-btn"
                >
                  View Details
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="!loading && totalProducts > 0" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalProducts"
            :page-sizes="[10, 15, 20, 30, 50]"
            layout="total, prev, pager, next, sizes, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </section>
    </main>

    <!-- Cart Drawer (Only for customers) -->
    <CartDrawer
      v-if="!isAuthenticated || authStore.userRole === 'customer'"
      v-model="cartDrawerVisible"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Shop,
  ShoppingCart,
  Monitor,
  SwitchButton,
  Search,
  View,
  ShoppingBag,
  Location,
  Box
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import CartDrawer from '../components/CartDrawer.vue'
import { getProducts } from '../api/products'
import { getStores } from '../api/stores'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const { isAuthenticated, user } = storeToRefs(authStore)

const userInitial = computed(() => {
  const source = user.value?.name || user.value?.email || ''
  return source ? source.charAt(0).toUpperCase() : 'U'
})
const userDisplayName = computed(() => user.value?.name || user.value?.email || 'User')
const userEmail = computed(() => user.value?.email || '')

const stores = ref([])
const allProducts = ref([]) // Store all fetched products for client-side filtering
const selectedStoreId = ref(null)
const loading = ref(false)
const cartDrawerVisible = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = ref(15)
const totalProducts = ref(0)

// Search and Filters
const searchQuery = ref('')
const selectedCategory = ref(null)
const sortByPrice = ref(null)
const categories = ref([])

// Computed
const displayProducts = computed(() => {
  let filtered = [...allProducts.value]

  // Filter out products with no stock
  filtered = filtered.filter(product => hasStock(product))

  // Apply category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(p => p.kind === selectedCategory.value)
  }

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(p => 
      p.product_name?.toLowerCase().includes(query) ||
      p.description?.toLowerCase().includes(query)
    )
  }

  // Apply price sorting
  if (sortByPrice.value) {
    filtered.sort((a, b) => {
      return sortByPrice.value === 'asc' 
        ? a.price - b.price 
        : b.price - a.price
    })
  }

  // Update total count
  totalProducts.value = filtered.length

  // Apply pagination
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  
  return filtered.slice(start, end)
})

// Methods
const fetchStores = async () => {
  try {
    const response = await getStores()
    stores.value = response.data || []
  } catch (error) {
    ElMessage.error('Failed to load stores')
  }
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {}

    // Only send store_id to backend
    if (selectedStoreId.value) {
      params.store_id = selectedStoreId.value
    }

    const response = await getProducts(params)
    allProducts.value = response.data || []

    // Extract unique categories from fetched products
    const categorySet = new Set()
    allProducts.value.forEach(product => {
      if (product.kind) {
        categorySet.add(product.kind)
      }
    })
    categories.value = Array.from(categorySet).sort()

  } catch (error) {
    ElMessage.error('Failed to load products')
    allProducts.value = []
  } finally {
    loading.value = false
  }
}

const handleStoreChange = () => {
  currentPage.value = 1
  fetchProducts()
}

const handleCategoryChange = () => {
  currentPage.value = 1
}

const handleSortChange = () => {
  currentPage.value = 1
}

const handlePageChange = (page) => {
  currentPage.value = page
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

// Debounced search
let searchTimeout = null
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300) // 300ms delay
}

const resetFilters = () => {
  selectedStoreId.value = null
  selectedCategory.value = null
  sortByPrice.value = null
  searchQuery.value = ''
  currentPage.value = 1
  fetchProducts()
}

const hasStock = (product) => {
  if (!product.stores_inventory || product.stores_inventory.length === 0) {
    return false
  }

  if (selectedStoreId.value) {
    const storeInv = product.stores_inventory.find(
      inv => inv.store_id === selectedStoreId.value
    )
    return storeInv && storeInv.stock > 0
  }

  return product.stores_inventory.some(inv => inv.stock > 0)
}

const getAvailableStoresCount = (product) => {
  if (!product.stores_inventory) return 0
  return product.stores_inventory.filter(inv => inv.stock > 0).length
}

const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

const handleProfileCommand = (command) => {
  switch (command) {
    case 'dashboard':
      router.push('/home')
      break
    case 'logout':
      authStore.clearAuth()
      cartStore.clearCart()
      ElMessage.success('Logged out successfully')
      router.push('/login')
      break
  }
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Lifecycle
onMounted(() => {
  fetchStores()
  fetchProducts()

  // Check if we should open cart drawer (from checkout back navigation)
  const shouldOpenCart = localStorage.getItem('openCartDrawer')
  if (shouldOpenCart === 'true') {
    cartDrawerVisible.value = true
    localStorage.removeItem('openCartDrawer')
  }
})

</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Header Styles */
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.brand h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auth-link {
  font-weight: 500;
}

.store-selector {
  width: 200px;
}

.action-badge {
  display: flex;
  align-items: center;
}

.icon-button {
  border: 2px solid #e4e7ed;
  background: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.icon-button:hover {
  border-color: #409EFF;
  background: #ecf5ff;
  transform: scale(1.05);
}

.cart-button {
  position: relative;
}

.profile-button {
  position: relative;
}

.profile-dropdown-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.user-info-item {
  padding: 0 !important;
}

.user-profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
}

.dropdown-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.user-email {
  font-size: 12px;
  color: #909399;
}

.logout-item {
  color: #f56c6c;
}

.logout-item:hover {
  background-color: #fef0f0;
}

.user-info {
  font-weight: 600;
  color: #409EFF;
}

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 48px 32px;
  margin-bottom: 32px;
  color: white;
  text-align: center;
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.hero-subtitle {
  font-size: 18px;
  margin: 0 0 32px 0;
  opacity: 0.9;
}

.hero-features {
  display: flex;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-item span {
  font-size: 14px;
  font-weight: 500;
}

/* Products Section */
.products-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 16px 0;
}

.controls {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.category-selector {
  width: 180px;
}

.sort-selector {
  width: 180px;
}

.search-input {
  width: 280px;
  flex-shrink: 0;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

/* Loading and Empty States */
.loading-container,
.empty-state {
  padding: 48px 0;
  text-align: center;
}

/* Products Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.product-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.product-image-wrapper {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 75%; /* 4:3 aspect ratio */
  overflow: hidden;
  cursor: pointer;
  background: #f5f7fa;
}

.product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s;
}

.product-image-wrapper:hover .product-image {
  transform: scale(1.05);
}

.out-of-stock-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.product-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  cursor: pointer;
  transition: color 0.2s;
}

.product-name:hover {
  color: #409EFF;
}

.product-description {
  font-size: 14px;
  color: #909399;
  margin: 0 0 12px 0;
  line-height: 1.5;
  flex: 1;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.product-price {
  font-size: 22px;
  font-weight: 700;
  color: #409EFF;
}

.stock-info {
  font-size: 12px;
  color: #67C23A;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stock-text {
  display: flex;
  align-items: center;
  gap: 4px;
}

.product-actions {
  display: flex;
  gap: 8px;
}

.view-detail-btn {
  width: 100%;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    padding: 12px 16px;
  }

  .brand h1 {
    font-size: 20px;
  }

  .header-actions {
    gap: 8px;
  }

  .store-selector {
    width: 140px;
  }

  .icon-button {
    width: 40px;
    height: 40px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-features {
    gap: 24px;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }

  .controls {
    flex-direction: column;
    align-items: stretch;
  }

  .category-selector,
  .sort-selector,
  .search-input {
    width: 100%;
  }
}
</style>
