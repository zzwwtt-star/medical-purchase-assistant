<template>
  <header class="app-header">
    <div>
      <p class="title">商家管理后台</p>
      <p class="subtitle">掌控订单、库存与药品上架</p>
    </div>
    <div class="user">
      <div class="avatar">{{ initials }}</div>
      <div>
        <p class="name">{{ merchant?.name || '商家管理员' }}</p>
        <button class="logout" @click="onLogout">退出登录</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { clearMerchant, getMerchant } from '../api'

const router = useRouter()
const merchant = getMerchant()

const initials = computed(() => {
  const name = merchant?.name || '商家'
  return name.slice(0, 1)
})

const onLogout = () => {
  clearMerchant()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
}

.title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px;
}

.subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #e0e7ff;
  color: var(--primary);
  font-weight: 700;
  display: grid;
  place-items: center;
}

.name {
  margin: 0 0 6px;
  font-weight: 600;
}

.logout {
  border: none;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  padding: 0;
  font-size: 13px;
}
</style>
