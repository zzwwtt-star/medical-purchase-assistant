<template>
  <div class="register-page">
    <div class="register-card">
      <div class="brand">
        <span>药</span>
        <div>
          <h2>商家注册</h2>
          <p>创建商家账号以管理订单与药品</p>
        </div>
      </div>
      <form @submit.prevent="onSubmit">
        <label>
          账号
          <input v-model="form.username" placeholder="请输入登录账号" required />
        </label>
        <label>
          密码
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </label>
        <label>
          确认密码
          <input v-model="form.confirm" type="password" placeholder="再次输入密码" required />
        </label>
        <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
      </form>
      <div class="actions">
        <span>已有账号？</span>
        <RouterLink to="/login">返回登录</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { merchantRegister } from '../../api'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  confirm: ''
})

const onSubmit = async () => {
  if (form.password !== form.confirm) {
    window.alert('两次输入密码不一致')
    return
  }

  loading.value = true
  try {
    const payload = {
      username: form.username,
      password: form.password
    }
    await merchantRegister(payload)
    window.alert('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    window.alert(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.register-card {
  width: min(460px, 92vw);
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
</style>
