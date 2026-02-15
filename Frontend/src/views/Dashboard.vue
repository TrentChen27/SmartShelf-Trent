<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <el-icon :size="32" class="logo-icon"><Shop /></el-icon>
            <span class="logo-text">SmartShelf</span>
          </div>
          <div class="header-actions">
            <el-button v-if="userRole === 'customer'" text @click="$router.push('/')" class="nav-button">
              <el-icon><HomeFilled /></el-icon>
              <span>Continue Shopping</span>
            </el-button>
            <el-dropdown trigger="click">
              <div class="user-menu">
                <el-avatar :size="36" class="user-avatar">
                  {{ authStore.user?.name?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-info">
                  <div class="user-name">{{ authStore.user?.name }}</div>
                  <div class="user-role">{{ roleLabel }}</div>
                </div>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="dashboard-main">
      <div class="container">
        <!-- Welcome Section -->
        <div class="welcome-section">
          <h1 class="welcome-title">Welcome back, {{ authStore.user?.name }}!</h1>
          <p class="welcome-subtitle">Manage your account and view your activity</p>
        </div>

        <!-- Dashboard Content -->
        <div class="dashboard-content">
          <!-- Sidebar Navigation -->
          <aside class="sidebar">
            <nav class="sidebar-nav">
              <div 
                v-for="tab in availableTabs" 
                :key="tab.name"
                :class="['nav-item', { active: activeTab === tab.name }]"
                @click="activeTab = tab.name"
              >
                <el-icon :size="20" class="nav-icon">
                  <component :is="tab.icon" />
                </el-icon>
                <span class="nav-label">{{ tab.label }}</span>
              </div>
            </nav>
          </aside>

          <!-- Content Area -->
          <main class="content-area">
            <div class="content-card">
              <!-- Orders Tab (All roles) -->
              <div v-if="activeTab === 'orders'" class="tab-content">
                <div class="tab-header">
                  <h2 class="tab-title">My Orders</h2>
                  <p class="tab-description">View and manage your order history</p>
                </div>
                <OrderManagement :role="userRole" />
              </div>

              <!-- Profile Tab (All roles) -->
              <div v-if="activeTab === 'profile'" class="tab-content">
                <div class="tab-header">
                  <h2 class="tab-title">Profile Settings</h2>
                  <p class="tab-description">Manage your account information</p>
                </div>
                <ProfileManagement />
              </div>

              <!-- Customer Management (Sales, Manager, Region) -->
              <div v-if="activeTab === 'customers'" class="tab-content">
                <CustomerManagement />
              </div>

              <!-- Sales Management (Manager, Region) -->
              <div v-if="activeTab === 'sales'" class="tab-content">
                <SalesTeamManagement :role="userRole" />
              </div>

              <!-- Inventory Management (Manager, Region) -->
              <div v-if="activeTab === 'inventory'" class="tab-content">
                <InventoryManagement :role="userRole" />
              </div>

              <!-- Store Management (Region Manager only) -->
              <div v-if="activeTab === 'stores'" class="tab-content">
                <StoreManagement />
              </div>

              <div v-if="activeTab === 'stats'" class="tab-content">
                <ManagerStats />
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Shop,
  HomeFilled,
  User,
  ArrowDown,
  SwitchButton,
  ShoppingBag,
  Setting,
  TrendCharts,
  Box,
  UserFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import OrderManagement from '../components/dashboard/OrderManagement.vue'
import ProfileManagement from '../components/dashboard/ProfileManagement.vue'
import CustomerManagement from '../components/dashboard/CustomerManagement.vue'
import SalesTeamManagement from '../components/dashboard/SalesTeamManagement.vue'
import InventoryManagement from '../components/dashboard/InventoryManagement.vue'
import StoreManagement from '../components/dashboard/StoreManagement.vue'
import ManagerStats from '../components/dashboard/ManagerStats.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const activeTab = ref('orders')

// Initialize activeTab from route on mount
onMounted(() => {
  if (route.meta.tab) {
    activeTab.value = route.meta.tab
  }
})

// Watch route changes to update activeTab
watch(
  () => route.meta.tab,
  (newTab) => {
    if (newTab) {
      activeTab.value = newTab
    }
  }
)

// Watch activeTab changes to update route
watch(activeTab, (newTab) => {
  const tabRoutes = {
    orders: '/home/orders',
    profile: '/home/profile',
    stats: '/home/stats',
    customers: '/home/customers',
    sales: '/home/employees',
    inventory: '/home/inventory',
    stores: '/home/stores'
  }

  const newPath = tabRoutes[newTab]
  if (newPath && route.path !== newPath) {
    router.push(newPath)
  }
})

// Get user role
const userRole = computed(() => authStore.userRole || 'customer')

// Role label
const roleLabel = computed(() => {
  const labels = {
    customer: 'Customer',
    sales: 'Sales',
    manager: 'Store Manager',
    region: 'Region Manager'
  }
  return labels[userRole.value] || 'User'
})

// Permission checks
const canManageCustomers = computed(() => {
  return ['sales', 'manager', 'region'].includes(userRole.value)
})

const canManageSales = computed(() => {
  return ['manager', 'region'].includes(userRole.value)
})

const canManageInventory = computed(() => {
  return ['manager', 'region'].includes(userRole.value)
})

const canManageStores = computed(() => {
  return userRole.value === 'region'
})

// Available tabs based on role
const availableTabs = computed(() => {
  const tabs = [
    { name: 'orders', label: 'Orders', icon: ShoppingBag },
    { name: 'profile', label: 'Profile', icon: Setting }
  ]
  // Add a Manager Stats tab for Manager and Region
  if (['manager', 'region'].includes(userRole.value)) {
    tabs.push({ name: 'stats', label: 'Analytics', icon: TrendCharts })
  }
  
  if (canManageCustomers.value) {
    tabs.push({ name: 'customers', label: 'Customers', icon: User })
  }

  if (canManageSales.value) {
    tabs.push({ name: 'sales', label: 'Employees', icon: UserFilled })
  }
  
  if (canManageInventory.value) {
    tabs.push({ name: 'inventory', label: 'Inventory', icon: Box })
  }
  
  if (canManageStores.value) {
    tabs.push({ name: 'stores', label: 'Stores', icon: Shop })
  }
  
  return tabs
})

function handleLogout() {
  authStore.clearAuth()
  cartStore.clearCart()
  ElMessage.success('Logged out successfully')
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e4e7ed;
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
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: translateY(-2px);
}

.logo-icon {
  color: #409eff;
  transition: transform 0.3s ease;
}

.logo:hover .logo-icon {
  transform: rotate(10deg);
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-button {
  font-size: 15px;
  font-weight: 500;
  color: #606266;
  transition: all 0.3s ease;
}

.nav-button:hover {
  color: #409eff;
  background: #ecf5ff;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-menu:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: white;
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
}

.dropdown-icon {
  color: #909399;
  transition: transform 0.3s ease;
}

.user-menu:hover .dropdown-icon {
  transform: translateY(2px);
}

/* Main Content */
.container {
  width: 100%;
  max-width: 3600px;
  margin: 0 auto;
  padding: 0 3rem;
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  .user-info {
    display: none;
  }
  
  .welcome-subtitle {
    display: none;
  }
}

.dashboard-main {
  flex: 1;
  padding: 2rem 0;
}

/* Welcome Section */
.welcome-section {
  margin-bottom: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #409eff;
}

.welcome-title {
  margin: 0 0 0.5rem 0;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  background: linear-gradient(135deg, #303133 0%, #606266 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  margin: 0;
  font-size: 15px;
  color: #909399;
}

/* Dashboard Content */
.dashboard-content {
  display: flex;
  gap: 2rem;
  align-items: start;
}

/* Sidebar */
.sidebar {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: sticky;
  top: 90px;
  width: 280px;
  flex-shrink: 0;
}

.sidebar-nav {
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  color: #606266;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-item.active {
  background: linear-gradient(90deg, #ecf5ff 0%, white 100%);
  color: #409eff;
  border-left-color: #409eff;
  font-weight: 600;
}

.nav-item.active .nav-icon {
  transform: scale(1.1);
}

.nav-icon {
  transition: transform 0.3s ease;
}

.nav-label {
  font-size: 15px;
}

/* Content Area */
.content-area {
  flex: 1;
  min-width: 0;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  min-height: 600px;
}

.tab-content {
  padding: 2rem;
}

.tab-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f5f7fa;
}

.tab-title {
  margin: 0 0 0.5rem 0;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.tab-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.coming-soon {
  padding: 4rem 2rem;
  text-align: center;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-card {
  animation: fadeIn 0.3s ease;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: static;
    display: flex;
    overflow-x: auto;
  }
  
  .sidebar-nav {
    display: flex;
    flex-direction: row;
    width: 100%;
    padding: 0;
  }
  
  .nav-item {
    flex: 1;
    justify-content: center;
    border-left: none !important;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
  }
  
  .nav-item.active {
    background: linear-gradient(180deg, #ecf5ff 0%, white 100%);
    border-bottom-color: #409eff;
    border-left-color: transparent !important;
  }
}
</style>
