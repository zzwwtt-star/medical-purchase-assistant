<template>
  <div class="login-page">
    <div class="bg-circle bg-circle-1"></div>
    <div class="bg-circle bg-circle-2"></div>

    <div class="login-card">
      <div class="title-wrap">
        <h1>欢迎登录</h1>
        <p>登录后可查看订单、管理购物车与个人信息</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <label class="field-label" for="username">账号</label>
        <input id="username" v-model.trim="form.username" type="text" placeholder="请输入账号" required />

        <label class="field-label" for="password">密码</label>
        <div class="password-wrap">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            required
          />
          <button
            class="eye-btn"
            type="button"
            aria-label="按住查看密码"
            @mousedown="showPassword = true"
            @mouseup="showPassword = false"
            @mouseleave="showPassword = false"
            @touchstart.prevent="showPassword = true"
            @touchend="showPassword = false"
            @touchcancel="showPassword = false"
          >
            <svg v-if="showPassword" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M2.8 4.2a1 1 0 0 1 1.4 0l15.6 15.6a1 1 0 0 1-1.4 1.4l-3.2-3.2a11.7 11.7 0 0 1-3.2.4c-5.6 0-9.6-4.1-11-6.1a1.9 1.9 0 0 1 0-2.4 21 21 0 0 1 5.3-4.9L2.8 5.6a1 1 0 0 1 0-1.4Zm8.2 8.2 2.8 2.8a3 3 0 0 1-2.8-2.8Zm8.7 1.3L17.8 12a6 6 0 0 0-7.9-7.9L8.1 2.3A11.2 11.2 0 0 1 12 1.6c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4 20.8 20.8 0 0 1-3.3 3.6Z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4c-1.4 2-5.4 6.1-11 6.1S2.4 15.5 1 13.5a1.9 1.9 0 0 1 0-2.4C2.4 9.1 6.4 5 12 5Zm0 2c-4.6 0-8 3.2-9.3 5 1.3 1.8 4.7 5 9.3 5s8-3.2 9.3-5c-1.3-1.8-4.7-5-9.3-5Zm0 2.5a2.5 2.5 0 1 1-2.5 2.5A2.5 2.5 0 0 1 12 9.5Z"/>
            </svg>
          </button>
        </div>

        <button class="login-btn" type="submit">登录</button>
      </form>

      <div class="actions">
        <button class="text-btn" type="button" @click="goHome">返回首页</button>
        <button class="text-btn" type="button" @click="showRegisterTip">注册账号</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loginUser, setLoginUser } from '../../api'

const router = useRouter()
const route = useRoute()

const initialUsername = String(route.query.username || '')

const form = reactive({
  username: initialUsername,
  password: ''
})

const showPassword = ref(false)

const handleLogin = async () => {
  if (form.username.length < 3) {
    window.alert('账号长度至少 3 位')
    return
  }

  if (form.password.length < 6) {
    window.alert('密码长度至少 6 位')
    return
  }

  try {
    const user = await loginUser({
      username: form.username,
      password: form.password
    })
    setLoginUser(user)
    window.alert('登录成功')
    router.push('/')
  } catch (error) {
    window.alert(error.message || '登录失败')
  }
}

const goHome = () => router.push('/')
const showRegisterTip = () => router.push('/register')
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(180deg, #f6f9ff 0%, #ecf2ff 100%);
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.bg-circle-1 {
  width: 320px;
  height: 320px;
  top: -80px;
  right: -90px;
  background: radial-gradient(circle, rgba(61, 102, 255, 0.32) 0%, rgba(61, 102, 255, 0) 70%);
}

.bg-circle-2 {
  width: 280px;
  height: 280px;
  left: -80px;
  bottom: -50px;
  background: radial-gradient(circle, rgba(81, 201, 255, 0.28) 0%, rgba(81, 201, 255, 0) 70%);
}

.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 16px 36px rgba(71, 99, 255, 0.15);
  padding: 28px 24px;
}

.title-wrap {
  text-align: center;
  margin-bottom: 18px;
}

.title-wrap h1 {
  margin: 0 0 8px;
  font-size: 30px;
  color: #25345e;
}

.title-wrap p {
  margin: 0;
  font-size: 14px;
  color: #667395;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  margin-top: 4px;
  font-size: 14px;
  color: #3c4d77;
  font-weight: 600;
}

.login-form input {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  border: 1px solid #d6def5;
  background: #fff;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.login-form input:focus {
  border-color: #4c6bff;
  box-shadow: 0 0 0 3px rgba(76, 107, 255, 0.16);
}

.password-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.eye-btn {
  width: 44px;
  height: 44px;
  border: 1px solid #d6def5;
  border-radius: 10px;
  background: #f3f6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #4059d5;
  transition: color 0.2s ease, background-color 0.2s ease, transform 0.12s ease, box-shadow 0.2s ease;
}

.eye-btn:hover {
  color: #2f49cc;
  background: #eaf0ff;
  box-shadow: 0 6px 14px rgba(64, 89, 213, 0.18);
}

.eye-btn:active {
  transform: scale(0.92);
}

.eye-btn svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.login-btn {
  margin-top: 8px;
  height: 46px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #3556ff 0%, #5a75ff 100%);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(53, 86, 255, 0.26);
}

.actions {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
}

.text-btn {
  border: none;
  background: transparent;
  color: #4b66ee;
  cursor: pointer;
  font-size: 14px;
}
</style>
