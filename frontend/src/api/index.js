const BASE_URL = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'

export const LOGIN_USER_KEY = 'login_user'

const request = async (path, options = {}) => {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  const payload = await response.json().catch(() => null)
  if (!payload || payload.code !== 0) {
    const message = payload?.message || '请求失败'
    throw new Error(message)
  }

  return payload.data
}

export const setLoginUser = (user) => {
  localStorage.setItem(LOGIN_USER_KEY, JSON.stringify(user))
}

export const getLoginUser = () => {
  const raw = localStorage.getItem(LOGIN_USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export const clearLoginUser = () => {
  localStorage.removeItem(LOGIN_USER_KEY)
}

export const registerUser = (payload) => request('/auth/register', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const loginUser = (payload) => request('/auth/login', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const fetchMedicines = ({ keyword = '', category = '' } = {}) => {
  const params = new URLSearchParams()
  if (keyword) params.set('keyword', keyword)
  if (category) params.set('category', category)
  const query = params.toString()
  return request(`/medicines${query ? `?${query}` : ''}`)
}

export const fetchMedicineDetail = (id) => request(`/medicines/${id}`)

export const fetchCart = (userId) => request(`/cart?user_id=${userId}`)

export const addCartItem = (payload) => request('/cart', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const updateCartItem = (id, payload) => request(`/cart/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload)
})

export const removeCartItem = (id) => request(`/cart/${id}`, {
  method: 'DELETE'
})

export const createOrder = (payload) => request('/orders', {
  method: 'POST',
  body: JSON.stringify(payload)
})

export const fetchOrders = (userId) => request(`/orders?user_id=${userId}`)

export const fetchOrderDetail = (id) => request(`/orders/${id}`)

export const removeOrder = (id) => request(`/orders/${id}`, {
  method: 'DELETE'
})

export const updateUser = (id, payload) => request(`/users/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload)
})

export const ollamaChatStream = (prompt, messages = []) => {
  return fetch(`${BASE_URL}/ollama/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt, messages })
  })
}

