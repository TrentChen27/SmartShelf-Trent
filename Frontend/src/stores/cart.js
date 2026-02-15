import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const CART_STORAGE_KEY = 'smartshelf_cart'

export const useCartStore = defineStore('cart', () => {
  // Load cart from localStorage
  const loadCartFromStorage = () => {
    try {
      const stored = localStorage.getItem(CART_STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch (error) {
      console.error('Failed to load cart from storage:', error)
      return []
    }
  }

  const items = ref(loadCartFromStorage())

  // Watch items and save to localStorage
  watch(items, (newItems) => {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(newItems))
    } catch (error) {
      console.error('Failed to save cart to storage:', error)
    }
  }, { deep: true })

  const totalItems = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  // Group items by store
  const itemsByStore = computed(() => {
    const grouped = {}
    items.value.forEach(item => {
      if (!grouped[item.store_id]) {
        grouped[item.store_id] = {
          store_id: item.store_id,
          store_name: item.store_name,
          items: []
        }
      }
      grouped[item.store_id].items.push(item)
    })
    return Object.values(grouped)
  })

  function addToCart(product, store, quantity = 1) {
    // Find existing item with same product AND store
    const existingItem = items.value.find(
      item => item.id === product.id && item.store_id === store.id
    )

    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({
        id: product.id,
        product_name: product.product_name,
        price: product.price,
        image_url: product.image_url,
        quantity: quantity,
        store_id: store.id,
        store_name: store.name,
        stock: product.stock || null // Store current stock for validation
      })
    }
  }

  function removeFromCart(productId, storeId) {
    const index = items.value.findIndex(
      item => item.id === productId && item.store_id === storeId
    )
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  function updateQuantity(productId, storeId, quantity) {
    const item = items.value.find(
      item => item.id === productId && item.store_id === storeId
    )
    if (item) {
      if (quantity <= 0) {
        removeFromCart(productId, storeId)
      } else {
        item.quantity = quantity
      }
    }
  }

  function clearCart() {
    items.value = []
    try {
      localStorage.removeItem(CART_STORAGE_KEY)
    } catch (error) {
      console.error('Failed to clear cart from storage:', error)
    }
  }

  // Update stock information for cart items
  function updateItemStock(productId, storeId, stock) {
    const item = items.value.find(
      item => item.id === productId && item.store_id === storeId
    )
    if (item) {
      item.stock = stock
    }
  }

  return {
    items,
    itemsByStore,
    totalItems,
    totalPrice,
    addToCart,
    removeFromCart,
    updateQuantity,
    updateItemStock,
    clearCart
  }
})
