<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">药</div>
      <div>
        <h1>商家中心</h1>
        <p>订单与库存管理</p>
      </div>
    </div>
    <nav class="nav">
      <RouterLink to="/" class="nav-item" active-class="active">总览</RouterLink>
      <RouterLink to="/orders" class="nav-item" active-class="active">订单管理</RouterLink>
      <RouterLink to="/products" class="nav-item" active-class="active">药品管理</RouterLink>
    </nav>
    <div class="tips">
      <p>提示</p>
      <span>实时关注待发货订单，保持药品库存充足。</span>
    </div>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #0f172a;
  color: #e2e8f0;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.logo {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: #3b82f6;
  color: white;
  font-weight: 700;
  display: grid;
  place-items: center;
}

.brand h1 {
  margin: 0;
  font-size: 18px;
}

.brand p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-item {
  padding: 12px 16px;
  border-radius: 14px;
  color: #e2e8f0;
  font-weight: 600;
  transition: 0.2s ease;
}

.nav-item:hover {
  background: rgba(148, 163, 184, 0.2);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.25);
  color: #ffffff;
}

.tips {
  margin-top: auto;
  padding: 16px;
  border-radius: 16px;
  background: rgba(148, 163, 184, 0.16);
  font-size: 12px;
  line-height: 1.6;
}

.tips p {
  margin: 0 0 6px;
  font-weight: 600;
}

.tips span {
  color: #cbd5f5;
}

@media (max-width: 960px) {
  .sidebar {
    width: 100%;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .nav {
    flex-direction: row;
    gap: 8px;
  }

  .tips {
    display: none;
  }
}
</style>
