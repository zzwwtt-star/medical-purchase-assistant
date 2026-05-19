<template>
  <div class="products-page">
    <header class="page-header">
      <div>
        <h2>药品管理</h2>
        <p>维护库存、分类与上架状态</p>
      </div>
      <button class="primary" @click="openCreate">新增药品</button>
    </header>

    <div class="table">
      <div class="table-row head">
        <span>名称</span>
        <span>分类</span>
        <span>规格</span>
        <span>价格</span>
        <span>上架</span>
        <span>操作</span>
      </div>
      <div
        v-for="item in medicines"
        :key="item.id"
        class="table-row"
        @click="goDetail(item.id)"
      >
        <span>
          <strong>{{ item.name }}</strong>
          <em>{{ item.manufacturer || '暂无厂家' }}</em>
        </span>
        <span>{{ item.category || '-' }}</span>
        <span>{{ item.spec || '-' }}</span>
        <span>¥{{ Number(item.price || 0).toFixed(2) }}</span>
        <span>{{ item.on_sale ? '是' : '否' }}</span>
        <span class="actions">
          <button class="ghost" @click.stop="openEdit(item)">编辑</button>
          <button class="ghost danger" @click.stop="remove(item.id)">删除</button>
        </span>
      </div>
      <div v-if="!medicines.length" class="empty">暂无药品</div>
    </div>

    <div v-if="showDialog" class="dialog-backdrop">
      <div class="dialog">
        <header>
          <h3>{{ editing ? '编辑药品' : '新增药品' }}</h3>
          <button class="ghost" @click="closeDialog">关闭</button>
        </header>
        <form @submit.prevent="save">
          <label>
            名称
            <input v-model="form.name" required />
          </label>
          <label>
            分类
            <input v-model="form.category" placeholder="如：眼科/滴眼液" />
          </label>
          <label>
            规格/计量
            <input v-model="form.spec" placeholder="如：10ml/支" />
          </label>
          <label>
            价格
            <input v-model.number="form.price" type="number" min="0" step="0.01" />
          </label>
          <label>
            生产厂家
            <input v-model="form.manufacturer" />
          </label>
          <label class="switch">
            <input v-model="form.on_sale" type="checkbox" />
            <span>上架销售</span>
          </label>
          <label>
            功能/用途
            <textarea v-model="form.desc" rows="3"></textarea>
          </label>
          <label>
            用法用量
            <textarea v-model="form.usage" rows="2"></textarea>
          </label>
          <label>
            注意事项
            <textarea v-model="form.notice" rows="2"></textarea>
          </label>
          <label>
            适应症/症状
            <textarea v-model="form.symptoms" rows="2"></textarea>
          </label>
          <div class="dialog-actions">
            <button type="button" class="ghost" @click="closeDialog">取消</button>
            <button type="submit" class="primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createMedicine, deleteMedicine, fetchMedicines, updateMedicine } from '../../api'

const router = useRouter()
const medicines = ref([])
const showDialog = ref(false)
const editing = ref(false)
const editingId = ref(null)

const form = reactive({
  name: '',
  category: '',
  spec: '',
  price: 0,
  manufacturer: '',
  on_sale: true,
  desc: '',
  usage: '',
  notice: '',
  symptoms: ''
})

const resetForm = () => {
  form.name = ''
  form.category = ''
  form.spec = ''
  form.price = 0
  form.manufacturer = ''
  form.on_sale = true
  form.desc = ''
  form.usage = ''
  form.notice = ''
  form.symptoms = ''
}

const loadMedicines = async () => {
  try {
    medicines.value = await fetchMedicines()
  } catch (error) {
    window.alert(error.message || '加载药品失败')
  }
}

const openCreate = () => {
  editing.value = false
  editingId.value = null
  resetForm()
  showDialog.value = true
}

const goDetail = (id) => {
  router.push(`/products/${id}`)
}

const openEdit = (item) => {
  editing.value = true
  editingId.value = item.id
  form.name = item.name
  form.category = item.category
  form.spec = item.spec
  form.price = item.price
  form.manufacturer = item.manufacturer
  form.on_sale = item.on_sale
  form.desc = item.desc
  form.usage = item.usage
  form.notice = item.notice
  form.symptoms = item.symptoms
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

const save = async () => {
  try {
    if (editing.value && editingId.value) {
      await updateMedicine(editingId.value, form)
    } else {
      await createMedicine(form)
    }
    closeDialog()
    loadMedicines()
  } catch (error) {
    window.alert(error.message || '保存失败')
  }
}

const remove = async (id) => {
  if (!window.confirm('确定删除该药品吗？')) {
    return
  }
  try {
    await deleteMedicine(id)
    loadMedicines()
  } catch (error) {
    window.alert(error.message || '删除失败')
  }
}

onMounted(loadMedicines)
</script>

<style scoped>
.products-page {
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

.primary {
  padding: 10px 18px;
  border-radius: 12px;
  border: none;
  background: var(--primary);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.table {
  display: grid;
  gap: 10px;
}

.table-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr 0.9fr 0.6fr 0.5fr 1fr;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8fafc;
  font-size: 13px;
  align-items: center;
  cursor: pointer;
}

.table-row.head {
  cursor: default;
}

.table-row span strong {
  display: block;
  font-weight: 600;
}

.table-row span em {
  display: block;
  font-size: 12px;
  color: var(--muted);
  font-style: normal;
}

.table-row.head {
  background: #eef2ff;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
}

.ghost {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: white;
  cursor: pointer;
  font-size: 12px;
}

.ghost.danger {
  color: #dc2626;
}

.empty {
  text-align: center;
  color: var(--muted);
  padding: 30px 0 0;
}

.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: grid;
  place-items: center;
  z-index: 20;
}

.dialog {
  width: min(520px, 92vw);
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  max-height: 90vh;
  overflow: auto;
}

.dialog header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dialog h3 {
  margin: 0;
  font-size: 18px;
}

.dialog form {
  display: grid;
  gap: 14px;
}

label {
  display: grid;
  gap: 8px;
  font-size: 13px;
}

input,
textarea {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  font-size: 13px;
}

.switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

@media (max-width: 860px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .actions {
    justify-content: flex-start;
  }
}
</style>
