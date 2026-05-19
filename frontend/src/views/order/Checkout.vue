<template>
  <div class="checkout-page">
    <header class="top card">
      <h1>结算中心</h1>
      <button class="ghost" @click="goCart">返回购物车</button>
    </header>

    <section class="card section">
      <h2>收货信息</h2>
      <p v-if="address" class="address">{{ address }}</p>
      <p v-else class="address empty">未填写收货地址，请先到个人中心完善。</p>
      <button class="ghost" @click="goUserCenter">{{ address ? '修改地址' : '填写收货地址' }}</button>
    </section>

    <section class="card section">
      <h2>订单商品</h2>
      <div v-if="selectedItems.length === 0" class="empty-tip">暂无可结算商品，请返回购物车勾选商品。</div>
      <article v-for="item in selectedItems" :key="item.id" class="item-row">
        <div>
          <h3>{{ item.name }}</h3>
          <p>规格：{{ item.spec }}</p>
          <p>单价：￥{{ item.price }} × {{ item.quantity }}</p>
        </div>
        <strong>￥{{ (Number(item.price) * item.quantity).toFixed(2) }}</strong>
      </article>
    </section>

    <section class="card section total-box">
      <p>商品总额：￥{{ goodsTotal.toFixed(2) }}</p>
      <p>配送费：￥{{ shippingFee.toFixed(2) }}</p>
      <h2>应付总额：￥{{ payableTotal.toFixed(2) }}</h2>
      <p class="note">注：本系统为毕业设计演示，支付环节采用模拟流程。</p>
      <button class="primary" :disabled="selectedItems.length === 0 || !address" @click="submitOrder">
        提交订单
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createOrder, fetchCart, getLoginUser } from '../../api'

const router = useRouter()

const user = ref(getLoginUser())
const address = ref(user.value?.address || '')

const cartItems = ref([])

const selectedItems = computed(() => cartItems.value.filter((item) => item.selected))

const goodsTotal = computed(() =>
  selectedItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
)

const shippingFee = computed(() => (selectedItems.value.length > 0 ? 6 : 0))
const payableTotal = computed(() => goodsTotal.value + shippingFee.value)

const goCart = () => router.push('/cart')
const goUserCenter = () => router.push('/user')

const loadCart = async () => {
  if (!user.value?.id) {
    cartItems.value = []
    return
  }

  try {
    const items = await fetchCart(user.value.id)
    cartItems.value = items.map((item) => ({
      id: item.id,
      medicineId: item.medicine_id,
      name: item.medicine.name,
      price: item.medicine.price,
      spec: item.medicine.spec,
      quantity: item.quantity,
      selected: item.selected
    }))
  } catch (error) {
    window.alert(error.message || '加载购物车失败')
  }
}

const submitOrder = async () => {
  if (!user.value?.id) {
    window.alert('请先登录')
    return
  }

  try {
    const result = await createOrder({
      user_id: user.value.id,
      address: address.value
    })
    window.alert(`下单成功\n订单号：${result.order_no}`)
    router.push('/order')
  } catch (error) {
    window.alert(error.message || '下单失败')
  }
}

onMounted(() => {
  loadCart()
})
</script>

<style scoped>
.checkout-page {
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

.section {
  padding: 16px;
  margin-bottom: 12px;
}

.section h2 {
  margin: 0 0 10px;
  color: #324874;
}

.address {
  margin: 0;
  color: #4b5d87;
  line-height: 1.6;
}

.address.empty {
  color: #9aa6c3;
}

.item-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 10px;
  border: 1px solid #edf1ff;
  border-radius: 10px;
  margin-bottom: 8px;
}

.item-row h3 {
  margin: 0 0 6px;
  color: #2f4270;
}

.item-row p {
  margin: 0 0 4px;
  color: #6d7a9b;
  font-size: 14px;
}

.item-row strong {
  color: #2e53df;
}

.total-box p {
  margin: 0 0 8px;
  color: #526089;
}

.total-box h2 {
  margin: 0 0 8px;
  color: #2e53df;
}

.note {
  font-size: 13px;
  color: #7a87a6;
}

.empty-tip {
  color: #7a87a6;
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

.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
