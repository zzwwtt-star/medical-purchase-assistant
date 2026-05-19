<template>
  <div class="user-page">
    <div class="user-card">
      <h1>个人中心</h1>

      <section class="profile-section">
        <label class="avatar-wrap" for="avatarInput" title="点击更换头像">
          <img v-if="avatarUrl" :src="avatarUrl" alt="用户头像" class="avatar-img" />
          <div v-else class="avatar-default" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.4 0-8 2.2-8 5a1 1 0 1 0 2 0c0-1.5 2.6-3 6-3s6 1.5 6 3a1 1 0 1 0 2 0c0-2.8-3.6-5-8-5Z"/>
            </svg>
          </div>
          <span class="avatar-tip">点击更换头像</span>
        </label>
        <input id="avatarInput" class="hidden-input" type="file" accept="image/*" @change="onAvatarChange" />

        <div class="account-info">
          <p class="label">账号</p>
          <p class="value">{{ username }}</p>
        </div>
      </section>

      <section class="panel">
        <h2>密码管理</h2>
        <button class="primary-btn" @click="goPasswordPage">修改密码</button>
      </section>

      <section class="panel">
        <h2>收货地址</h2>

        <template v-if="!isEditingAddress">
          <p class="address-text" :class="{ empty: !address }">{{ address || '待填写' }}</p>
          <button class="primary-btn" @click="isEditingAddress = true">{{ address ? '修改地址' : '填写地址' }}</button>
        </template>

        <template v-else>
          <div class="field">
            <label for="address">地址信息</label>
            <textarea id="address" v-model="draftAddress" rows="3" placeholder="例如：广东省深圳市南山区 xx 路 xx 号"></textarea>
          </div>
          <div class="row-actions">
            <button class="primary-btn" @click="saveAddress">保存地址</button>
            <button class="ghost-btn" @click="cancelEditAddress">取消</button>
          </div>
        </template>
      </section>

      <div class="actions">
        <button class="ghost-btn" @click="goHome">返回首页</button>
        <button class="danger-btn" @click="logout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearLoginUser, getLoginUser, setLoginUser, updateUser } from '../../api'

const router = useRouter()

const user = ref(getLoginUser())
const username = computed(() => user.value?.username || '用户')
const getAvatarStorageKey = (name) => `demo_user_avatar_${name || ''}`

const avatarUrl = ref('')
const address = ref('')
const draftAddress = ref('')
const isEditingAddress = ref(false)

onMounted(() => {
  avatarUrl.value = user.value?.username
    ? localStorage.getItem(getAvatarStorageKey(user.value.username)) || ''
    : ''
  address.value = user.value?.address || ''
  draftAddress.value = address.value
})

const onAvatarChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    window.alert('请选择图片文件')
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    const result = String(reader.result || '')
    avatarUrl.value = result
    if (user.value?.username) {
      localStorage.setItem(getAvatarStorageKey(user.value.username), result)
    }
    window.alert('头像已更新')
  }
  reader.readAsDataURL(file)
}

const goPasswordPage = () => {
  router.push('/user/password')
}

const saveAddress = async () => {
  if (!draftAddress.value.trim()) {
    window.alert('请先输入收货地址')
    return
  }

  if (!user.value?.id) {
    window.alert('请先登录')
    return
  }

  try {
    const updated = await updateUser(user.value.id, { address: draftAddress.value.trim() })
    user.value = updated
    setLoginUser(updated)
    address.value = updated.address || ''
    isEditingAddress.value = false
    window.alert('收货地址已保存')
  } catch (error) {
    window.alert(error.message || '保存失败')
  }
}

const cancelEditAddress = () => {
  draftAddress.value = address.value
  isEditingAddress.value = false
}

const goHome = () => router.push('/')

const logout = () => {
  clearLoginUser()
  window.alert('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(180deg, #f7f9ff 0%, #edf2ff 100%);
}

.user-card {
  max-width: 760px;
  margin: 0 auto;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 14px 32px rgba(71, 99, 255, 0.12);
  padding: 24px;
}

h1 {
  margin: 0 0 16px;
  color: #293b66;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar-wrap {
  position: relative;
  width: 92px;
  height: 92px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  border: 3px solid #dce5ff;
}

.avatar-img,
.avatar-default {
  width: 100%;
  height: 100%;
}

.avatar-img {
  object-fit: cover;
}

.avatar-default {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fff 0%, #f4f7ff 100%);
}

.avatar-default svg {
  width: 44px;
  height: 44px;
  fill: #3556ff;
}

.avatar-tip {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  font-size: 11px;
  text-align: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  padding: 3px 0;
}

.hidden-input {
  display: none;
}

.account-info .label {
  color: #7280a3;
  margin: 0 0 6px;
}

.account-info .value {
  margin: 0;
  font-size: 20px;
  color: #2b3c68;
  font-weight: 700;
}

.panel {
  border: 1px solid #e5ebff;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 14px;
}

.panel h2 {
  margin: 0 0 12px;
  font-size: 18px;
  color: #334875;
}

.panel-text {
  margin: 0 0 12px;
  color: #67779b;
}

.field {
  margin-bottom: 10px;
}

.field label {
  display: block;
  margin-bottom: 6px;
  color: #4a5b84;
}

input,
textarea {
  width: 100%;
  border: 1px solid #d7def7;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
}

.address-text {
  margin: 0 0 12px;
  color: #3f507a;
  line-height: 1.6;
  white-space: pre-wrap;
}

.address-text.empty {
  color: #9aa6c3;
}

.row-actions {
  display: flex;
  gap: 10px;
}

input:focus,
textarea:focus {
  border-color: #4b67ff;
  box-shadow: 0 0 0 3px rgba(75, 103, 255, 0.14);
}

.primary-btn {
  border: none;
  border-radius: 10px;
  background: #3f5dff;
  color: #fff;
  padding: 10px 14px;
  cursor: pointer;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
}

.ghost-btn,
.danger-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
}

.ghost-btn {
  background: #eef2ff;
  color: #435fcf;
}

.danger-btn {
  background: #ffeff0;
  color: #d6434c;
}

@media (max-width: 768px) {
  .user-page {
    padding: 14px;
  }

  .user-card {
    padding: 16px;
  }

  .profile-section {
    align-items: flex-start;
    flex-direction: column;
  }

  .actions {
    gap: 10px;
    flex-direction: column;
  }
}
</style>
