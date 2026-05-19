<template>
  <div class="medicine-page">
    <header class="top-bar card">
      <div>
        <h1>药品列表</h1>
        <p>根据常见症状为你推荐药品，可进入详情页进一步查看</p>
      </div>
      <div class="top-actions">
        <button class="back-btn" @click="goCart">返回购物车</button>
        <button class="back-btn" @click="goHome">返回首页</button>
      </div>
    </header>

    <section class="filter card">
      <div class="search-row">
        <input
          v-model.trim="keyword"
          @keyup.enter="applySearch"
          type="text"
          placeholder="搜索药品名称或功效，例如：感冒、止咳、退烧"
        />
        <button class="search-btn" @click="applySearch" aria-label="执行搜索">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M10 3a7 7 0 0 1 5.5 11.3l4.1 4.1a1 1 0 1 1-1.4 1.4l-4.1-4.1A7 7 0 1 1 10 3Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z" />
          </svg>
        </button>
      </div>
      <div class="tags">
        <button
          v-for="tag in tags"
          :key="tag"
          :class="['tag-btn', { active: selectedTag === tag }]"
          @click="handleTagClick(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </section>

    <section class="medicine-grid">
      <article v-for="item in medicineList" :key="item.id" class="medicine-card card">
        <div class="pill-icon" :class="item.colorClass">💊</div>
        <h3>{{ item.name }}</h3>
        <p class="desc">{{ item.desc }}</p>
        <div class="meta">
          <span>规格：{{ item.spec }}</span>
          <span>￥{{ item.price }}</span>
        </div>
        <div class="actions">
          <button class="ghost" @click="viewDetail(item)">查看详情</button>
          <button class="primary" @click="addToCart(item)">加入购物车</button>
        </div>
      </article>
    </section>

    <p v-if="medicineList.length === 0" class="empty">没有匹配的药品，换个关键词试试。</p>

    <button
      class="floating-cart right"
      :class="{ expanded: cartExpanded && !isDragging }"
      :style="{ top: `${cartTop}px` }"
      @mouseenter="cartExpanded = true"
      @mouseleave="cartExpanded = false"
      @mousedown="startDrag"
      @touchstart.prevent="startDrag"
      @click="onCartClick"
      aria-label="打开购物车"
    >
      <span class="cart-icon">🛒</span>
      <span class="cart-badge" v-if="cartCount > 0">{{ cartCount }}</span>
    </button>

    <div v-if="cartDrawerOpen" class="cart-drawer-mask" @click="cartDrawerOpen = false"></div>

    <aside class="cart-drawer" :class="{ open: cartDrawerOpen }">
      <div class="drawer-head">
        <h3>购物车预览</h3>
        <button class="close-btn" @click="cartDrawerOpen = false">关闭</button>
      </div>

      <div v-if="cartItems.length === 0" class="drawer-empty">购物车还是空的，快去选药吧。</div>

      <ul v-else class="drawer-list">
        <li v-for="item in cartItems" :key="item.id" class="drawer-item">
          <div>
            <p class="name">{{ item.name }}</p>
            <p class="meta-line">￥{{ item.price }} · 小计 ￥{{ (item.quantity * Number(item.price)).toFixed(2) }}</p>
          </div>

          <div class="item-actions">
            <div class="qty-controls">
              <button class="qty-btn" @click="decreaseQty(item.id)">-</button>
              <span class="qty-num">{{ item.quantity }}</span>
              <button class="qty-btn" @click="increaseQty(item.id)">+</button>
            </div>

            <button class="remove-icon-btn" @click="removeFromMiniCart(item.id)" aria-label="移除商品"></button>
          </div>
        </li>
      </ul>

      <div class="drawer-foot">
        <p>共 {{ cartCount }} 件 · 合计 <strong>￥{{ cartTotalPrice.toFixed(2) }}</strong></p>
        <div class="foot-actions">
          <button class="ghost" @click="clearMiniCart">清空</button>
          <button class="primary" @click="goCart">去购物车结算</button>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { addCartItem, fetchCart, fetchMedicines, getLoginUser, removeCartItem, updateCartItem } from '../../api'

const router = useRouter()

const CART_TOP_KEY = 'demo_cart_top'

const keyword = ref('')
const searchKeyword = ref('')
const selectedTag = ref('全部')
const cartExpanded = ref(false)
const cartDrawerOpen = ref(false)
const tags = ['全部', '感冒/发热', '咳嗽/呼吸道', '咽喉/口腔', '鼻炎/过敏', '肠胃/消化', '止痛/退热', '皮肤/外用', '消炎/抗菌', '儿科常备', '妇科常备', '维生素/营养', '眼科/滴眼液']

const defaultCartTop = Math.round(window.innerHeight * 0.56)
const savedCartTop = Number(localStorage.getItem(CART_TOP_KEY))
const cartTop = ref(Number.isFinite(savedCartTop) && savedCartTop > 0 ? savedCartTop : defaultCartTop)
const isDragging = ref(false)
const dragMoved = ref(false)
let startPointerY = 0
let startCartTop = 0
let suppressClick = false

const medicineList = ref([])
const cartItems = ref([])
const currentUser = ref(getLoginUser())

const categoryMap = {
  '感冒/发热': '感冒',
  '咳嗽/呼吸道': '咳嗽',
  '咽喉/口腔': '咽喉',
  '鼻炎/过敏': '鼻炎',
  '肠胃/消化': '肠胃',
  '止痛/退热': '止痛',
  '皮肤/外用': '皮肤',
  '消炎/抗菌': '消炎',
  '儿科常备': '儿科',
  '妇科常备': '妇科',
  '维生素/营养': '维生素',
  '眼科/滴眼液': '眼科'
}

const cartCount = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity, 0))
const cartTotalPrice = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity * Number(item.price), 0))

const getColorClass = (seed) => {
  const value = String(seed || '')
  const hash = value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return `c${(hash % 5) + 1}`
}

const loadMedicines = async ({ keyword = '', category = '' } = {}) => {
  try {
    const items = await fetchMedicines({ keyword, category })
    medicineList.value = items.map((item) => ({
      ...item,
      tag: item.category || '全部',
      colorClass: getColorClass(item.id || item.name)
    }))
  } catch (error) {
    window.alert(error.message || '加载药品失败')
  }
}

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

const synonymMap = {
  发烧: '发热',
  退烧: '发热',
  咽喉痛: '咽痛',
  嗓子痛: '咽痛',
  咳痰: '痰多',
  拉肚子: '腹泻',
  肚子疼: '腹痛',
  过敏性鼻炎: '鼻炎',
  鼻涕: '流涕',
  消化不良: '腹胀',
  胃痛: '腹痛'
}

const normalizeKeyword = (value) => {
  const raw = value.trim().toLowerCase()
  if (!raw) return ''

  let normalized = raw
  Object.entries(synonymMap).forEach(([from, to]) => {
    normalized = normalized.replaceAll(from, to)
  })

  return normalized
}

const applySearch = async () => {
  searchKeyword.value = normalizeKeyword(keyword.value)
  const category = selectedTag.value === '全部' ? '' : categoryMap[selectedTag.value] || selectedTag.value
  await loadMedicines({
    keyword: searchKeyword.value,
    category
  })
}

const handleTagClick = async (tag) => {
  selectedTag.value = selectedTag.value === tag ? '全部' : tag
  keyword.value = ''
  searchKeyword.value = ''
  const category = selectedTag.value === '全部' ? '' : categoryMap[selectedTag.value] || selectedTag.value
  await loadMedicines({
    keyword: '',
    category
  })
}

const goCart = () => router.push('/cart')
const goHome = () => router.push('/')

const viewDetail = (item) => {
  router.push(`/medicine/${item.id}`)
}

const addToCart = async (item) => {
  if (!currentUser.value?.id) {
    window.alert('请先登录')
    return
  }

  try {
    await addCartItem({
      user_id: currentUser.value.id,
      medicine_id: item.id,
      quantity: 1
    })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '加入购物车失败')
  }
}

const removeFromMiniCart = async (id) => {
  const target = cartItems.value.find((item) => item.id === id)
  if (!target) return

  try {
    await removeCartItem(target.id)
    await loadCart()
  } catch (error) {
    window.alert(error.message || '移除失败')
  }
}

const increaseQty = async (id) => {
  const target = cartItems.value.find((item) => item.id === id)
  if (!target) return

  try {
    await updateCartItem(target.id, { quantity: target.quantity + 1 })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '修改数量失败')
  }
}

const decreaseQty = async (id) => {
  const target = cartItems.value.find((item) => item.id === id)
  if (!target) return

  const nextQuantity = target.quantity - 1
  if (nextQuantity <= 0) {
    await removeFromMiniCart(id)
    return
  }

  try {
    await updateCartItem(target.id, { quantity: nextQuantity })
    await loadCart()
  } catch (error) {
    window.alert(error.message || '修改数量失败')
  }
}

const clearMiniCart = async () => {
  const tasks = cartItems.value.map((item) => removeCartItem(item.id))
  if (!tasks.length) return

  try {
    await Promise.all(tasks)
    await loadCart()
  } catch (error) {
    window.alert(error.message || '清空失败')
  }
}

const getClientY = (event) => ('touches' in event ? event.touches[0].clientY : event.clientY)

const clampTop = (value) => {
  const min = 32
  const max = window.innerHeight - 32
  return Math.max(min, Math.min(max, value))
}

const onDragMove = (event) => {
  if (!isDragging.value) return
  const currentY = getClientY(event)
  cartTop.value = clampTop(startCartTop + (currentY - startPointerY))
  dragMoved.value = true
}

const endDrag = () => {
  if (!isDragging.value) return

  isDragging.value = false
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchmove', onDragMove)
  window.removeEventListener('touchend', endDrag)

  localStorage.setItem(CART_TOP_KEY, String(Math.round(cartTop.value)))

  if (dragMoved.value) suppressClick = true
}

const startDrag = (event) => {
  isDragging.value = true
  dragMoved.value = false
  cartExpanded.value = false
  startPointerY = getClientY(event)
  startCartTop = cartTop.value

  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('touchmove', onDragMove, { passive: true })
  window.addEventListener('touchend', endDrag)
}

const onCartClick = () => {
  if (suppressClick) {
    suppressClick = false
    return
  }
  cartDrawerOpen.value = !cartDrawerOpen.value
}

onMounted(() => {
  loadMedicines()
  loadCart()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchmove', onDragMove)
  window.removeEventListener('touchend', endDrag)
})
</script>

<style scoped>
.medicine-page {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(180deg, #f7f9ff 0%, #edf2ff 100%);
}

.card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(71, 99, 255, 0.08);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px;
  margin-bottom: 14px;
}

.top-actions {
  display: flex;
  gap: 8px;
}

.top-bar h1 {
  margin: 0 0 8px;
  color: #2f4270;
}

.top-bar p {
  margin: 0;
  color: #6a7692;
}

.back-btn {
  border: none;
  border-radius: 10px;
  background: #eef2ff;
  color: #425ecf;
  padding: 10px 14px;
  cursor: pointer;
}

.filter {
  padding: 16px;
  margin-bottom: 14px;
}

.search-row {
  display: grid;
  grid-template-columns: 1fr 44px;
  gap: 8px;
}

.filter input {
  width: 100%;
  height: 42px;
  border: 1px solid #d6def5;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.search-btn {
  width: 44px;
  height: 42px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #3f5dff 0%, #5f79ff 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(63, 93, 255, 0.24);
}

.search-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.tags {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-btn {
  border: none;
  border-radius: 999px;
  padding: 6px 12px;
  background: #eef2ff;
  color: #526189;
  cursor: pointer;
}

.tag-btn.active {
  background: #3f5dff;
  color: #fff;
}

.medicine-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.medicine-card {
  padding: 16px;
}

.pill-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.c1 { background: #dce6ff; }
.c2 { background: #e9dcff; }
.c3 { background: #d9f6ff; }
.c4 { background: #e2ffe2; }
.c5 { background: #fff0d9; }

.medicine-card h3 {
  margin: 0 0 8px;
  color: #2f4270;
}

.desc {
  margin: 0 0 10px;
  color: #6b7896;
  font-size: 14px;
  line-height: 1.5;
  min-height: 42px;
}

.meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #5f6e90;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 8px;
}

.ghost,
.primary {
  flex: 1;
  border: none;
  border-radius: 9px;
  height: 36px;
  cursor: pointer;
}

.ghost {
  background: #eef2ff;
  color: #425ecf;
}

.primary {
  background: #3f5dff;
  color: #fff;
}

.empty {
  margin-top: 12px;
  text-align: center;
  color: #7b88a8;
}

.floating-cart {
  position: fixed;
  transform: translateY(-50%);
  width: 42px;
  height: 64px;
  border: none;
  background: linear-gradient(135deg, #3f5dff 0%, #5f79ff 100%);
  color: #fff;
  box-shadow: 0 10px 24px rgba(63, 93, 255, 0.36);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  z-index: 30;
  transition: width 0.25s ease, height 0.25s ease, right 0.25s ease, border-radius 0.25s ease;
}

.floating-cart:active {
  cursor: grabbing;
}

.floating-cart.right {
  right: 0;
  border-top-left-radius: 32px;
  border-bottom-left-radius: 32px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.floating-cart .cart-icon {
  font-size: 20px;
  line-height: 1;
}

.floating-cart.expanded {
  width: 64px;
  height: 64px;
  border-radius: 50%;
}

.floating-cart.right.expanded {
  right: 10px;
}

.floating-cart.left.expanded {
  left: 10px;
}

.cart-badge {
  position: absolute;
  top: -6px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 10px;
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 12px rgba(255, 77, 79, 0.35);
}

.floating-cart.right .cart-badge {
  right: -6px;
}

.floating-cart.left .cart-badge {
  left: -6px;
}

.cart-drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(18, 27, 52, 0.25);
  z-index: 40;
}

.cart-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 330px;
  max-width: 86vw;
  height: 100vh;
  background: #fff;
  box-shadow: -12px 0 28px rgba(47, 66, 112, 0.18);
  transform: translateX(100%);
  transition: transform 0.25s ease;
  z-index: 41;
  display: flex;
  flex-direction: column;
}

.cart-drawer.open {
  transform: translateX(0);
}

.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 10px;
  border-bottom: 1px solid #edf1ff;
}

.drawer-head h3 {
  margin: 0;
  color: #2e416f;
}

.close-btn {
  border: none;
  background: #eef2ff;
  color: #4662cf;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
}

.drawer-empty {
  padding: 18px 14px;
  color: #7a87a6;
}

.drawer-list {
  margin: 0;
  padding: 10px 14px;
  list-style: none;
  overflow: auto;
  flex: 1;
}

.drawer-item {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 10px;
  border: 1px solid #edf1ff;
  border-radius: 10px;
  margin-bottom: 8px;
}

.name {
  margin: 0 0 4px;
  color: #334874;
  font-weight: 600;
}

.meta-line {
  margin: 0;
  color: #7280a1;
  font-size: 13px;
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.qty-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.qty-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 7px;
  background: #eef2ff;
  color: #435ecf;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.qty-num {
  min-width: 16px;
  text-align: center;
  color: #3d4f7a;
  font-weight: 600;
}

.remove-icon-btn {
  position: relative;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: #ff5a5f;
  cursor: pointer;
}

.remove-icon-btn::after {
  content: '';
  position: absolute;
  left: 5px;
  right: 5px;
  top: 10px;
  height: 2px;
  border-radius: 2px;
  background: #fff;
}

.drawer-foot {
  border-top: 1px solid #edf1ff;
  padding: 12px 14px 14px;
}

.drawer-foot p {
  margin: 0 0 10px;
  color: #46567f;
}

.foot-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 960px) {
  .medicine-grid {
    grid-template-columns: 1fr;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .floating-cart {
    top: auto !important;
    bottom: 18px;
    transform: none;
  }
}
</style>
