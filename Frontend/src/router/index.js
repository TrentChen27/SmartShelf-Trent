import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: () => import('../views/HomePage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/ProductDetail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../views/Checkout.vue'),
    meta: { requiresAuth: true }
  },
  // Unified Dashboard for all roles with sub-routes for tabs
  {
    path: '/home',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        redirect: '/home/orders'
      },
      {
        path: 'orders',
        name: 'DashboardOrders',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'orders' }
      },
      {
        path: 'profile',
        name: 'DashboardProfile',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'profile' }
      },
      {
        path: 'customers',
        name: 'DashboardCustomers',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'customers' }
      },
      {
        path: 'employees',
        name: 'DashboardEmployees',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'sales' }
      },
      {
        path: 'inventory',
        name: 'DashboardInventory',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'inventory' }
      },
      {
        path: 'stores',
        name: 'DashboardStores',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'stores' }
      },
      {
        path: 'stats',
        name: 'DashboardStats',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true, tab: 'stats' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const hasToken = localStorage.getItem('token')
  const requiresAuth = Boolean(to.meta.requiresAuth)
  const isAuthRoute = to.path === '/login' || to.path === '/register'

  if (requiresAuth && !hasToken) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (hasToken && isAuthRoute) {
    next('/home')
    return
  }

  next()
})

export default router
