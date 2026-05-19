<template>
  <div class="cart-page">
    <header class="top card">
      <div>
        <h1>购物车</h1>
        <p>已选择 {{ selectedCount }} 件商品</p>
      </div>
      <div class="top-actions">
        <button class="ghost" @click="goMedicine">继续选药</button>
        <button class="ghost" @click="goHome">返回首页</button>
      </div>
    </header>

    <section v-if="cartItems.length > 0" class="list card">
      <div class="toolbar">
        <label class="check-wrap">
          <input type="checkbox" :checked="isAllSelected" @change="toggleAll($event.target.checked)" />
          <span>全选</span>
        </label>
        <button class="danger-lite" @click="removeSelected">删除已选</button>
      </div>

      <article v-for="item in cartItems" :key="item.id" class="item-row">
        <label class="check-wrap item-check">
          <input type="checkbox" v-model="item.selected" @change="toggleItem(item)" />
        </label>

        <div class="item-main">
          <h3>{{ item.name }}</h3>
          <p class="spec">规格：{{ item.spec }}</p>
          <p class="price">单价：￥{{ item.price }}</p>
        </div>

        <div class="item-actions">
          <div class="qty-box">
            <button @click="decrease(item)">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="increase(item)">+</button>
          </div>
          <p class="subtotal">小计：￥{{ (Number(item.price) * item.quantity).toFixed(2) }}</p>
          <button class="remove-icon-btn" title="移除该商品" aria-label="移除该商品" @click="removeItem(item.id)"></button>
        </div>
      </article>
    </section>

    <section v-else class="empty card">
      <p>购物车为空，快去添加药品吧。</p>
      <button class="primary" @click="goMedicine">去药品列表</button>
    </section>

    <footer class="bottom card" v-if="cartItems.length > 0">
      <div>
        <p>已选 {{ selectedCount }} 件</p>
        <h2>合计：￥{{ selectedTotal.toFixed(2) }}</h2>
      </div>
      <button class="primary" :disabled="selectedCount === 0" @click="checkout">去结算</button>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCart, getLoginUser, removeCartItem, updateCartItem } from '../../api'

const router = useRouter()

const cartItems = ref([])
const currentUser = ref(getLoginUser())

const loadCart = async () => {
  if (!currentUser.value?.id) {
    cartItems.value = []
    return
  }

  try {
    const items = await fetchCart(currentUser.value.id)
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

const isAllSelected = computed(() =>
  cartItems.value.length > 0 && cartItems.value.every((item) => item.selected)
)

const selectedCount = computed(() =>
  cartItems.value.filter((item) => item.selected).reduce((sum, item) => sum + item.quantity, 0)
)

const selectedTotal = computed(() =>
  cartItems.value
    .filter((item) => item.selected)
    .reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
)

const toggleAll = async (checked) => {
  const tasks = cartItems.value.map((item) => updateCartItem(item.id, { selected: checked }))
  if (!tasks.length) return

  try {
    await Promise.all(tasks)
    await loadCart()
  } catch (error) {
    window.alert(error.message || '更新失败')
  }
}

const increase = async (item) => {
  try {
    await updateCartItem(item.id, { quantity: item.quantity + 1 })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '更新失败')
  }
}

const decrease = async (item) => {
  if (item.quantity <= 1) return

  try {
    await updateCartItem(item.id, { quantity: item.quantity - 1 })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '更新失败')
  }
}

const removeItem = async (id) => {
  try {
    await removeCartItem(id)
    await loadCart()
  } catch (error) {
    window.alert(error.message || '删除失败')
  }
}

const toggleItem = async (item) => {
  try {
    await updateCartItem(item.id, { selected: item.selected })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '更新失败')
  }
}

const removeSelected = async () => {
  const tasks = cartItems.value.filter((item) => item.selected).map((item) => removeCartItem(item.id))
  if (!tasks.length) return

  try {
    await Promise.all(tasks)
    await loadCart()
  } catch (error) {
    window.alert(error.message || '删除失败')
  }
}

const checkout = () => {
  router.push('/checkout')
}

const goHome = () => router.push('/')
const goMedicine = () => router.push('/medicine')

onMounted(() => {
  loadCart()
})
</script>

<style scoped>
.cart-page {
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

.top-actions {
  display: flex;
  gap: 8px;
}

.top h1 {
  margin: 0 0 6px;
  color: #2e426f;
}

.top p {
  margin: 0;
  color: #6b7896;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid #edf1ff;
}

.list {
  margin-bottom: 12px;
}

.item-row {
  display: grid;
  grid-template-columns: 28px 1fr auto;
  gap: 12px;
  padding: 14px;
  border-bottom: 1px solid #edf1ff;
}

.item-main h3 {
  margin: 0 0 6px;
  color: #2f4270;
}

.spec,
.price {
  margin: 0 0 4px;
  color: #6a7899;
  font-size: 14px;
}

.item-actions {
  min-width: 170px;
}

.qty-box {
  display: inline-flex;
  align-items: center;
  border: 1px solid #dbe2fa;
  border-radius: 10px;
  overflow: hidden;
}

.qty-box button {
  width: 30px;
  height: 32px;
  border: none;
  background: #f1f4ff;
  color: #4764d6;
  cursor: pointer;
}

.qty-box span {
  width: 34px;
  text-align: center;
  color: #334773;
}

.subtotal {
  margin: 8px 0;
  color: #314778;
  font-size: 14px;
}

.remove-icon-btn {
  position: relative;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: #ff5a5f;
  cursor: pointer;
}

.remove-icon-btn::after {
  content: '';
  position: absolute;
  left: 6px;
  right: 6px;
  top: 11px;
  height: 2px;
  border-radius: 2px;
  background: #fff;
}

.bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
}

.bottom p {
  margin: 0 0 4px;
  color: #6d7a9a;
}

.bottom h2 {
  margin: 0;
  color: #2e53df;
  font-size: 24px;
}

.empty {
  padding: 24px;
  text-align: center;
}

.empty p {
  color: #6d7a9a;
  margin: 0 0 12px;
}

.check-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #475883;
}

.ghost,
.primary,
.danger-lite {
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

.danger-lite {
  background: #fff1f2;
  color: #d74a53;
}

@media (max-width: 900px) {
  .item-row {
    grid-template-columns: 1fr;
  }

  .item-check {
    margin-bottom: -6px;
  }

  .item-actions {
    min-width: auto;
  }

  .bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
