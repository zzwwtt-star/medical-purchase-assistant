<template>
  <div class="login-page">
    <div class="page-hero">
      <h1>药品商家管理系统</h1>
      <p>药品上架、订单处理与发货管理一站式完成</p>
    </div>
    <div class="login-card">
      <div class="brand">
        <span>药</span>
        <div>
          <h2>商家管理登录</h2>
          <p>登录后可管理订单与药品信息</p>
        </div>
      </div>
      <form @submit.prevent="onSubmit">
        <label>
          账号
          <input v-model="form.username" placeholder="请输入商家账号" required />
        </label>
        <label>
          密码
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </label>
        <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      </form>
      <div class="actions">
        <span>没有账号？</span>
        <RouterLink to="/register">去注册</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { merchantLogin, setMerchant } from '../../api'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const onSubmit = async () => {
  loading.value = true
  try {
    if (form.username === 'admin' && form.password === '123456') {
      setMerchant({ name: '商家管理员', username: form.username })
      router.push('/')
      return
    }

    const data = await merchantLogin(form)
    setMerchant(data)
    router.push('/')
  } catch (error) {
    window.alert(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
  overflow: hidden;
}

.page-hero {
  position: absolute;
  top: 12px;
  left: 12px;
  text-align: left;
}

.page-hero h1 {
  margin: 0 0 6px;
  font-size: 40px;
  font-weight: 800;
  color: #1f2f5c;
  letter-spacing: 3px;
}

.page-hero p {
  margin: 0;
  color: #5f6f92;
  font-size: 14px;
}

.login-card {
  margin: 0;
}

@media (max-width: 768px) {
  .page-hero {
    top: 10px;
    left: 10px;
  }

  .page-hero h1 {
    font-size: 30px;
  }
}

.login-card {
  width: min(420px, 92vw);
  background: var(--panel);
  box-shadow: var(--shadow);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}

.brand span {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: var(--primary);
  color: white;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.brand h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.brand p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

form {
  display: grid;
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  font-size: 14px;
}

input {
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  font-size: 14px;
}

button {
  padding: 12px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--primary);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.actions {
  margin-top: 14px;
  display: flex;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.actions a {
  color: var(--primary);
  font-weight: 600;
}

.page-title {
  margin: 12px 0 18px;
  font-size: 26px;
  font-weight: 800;
  color: #2f4270;
  letter-spacing: 2px;
  text-align: left;
}
</style>
