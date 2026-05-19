import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/home/Home.vue'
import Login from '../views/login/Login.vue'
import Register from '../views/register/Register.vue'
import Cart from '../views/cart/Cart.vue'
import Order from '../views/order/Order.vue'
import User from '../views/user/User.vue'
import Password from '../views/user/Password.vue'
import MedicineList from '../views/medicine/MedicineList.vue'
import MedicineDetail from '../views/medicine/MedicineDetail.vue'
import VoiceChat from '../views/voice/VoiceChat.vue'
import VoiceAgent from '../views/voice/VoiceAgent.vue'
import Checkout from '../views/order/Checkout.vue'

import { getLoginUser } from '../api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/cart',
      name: 'cart',
      component: Cart,
      meta: { requiresAuth: true }
    },
    {
      path: '/order',
      name: 'order',
      component: Order,
      meta: { requiresAuth: true }
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: Checkout,
      meta: { requiresAuth: true }
    },
    {
      path: '/user',
      name: 'user',
      component: User,
      meta: { requiresAuth: true }
    },
    {
      path: '/user/password',
      name: 'user-password',
      component: Password,
      meta: { requiresAuth: true }
    },
    {
      path: '/medicine',
      name: 'medicine-list',
      component: MedicineList
    },
    {
      path: '/medicine/:id',
      name: 'medicine-detail',
      component: MedicineDetail
    },
    {
      path: '/voice-chat',
      name: 'voice-chat',
      component: VoiceChat,
      meta: { requiresAuth: true }
    },
    {
      path: '/voice-agent',
      name: 'voice-agent',
      component: VoiceAgent,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to) => {
  const isLogin = Boolean(getLoginUser())

  if (to.meta.requiresAuth && !isLogin) {
    window.alert('请先登录后再访问该页面')
    return '/login'
  }

  return true
})

export default router
