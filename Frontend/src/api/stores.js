import request from './axios'

export function getStores(params) {
  return request({
    url: '/stores',
    method: 'get',
    params
  })
}

export function getStoreById(id) {
  return request({
    url: `/stores/${id}`,
    method: 'get'
  })
}

export function getStoresByRegion(regionId) {
  return request({
    url: `/regions/${regionId}/stores`,
    method: 'get'
  })
}
