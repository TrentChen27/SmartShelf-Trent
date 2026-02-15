import axios from './axios'

// Get user profile
export const getProfile = async () => {
  const response = await axios.get('/auth/profile')
  return response.data
}

// Update user profile
export const updateProfile = async (data) => {
  const response = await axios.put('/auth/profile', data)
  return response.data
}
