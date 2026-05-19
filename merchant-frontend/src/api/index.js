const BASE_URL = 'http://localhost:5000/api'

export const getMerchant = () => {
  const raw = localStorage.getItem('merchantUser')
  return raw ? JSON.parse(raw) : null
}

export const setMerchant = (data) => {
  localStorage.setItem('merchantUser', JSON.stringify(data))
}

export const clearMerchant = () => {
  localStorage.removeItem('merchantUser')
}

const request = async (url, options = {}) => {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: '请求失败' }))
    throw new Error(error.message || '请求失败')
  }

  const payload = await response.json()
  return payload.data ?? payload
}

export const merchantLogin = (payload) => request('/merchant/login', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const merchantRegister = (payload) => request('/merchant/register', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const fetchMerchantOverview = () => request('/merchant/overview')

export const fetchMerchantOrders = (status) => {
  const query = status ? `?status=${status}` : ''
  return request(`/merchant/orders${query}`)
}

export const updateOrderStatus = (id, status) => request(`/merchant/orders/${id}/status`, {
  method: 'PUT',
  body: JSON.stringify({ status })
})

export const fetchMedicines = () => request('/merchant/medicines')

export const fetchMedicineDetail = (id) => request(`/medicines/${id}`)

export const createMedicine = (payload) => request('/merchant/medicines', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const updateMedicine = (id, payload) => request(`/merchant/medicines/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload)
})

export const deleteMedicine = (id) => request(`/merchant/medicines/${id}`, {
  method: 'DELETE'
})
