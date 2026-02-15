import request from './axios'

export function getManagerStats(params) {
  return request({
    url: '/manager/stats',
    method: 'get',
    params
  })
}