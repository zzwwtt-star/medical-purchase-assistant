import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/login/Login.vue'
import Register from '../views/register/Register.vue'
import Dashboard from '../views/dashboard/Dashboard.vue'
import Orders from '../views/orders/Orders.vue'
import Products from '../views/products/Products.vue'
import ProductDetail from '../views/products/ProductDetail.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { hideLayout: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { hideLayout: true }
  },
  {
    path: '/',
    name: 'dashboard',
    component: Dashboard
  },
  {
    path: '/orders',
    name: 'orders',
    component: Orders
  },
  {
    path: '/products',
    name: 'products',
    component: Products
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: ProductDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (to.path === '/login' || to.path === '/register') {
    return true
  }

  const merchant = localStorage.getItem('merchantUser')
  if (!merchant) {
    window.alert('请先登录商家后台')
    return '/login'
  }

  return true
})

export default router
