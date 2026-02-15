import request from './axios'

export async function login(data) {
  const response = await request({
    url: '/auth/login',
    method: 'post',
    data
  })
  return response.data
}

export async function register(data) {
  const response = await request({
    url: '/auth/register',
    method: 'post',
    data
  })
  return response.data
}

export async function logout() {
  const response = await request({
    url: '/auth/logout',
    method: 'post'
  })
  return response.data
}

export async function getUserInfo() {
  const response = await request({
    url: '/auth/user',
    method: 'get'
  })
  return response.data
}

export async function getProfile() {
  const response = await request({
    url: '/auth/profile',
    method: 'get'
  })
  return response.data
}

export async function updateProfile(data) {
  const response = await request({
    url: '/auth/profile',
    method: 'put',
    data
  })
  return response.data
}
