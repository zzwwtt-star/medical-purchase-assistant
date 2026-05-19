<template>
  <div class="detail-page">
    <header class="top-bar card">
      <button class="ghost-btn" @click="goBack">返回列表</button>
      <h1>药品详情</h1>
      <button class="ghost-btn" @click="goHome">首页</button>
    </header>

    <section v-if="medicine" class="detail-main card">
      <div class="image-box" :class="medicine.colorClass">💊</div>
      <div class="info-box">
        <h2>{{ medicine.name }}</h2>
        <p class="category">分类：{{ medicine.category }}</p>
        <div class="symptoms">
          <span v-for="s in medicine.symptoms" :key="s" class="chip">{{ s }}</span>
        </div>

        <p class="price">￥{{ medicine.price }}</p>
        <p class="line">规格：{{ medicine.spec }}</p>
        <p class="line">厂家：{{ medicine.manufacturer }}</p>

        <div class="buy-row">
          <div class="qty">
            <button @click="decreaseQty">-</button>
            <span>{{ quantity }}</span>
            <button @click="increaseQty">+</button>
          </div>
          <button class="primary-btn" @click="addToCart">加入购物车</button>
        </div>
      </div>
    </section>

    <section v-if="medicine" class="detail-desc card">
      <h3>功能主治</h3>
      <p>{{ medicine.desc }}</p>

      <h3>用法用量</h3>
      <p>{{ medicine.usage }}</p>

      <h3>注意事项</h3>
      <ul>
        <li v-for="(n, idx) in medicine.notice" :key="idx">{{ n }}</li>
      </ul>

      <p class="tip">温馨提示：本页面信息仅供参考，如症状严重请及时就医。</p>
    </section>

    <section v-if="medicine" class="recommend card">
      <h3>同类推荐</h3>
      <div class="recommend-list">
        <button
          v-for="item in recommendList"
          :key="item.id"
          class="recommend-item"
          @click="goDetail(item.id)"
        >
          {{ item.name }}
        </button>
      </div>
    </section>

    <div v-if="!medicine" class="card not-found">
      未找到该药品信息。
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { addCartItem, fetchMedicineDetail, fetchMedicines, getLoginUser } from '../../api'

const route = useRoute()
const router = useRouter()

const quantity = ref(1)

const medicine = ref(null)
const medicinePool = ref([])
const currentUser = ref(getLoginUser())

const recommendList = computed(() => {
  if (!medicine.value) return []
  return medicinePool.value
    .filter((m) => m.category === medicine.value.category && m.id !== medicine.value.id)
    .slice(0, 3)
    .map((item) => hydrateMedicine(item))
})

const goBack = () => router.push('/medicine')
const goHome = () => router.push('/')
const goDetail = (id) => router.push(`/medicine/${id}`)

const decreaseQty = () => {
  if (quantity.value > 1) quantity.value -= 1
}

const increaseQty = () => {
  quantity.value += 1
}

const getColorClass = (seed) => {
  const value = String(seed || '')
  const hash = value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return `c${(hash % 5) + 1}`
}

const hydrateMedicine = (item) => {
  if (!item) return null
  return {
    ...item,
    notice: item.notice ? String(item.notice).split(/,|，|\n/).filter(Boolean) : [],
    symptoms: item.symptoms ? String(item.symptoms).split(/,|，|\n/).filter(Boolean) : [],
    colorClass: getColorClass(item.id || item.name)
  }
}

const loadDetail = async () => {
  try {
    const item = await fetchMedicineDetail(route.params.id)
    medicine.value = hydrateMedicine(item)
  } catch (error) {
    window.alert(error.message || '加载药品失败')
  }
}

const loadRecommend = async () => {
  try {
    const items = await fetchMedicines()
    medicinePool.value = items.map((item, index) => ({
      ...item,
      colorClass: `c${(index % 5) + 1}`
    }))
  } catch (error) {
    window.alert(error.message || '加载推荐失败')
  }
}

onMounted(() => {
  loadDetail()
  loadRecommend()
})

watch(() => route.params.id, () => {
  quantity.value = 1
  loadDetail()
  loadRecommend()
})

const addToCart = async () => {
  if (!medicine.value) return

  if (!currentUser.value?.id) {
    window.alert('请先登录')
    return
  }

  try {
    await addCartItem({
      user_id: currentUser.value.id,
      medicine_id: medicine.value.id,
      quantity: quantity.value
    })
    window.alert(`已加入购物车：${medicine.value.name} x${quantity.value}`)
  } catch (error) {
    window.alert(error.message || '加入购物车失败')
  }
}
</script>

<style scoped>
.detail-page { min-height: 100vh; padding: 20px; background: linear-gradient(180deg,#f7f9ff 0%,#edf2ff 100%); }
.card { background:#fff; border-radius:14px; box-shadow:0 10px 24px rgba(71,99,255,.08); }
.top-bar { display:flex; justify-content:space-between; align-items:center; padding:14px 16px; margin-bottom:12px; }
.top-bar h1 { margin:0; color:#2f4270; font-size:20px; }
.ghost-btn { border:none; background:#eef2ff; color:#425ecf; border-radius:8px; padding:8px 12px; cursor:pointer; }
.detail-main { display:grid; grid-template-columns:160px 1fr; gap:18px; padding:18px; margin-bottom:12px; }
.image-box { width:160px; height:160px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:56px; }
.info-box h2 { margin:0 0 6px; color:#2f4270; }
.category { margin:0 0 8px; color:#667596; }
.symptoms { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
.chip { background:#eef2ff; color:#50608a; border-radius:999px; padding:4px 10px; font-size:12px; }
.price { margin:0 0 6px; font-size:28px; font-weight:700; color:#2f53e0; }
.line { margin:0 0 4px; color:#5f6f92; }
.buy-row { margin-top:12px; display:flex; gap:10px; align-items:center; }
.qty { display:flex; align-items:center; border:1px solid #d7def7; border-radius:10px; overflow:hidden; }
.qty button { width:32px; height:36px; border:none; background:#f3f6ff; color:#445fce; cursor:pointer; }
.qty span { width:38px; text-align:center; }
.primary-btn { border:none; border-radius:10px; background:#3f5dff; color:#fff; padding:10px 14px; cursor:pointer; }
.detail-desc { padding:16px; margin-bottom:12px; }
.detail-desc h3 { margin:0 0 8px; color:#2f4270; }
.detail-desc p { margin:0 0 12px; color:#5f6f92; line-height:1.6; }
.detail-desc ul { margin:0 0 12px 18px; color:#5f6f92; }
.tip { color:#6a78a0; font-size:13px; }
.recommend { padding:16px; }
.recommend h3 { margin:0 0 10px; color:#2f4270; }
.recommend-list { display:flex; gap:8px; flex-wrap:wrap; }
.recommend-item { border:none; border-radius:8px; padding:8px 10px; background:#eef2ff; color:#4460ce; cursor:pointer; }
.not-found { padding:18px; color:#6b7896; }
.c1 { background:#dce6ff; } .c2 { background:#e9dcff; } .c3 { background:#d9f6ff; } .c4 { background:#e2ffe2; } .c5 { background:#fff0d9; }
@media (max-width: 900px) {
  .detail-main { grid-template-columns:1fr; }
  .image-box { width:100%; height:140px; }
}
</style>
