import request from './axios'

export function getProducts(params) {
  return request({
    url: '/products',
    method: 'get',
    params
  })
}

export function getProductCategories() {
  return request({
    url: '/products/categories',
    method: 'get'
  })
}

export function getProductById(id) {
  return request({
    url: `/products/${id}`,
    method: 'get'
  })
}

export function getStoreInventory(storeId, productId) {
  return request({
    url: `/stores/${storeId}/inventory/${productId}`,
    method: 'get'
  })
}

export function getStoreInventoryList(storeId) {
  return request({
    url: `/stores/${storeId}/inventory`,
    method: 'get'
  })
}
