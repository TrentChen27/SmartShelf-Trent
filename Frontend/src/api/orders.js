import request from './axios'

export function createOrder(data) {
  return request({
    url: '/orders',
    method: 'post',
    data
  })
}

export function getOrders(params) {
  return request({
    url: '/orders',
    method: 'get',
    params
  })
}

export function getOrderById(id) {
  return request({
    url: `/orders/${id}`,
    method: 'get'
  })
}

export function cancelOrder(id) {
  return request({
    url: `/orders/${id}/cancel`,
    method: 'put'
  })
}

export function confirmPickup(id, data) {
  return request({
    url: `/orders/${id}/pickup`,
    method: 'post',
    data
  })
}

export function requestModification(id, data) {
  return request({
    url: `/orders/${id}/request-modification`,
    method: 'post',
    data
  })
}

export function updateOrderStatus(id, status) {
  return request({
    url: `/orders/${id}/status`,
    method: 'put',
    data: { pickup_status: status }
  })
}

export function updatePaymentStatus(id, status) {
  return request({
    url: `/orders/${id}/payment`,
    method: 'put',
    data: { payment_status: status }
  })
}

export function processPayment(id, paymentData) {
  return request({
    url: `/orders/${id}/process-payment`,
    method: 'post',
    data: paymentData
  })
}
