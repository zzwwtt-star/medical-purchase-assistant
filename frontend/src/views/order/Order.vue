<template>
  <div class="order-page">
    <header class="top card">
      <h1>我的订单</h1>
      <button class="ghost" @click="goHome">返回首页</button>
    </header>

    <section class="card list" v-if="orders.length > 0">
      <article v-for="order in orders" :key="order.orderNo" class="order-item">
        <div class="head">
          <p>订单号：{{ order.orderNo }}</p>
          <span class="status" :class="`status-${order.statusKey}`">{{ order.status }}</span>
        </div>
        <p class="time">下单时间：{{ order.createdAt }}</p>
        <p class="address">收货地址：{{ order.address }}</p>
        <ul>
          <li v-for="item in order.items" :key="`${order.orderNo}-${item.id}`">
            {{ item.name }} × {{ item.quantity }}（￥{{ (Number(item.price) * item.quantity).toFixed(2) }}）
          </li>
        </ul>
        <div class="order-foot">
          <h3>订单金额：￥{{ order.total }}</h3>
          <button class="remove-icon-btn" title="删除订单" aria-label="删除订单" @click="removeOrderItem(order)"></button>
        </div>
      </article>
    </section>

    <section v-else class="card empty">
      <p>暂无订单，快去选药下单吧。</p>
      <button class="primary" @click="goMedicine">去药品列表</button>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOrderDetail, fetchOrders, getLoginUser, removeOrder } from '../../api'

const router = useRouter()
const orders = ref([])
const user = ref(getLoginUser())

const loadOrders = async () => {
  if (!user.value?.id) {
    orders.value = []
    return
  }

  try {
    const items = await fetchOrders(user.value.id)
    const detailTasks = items.map((item) => fetchOrderDetail(item.id))
    const details = await Promise.all(detailTasks)

    const statusMap = {
      pending: '待发货',
      shipped: '已发货'
    }

    orders.value = details.map((item) => ({
      id: item.id,
      orderNo: item.order_no,
      createdAt: item.created_at,
      address: item.address,
      total: item.total.toFixed(2),
      status: statusMap[item.status] || '待发货',
      statusKey: item.status || 'pending',
      items: item.items.map((detail) => ({
        id: detail.id,
        name: detail.medicine.name,
        quantity: detail.quantity,
        price: detail.price
      }))
    }))
  } catch (error) {
    window.alert(error.message || '加载订单失败')
  }
}

const removeOrderItem = async (order) => {
  if (!order?.id) return
  if (!window.confirm('确认删除该订单吗？')) return

  try {
    await removeOrder(order.id)
    await loadOrders()
  } catch (error) {
    window.alert(error.message || '删除订单失败')
  }
}

const goHome = () => router.push('/')
const goMedicine = () => router.push('/medicine')

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.order-page {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(180deg, #f7f9ff 0%, #edf2ff 100%);
}

.card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(71, 99, 255, 0.08);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
}

.top h1 {
  margin: 0;
  color: #2f4270;
}

.list {
  padding: 14px;
}

.order-item {
  border: 1px solid #edf1ff;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
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
  font-size: 16px;
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

h3 {
  margin: 0;
  color: #2e53df;
}

.remove-icon-btn {
  position: relative;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: #ff5a5f;
  cursor: pointer;
}

.remove-icon-btn::after {
  content: '';
  position: absolute;
  left: 7px;
  right: 7px;
  top: 12px;
  height: 2px;
  border-radius: 2px;
  background: #fff;
}

.empty {
  padding: 24px;
  text-align: center;
}

.empty p {
  color: #6d7a9a;
  margin: 0 0 12px;
}

.ghost,
.primary {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.ghost {
  background: #eef2ff;
  color: #4561cf;
}

.primary {
  background: #3f5dff;
  color: #fff;
}
</style>
