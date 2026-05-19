<template>
  <div class="detail-page" v-if="medicine">
    <header class="top-bar">
      <button class="ghost" @click="goBack">返回药品管理</button>
      <div>
        <h2>{{ medicine.name }}</h2>
        <p>分类：{{ medicine.category || '未分类' }}</p>
      </div>
      <span class="status" :class="medicine.on_sale ? 'on' : 'off'">
        {{ medicine.on_sale ? '上架中' : '已下架' }}
      </span>
    </header>

    <section class="main">
      <div class="card">
        <h3>基础信息</h3>
        <div class="grid">
          <div>
            <span>规格</span>
            <strong>{{ medicine.spec || '-' }}</strong>
          </div>
          <div>
            <span>价格</span>
            <strong>¥{{ Number(medicine.price || 0).toFixed(2) }}</strong>
          </div>
          <div>
            <span>厂家</span>
            <strong>{{ medicine.manufacturer || '-' }}</strong>
          </div>
          <div>
            <span>库存</span>
            <strong>{{ medicine.stock }}</strong>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>功能主治</h3>
        <p>{{ medicine.desc || '暂无描述' }}</p>
      </div>

      <div class="card">
        <h3>用法用量</h3>
        <p>{{ medicine.usage || '暂无说明' }}</p>
      </div>

      <div class="card">
        <h3>注意事项</h3>
        <ul v-if="noticeList.length">
          <li v-for="(item, idx) in noticeList" :key="idx">{{ item }}</li>
        </ul>
        <p v-else>暂无注意事项</p>
      </div>

      <div class="card">
        <h3>适应症/症状</h3>
        <div class="chips">
          <span v-for="item in symptomList" :key="item" class="chip">{{ item }}</span>
        </div>
        <p v-if="!symptomList.length">暂无症状信息</p>
      </div>
    </section>
  </div>
  <div v-else class="loading">加载中...</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchMedicineDetail } from '../../api'

const route = useRoute()
const router = useRouter()
const medicine = ref(null)

const parseList = (value) =>
  value ? String(value).split(/,|，|\n/).map((item) => item.trim()).filter(Boolean) : []

const noticeList = computed(() => parseList(medicine.value?.notice))
const symptomList = computed(() => parseList(medicine.value?.symptoms))

const loadDetail = async () => {
  try {
    medicine.value = await fetchMedicineDetail(route.params.id)
  } catch (error) {
    window.alert(error.message || '加载药品详情失败')
  }
}

const goBack = () => router.push('/products')

onMounted(loadDetail)
</script>

<style scoped>
.detail-page {
  display: grid;
  gap: 20px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--panel);
  padding: 18px 20px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  gap: 16px;
}

.top-bar h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.top-bar p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.ghost {
  border: none;
  background: #eef2ff;
  color: var(--primary);
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.status.on {
  background: #dcfce7;
  color: #15803d;
}

.status.off {
  background: #fee2e2;
  color: #b91c1c;
}

.main {
  display: grid;
  gap: 16px;
}

.card {
  background: var(--panel);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
}

.card h3 {
  margin: 0 0 12px;
  font-size: 16px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.grid span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 6px;
}

.grid strong {
  font-size: 15px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #eef2ff;
  color: #425ecf;
  font-size: 12px;
}

.loading {
  padding: 40px;
  text-align: center;
  color: var(--muted);
}
</style>
