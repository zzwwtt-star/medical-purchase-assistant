<template>
  <div class="password-page">
    <div class="password-card">
      <h1>修改密码</h1>

      <div class="field">
        <label for="oldPassword">当前密码</label>
        <div class="password-wrap">
          <input id="oldPassword" v-model="form.oldPassword" :type="showOld ? 'text' : 'password'" placeholder="请输入当前密码" />
          <button class="eye-btn" type="button" aria-label="按住查看当前密码" @mousedown="showOld = true" @mouseup="showOld = false" @mouseleave="showOld = false" @touchstart.prevent="showOld = true" @touchend="showOld = false" @touchcancel="showOld = false">
            <svg v-if="showOld" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M2.8 4.2a1 1 0 0 1 1.4 0l15.6 15.6a1 1 0 0 1-1.4 1.4l-3.2-3.2a11.7 11.7 0 0 1-3.2.4c-5.6 0-9.6-4.1-11-6.1a1.9 1.9 0 0 1 0-2.4 21 21 0 0 1 5.3-4.9L2.8 5.6a1 1 0 0 1 0-1.4Zm8.2 8.2 2.8 2.8a3 3 0 0 1-2.8-2.8Zm8.7 1.3L17.8 12a6 6 0 0 0-7.9-7.9L8.1 2.3A11.2 11.2 0 0 1 12 1.6c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4 20.8 20.8 0 0 1-3.3 3.6Z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4c-1.4 2-5.4 6.1-11 6.1S2.4 15.5 1 13.5a1.9 1.9 0 0 1 0-2.4C2.4 9.1 6.4 5 12 5Zm0 2c-4.6 0-8 3.2-9.3 5 1.3 1.8 4.7 5 9.3 5s8-3.2 9.3-5c-1.3-1.8-4.7-5-9.3-5Zm0 2.5a2.5 2.5 0 1 1-2.5 2.5A2.5 2.5 0 0 1 12 9.5Z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="field">
        <label for="newPassword">新密码</label>
        <div class="password-wrap">
          <input id="newPassword" v-model="form.newPassword" :type="showNew ? 'text' : 'password'" placeholder="请输入新密码" />
          <button class="eye-btn" type="button" aria-label="按住查看新密码" @mousedown="showNew = true" @mouseup="showNew = false" @mouseleave="showNew = false" @touchstart.prevent="showNew = true" @touchend="showNew = false" @touchcancel="showNew = false">
            <svg v-if="showNew" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M2.8 4.2a1 1 0 0 1 1.4 0l15.6 15.6a1 1 0 0 1-1.4 1.4l-3.2-3.2a11.7 11.7 0 0 1-3.2.4c-5.6 0-9.6-4.1-11-6.1a1.9 1.9 0 0 1 0-2.4 21 21 0 0 1 5.3-4.9L2.8 5.6a1 1 0 0 1 0-1.4Zm8.2 8.2 2.8 2.8a3 3 0 0 1-2.8-2.8Zm8.7 1.3L17.8 12a6 6 0 0 0-7.9-7.9L8.1 2.3A11.2 11.2 0 0 1 12 1.6c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4 20.8 20.8 0 0 1-3.3 3.6Z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4c-1.4 2-5.4 6.1-11 6.1S2.4 15.5 1 13.5a1.9 1.9 0 0 1 0-2.4C2.4 9.1 6.4 5 12 5Zm0 2c-4.6 0-8 3.2-9.3 5 1.3 1.8 4.7 5 9.3 5s8-3.2 9.3-5c-1.3-1.8-4.7-5-9.3-5Zm0 2.5a2.5 2.5 0 1 1-2.5 2.5A2.5 2.5 0 0 1 12 9.5Z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="field">
        <label for="confirmPassword">确认新密码</label>
        <div class="password-wrap">
          <input id="confirmPassword" v-model="form.confirmPassword" :type="showConfirm ? 'text' : 'password'" placeholder="请再次输入新密码" />
          <button class="eye-btn" type="button" aria-label="按住查看确认新密码" @mousedown="showConfirm = true" @mouseup="showConfirm = false" @mouseleave="showConfirm = false" @touchstart.prevent="showConfirm = true" @touchend="showConfirm = false" @touchcancel="showConfirm = false">
            <svg v-if="showConfirm" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M2.8 4.2a1 1 0 0 1 1.4 0l15.6 15.6a1 1 0 0 1-1.4 1.4l-3.2-3.2a11.7 11.7 0 0 1-3.2.4c-5.6 0-9.6-4.1-11-6.1a1.9 1.9 0 0 1 0-2.4 21 21 0 0 1 5.3-4.9L2.8 5.6a1 1 0 0 1 0-1.4Zm8.2 8.2 2.8 2.8a3 3 0 0 1-2.8-2.8Zm8.7 1.3L17.8 12a6 6 0 0 0-7.9-7.9L8.1 2.3A11.2 11.2 0 0 1 12 1.6c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4 20.8 20.8 0 0 1-3.3 3.6Z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5c5.6 0 9.6 4.1 11 6.1a1.9 1.9 0 0 1 0 2.4c-1.4 2-5.4 6.1-11 6.1S2.4 15.5 1 13.5a1.9 1.9 0 0 1 0-2.4C2.4 9.1 6.4 5 12 5Zm0 2c-4.6 0-8 3.2-9.3 5 1.3 1.8 4.7 5 9.3 5s8-3.2 9.3-5c-1.3-1.8-4.7-5-9.3-5Zm0 2.5a2.5 2.5 0 1 1-2.5 2.5A2.5 2.5 0 0 1 12 9.5Z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="actions">
        <button class="primary-btn" @click="savePassword">保存密码</button>
        <button class="ghost-btn" @click="goBack">返回个人中心</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = computed(() => localStorage.getItem('demo_login_user') || '')
const getPasswordStorageKey = (name) => `demo_user_password_${name || ''}`

const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const savePassword = () => {
  const key = getPasswordStorageKey(username.value)
  const savedPassword = localStorage.getItem(key)

  if (savedPassword && form.oldPassword !== savedPassword) {
    window.alert('当前密码不正确')
    return
  }

  if (form.newPassword.length < 6) {
    window.alert('新密码长度至少 6 位')
    return
  }

  if (form.newPassword === form.oldPassword) {
    window.alert('新密码不能与当前密码相同')
    return
  }

  if (form.newPassword !== form.confirmPassword) {
    window.alert('两次输入的新密码不一致')
    return
  }

  localStorage.setItem(key, form.newPassword)
  window.alert('密码已修改（演示）')
  router.push('/user')
}

const goBack = () => router.push('/user')
</script>

<style scoped>
.password-page {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(180deg, #f7f9ff 0%, #edf2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-card {
  width: 100%;
  max-width: 520px;
  background: #fff;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 14px 32px rgba(71, 99, 255, 0.12);
}

h1 {
  margin: 0 0 16px;
  color: #2f416d;
}

.field {
  margin-bottom: 12px;
}

label {
  display: block;
  margin-bottom: 6px;
  color: #4d5f89;
}

.password-wrap {
  display: grid;
  grid-template-columns: 1fr 40px;
  gap: 8px;
}

input {
  width: 100%;
  border: 1px solid #d7def7;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
}

input:focus {
  border-color: #4b67ff;
  box-shadow: 0 0 0 3px rgba(75, 103, 255, 0.14);
}

.eye-btn {
  border: none;
  border-radius: 10px;
  background: #eef2ff;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.primary-btn,
.ghost-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
}

.primary-btn {
  background: #3f5dff;
  color: #fff;
}

.ghost-btn {
  background: #eef2ff;
  color: #435fcf;
}
</style>
