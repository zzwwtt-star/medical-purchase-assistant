<template>
  <div class="orders-page">
    <header class="page-header">
      <div>
        <h2>订单管理</h2>
        <p>跟踪待发货订单并快速更新物流状态</p>
      </div>
      <div class="filters">
        <button :class="{ active: status === 'pending' }" @click="changeStatus('pending')">待发货</button>
        <button :class="{ active: status === 'shipped' }" @click="changeStatus('shipped')">已发货</button>
      </div>
    </header>

    <div class="list">
      <article v-for="order in orders" :key="order.id" class="order-item">
        <div class="head">
          <p>订单号：{{ order.order_no }}</p>
          <span class="status" :class="status === 'pending' ? 'status-pending' : 'status-shipped'">
            {{ status === 'pending' ? '待发货' : '已发货' }}
          </span>
        </div>
        <p class="time">下单时间：{{ order.created_at }}</p>
        <p class="address">收货地址：{{ order.address || '未填写' }}</p>
        <ul>
          <li v-for="item in order.items" :key="item.id">
            {{ item.medicine?.name || '未知药品' }} × {{ item.quantity }}（￥{{ (Number(item.price) * item.quantity).toFixed(2) }}）
          </li>
        </ul>
        <div class="order-foot">
          <h3>订单金额：￥{{ Number(order.total).toFixed(2) }}</h3>
          <button
            v-if="status === 'pending'"
            class="primary"
            @click="markShipped(order.id)"
          >
            确认发货
          </button>
          <span v-else class="shipped">已发货</span>
        </div>
      </article>
      <div v-if="!orders.length" class="empty">暂无订单</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchMerchantOrders, updateOrderStatus } from '../../api'

const status = ref('pending')
const orders = ref([])

const loadOrders = async () => {
  try {
    orders.value = await fetchMerchantOrders(status.value)
  } catch (error) {
    window.alert(error.message || '加载订单失败')
  }
}

const changeStatus = (value) => {
  status.value = value
  loadOrders()
}

const markShipped = async (orderId) => {
  try {
    await updateOrderStatus(orderId, 'shipped')
    loadOrders()
  } catch (error) {
    window.alert(error.message || '更新失败')
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.orders-page {
  display: grid;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.page-header p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.filters {
  display: flex;
  gap: 8px;
}

.filters button {
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: white;
  cursor: pointer;
  font-weight: 600;
}

.filters button.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.list {
  display: grid;
  gap: 16px;
}

.order-item {
  border: 1px solid #edf1ff;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: var(--panel);
  box-shadow: var(--shadow);
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.head p,
.time,
.address {
  margin: 0 0 6px;
  color: #5f6f92;
}

.status {
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  height: fit-content;
}

.status-pending {
  background: #fff4e5;
  color: #f59e0b;
}

.status-shipped {
  background: #e0f2fe;
  color: #0ea5e9;
}

ul {
  margin: 0 0 8px 16px;
  color: #55658c;
}

.order-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.order-foot h3 {
  margin: 0;
  color: #2e53df;
}

.shipped {
  font-weight: 700;
  color: #0ea5e9;
}

.primary {
  padding: 10px 16px;
  border-radius: 12px;
  border: none;
  background: var(--primary);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.status {
  font-weight: 600;
  color: var(--muted);
}

.empty {
  text-align: center;
  color: var(--muted);
  padding: 40px 0;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-main {
    flex-direction: column;
    gap: 12px;
  }

  .order-actions {
    text-align: left;
  }
}
</style>
