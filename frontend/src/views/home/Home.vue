<template>
  <div class="home-page">
    <div class="bg-decoration bg-decoration-1"></div>
    <div class="bg-decoration bg-decoration-2"></div>

    <header class="top-bar glass-card">
      <div class="brand-wrap">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 2a5 5 0 0 0-5 5v2.1A4.9 4.9 0 0 0 4 13.7C4 16.6 6.4 19 9.3 19H10v2H8a1 1 0 1 0 0 2h8a1 1 0 1 0 0-2h-2v-2h.7c2.9 0 5.3-2.4 5.3-5.3 0-2-1.1-3.8-3-4.6V7a5 5 0 0 0-5-5Zm-3 5a3 3 0 1 1 6 0v2H9V7Zm.3 10C7.5 17 6 15.5 6 13.7c0-1.2.7-2.3 1.8-2.9V12a1 1 0 0 0 1 1h6.4a1 1 0 0 0 1-1v-1.2a3.3 3.3 0 0 1 1.8 2.9c0 1.8-1.5 3.3-3.3 3.3H9.3Z"
            />
          </svg>
        </div>
        <div>
          <div class="logo">智能购药系统</div>
          <p class="logo-subtitle">AI Health Assistant</p>
        </div>
      </div>

      <div class="user-actions">
        <span v-if="isLogin" class="user-name">{{ currentUser }}</span>
        <button class="avatar-btn" @click="goLogin" :aria-label="isLogin ? '用户中心' : '登录'">
          <img v-if="isLogin && avatarUrl" :src="avatarUrl" alt="用户头像" class="avatar-img" />
          <svg v-else viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.4 0-8 2.2-8 5a1 1 0 1 0 2 0c0-1.5 2.6-3 6-3s6 1.5 6 3a1 1 0 1 0 2 0c0-2.8-3.6-5-8-5Z"
            />
          </svg>
        </button>
        <button v-if="isLogin" class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="hero glass-card">
      <div class="hero-tag">智能问诊 · 语音交互 · 快速购药</div>
      <h1>语音购药，更快更安心</h1>
      <p>说出你的症状或药名，系统将为你快速匹配合适药品和用药建议。</p>
      <button class="primary-btn" @click="goVoiceChat">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 3a4 4 0 0 0-4 4v4a4 4 0 1 0 8 0V7a4 4 0 0 0-4-4Zm-6 8a1 1 0 0 1 1 1 5 5 0 0 0 10 0 1 1 0 1 1 2 0 7 7 0 0 1-6 6.9V21h2a1 1 0 1 1 0 2H9a1 1 0 0 1 0-2h2v-2.1A7 7 0 0 1 5 12a1 1 0 0 1 1-1Z"
          />
        </svg>
        开始语音购药
      </button>
    </main>

    <section class="quick-actions">
      <button class="action-card" @click="goCart">
        <div class="action-icon cart-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M7.2 5H21a1 1 0 0 1 1 .8l-1.4 7A2 2 0 0 1 18.6 14H9a2 2 0 0 1-2-1.6L5.4 4H3a1 1 0 1 1 0-2h3.2a1 1 0 0 1 1 .8L7.2 5Zm2.6 11a2 2 0 1 0 2 2 2 2 0 0 0-2-2Zm7 0a2 2 0 1 0 2 2 2 2 0 0 0-2-2Z"
            />
          </svg>
        </div>
        <h3>购物车</h3>
        <p>查看并结算已选药品</p>
      </button>

      <button class="action-card" @click="goOrder">
        <div class="action-icon order-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M7 2h10a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V5a3 3 0 0 1 3-3Zm1 5a1 1 0 1 0 0 2h8a1 1 0 1 0 0-2H8Zm0 4a1 1 0 1 0 0 2h8a1 1 0 1 0 0-2H8Zm0 4a1 1 0 0 0 0 2h5a1 1 0 1 0 0-2H8Z"
            />
          </svg>
        </div>
        <h3>订单</h3>
        <p>查看配送进度与历史记录</p>
      </button>

      <button class="action-card" @click="goMedicineDetail">
        <div class="action-icon medicine-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M14.1 2.3a4 4 0 0 1 5.6 5.6l-2.8 2.8-5.6-5.6 2.8-2.8ZM10 6.4l7.6 7.6-4.2 4.2A5.4 5.4 0 1 1 5.8 10L10 6.4Zm-2 7a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2H8Z"
            />
          </svg>
        </div>
        <h3>药品详情</h3>
        <p>了解药品说明、规格与用法</p>
      </button>
    </section>

  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearLoginUser, getLoginUser } from '../../api'

const router = useRouter()
const userState = ref(getLoginUser())
const getAvatarStorageKey = (username) => `demo_user_avatar_${username || ''}`
const avatarUrl = ref('')

const isLogin = computed(() => Boolean(userState.value))
const currentUser = computed(() => userState.value?.username || '')

const syncUserState = () => {
  userState.value = getLoginUser()
  avatarUrl.value = userState.value?.username
    ? localStorage.getItem(getAvatarStorageKey(userState.value.username)) || ''
    : ''
}

onMounted(() => {
  syncUserState()
  window.addEventListener('focus', syncUserState)
})

onUnmounted(() => {
  window.removeEventListener('focus', syncUserState)
})

const goLogin = () => {
  if (!isLogin.value) router.push('/login')
  else router.push('/user')
}

const logout = () => {
  clearLoginUser()
  userState.value = null
  avatarUrl.value = ''
  window.alert('已退出登录')
}

const goVoiceChat = () => router.push('/voice-chat')
const goCart = () => router.push('/cart')
const goOrder = () => router.push('/order')
const goMedicineDetail = () => router.push('/medicine')
</script>

<style scoped>
.home-page {
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  padding: 20px 24px 18px;
  background: radial-gradient(circle at 10% 10%, #dce7ff 0%, transparent 30%),
    radial-gradient(circle at 90% 15%, #e6f0ff 0%, transparent 25%),
    linear-gradient(180deg, #f7f9ff 0%, #eef3ff 100%);
  color: #1f2a44;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(4px);
  opacity: 0.5;
  pointer-events: none;
}

.bg-decoration-1 {
  width: 280px;
  height: 280px;
  right: -80px;
  top: -80px;
  background: radial-gradient(circle, rgba(83, 120, 255, 0.35) 0%, rgba(83, 120, 255, 0) 70%);
}

.bg-decoration-2 {
  width: 240px;
  height: 240px;
  left: -60px;
  bottom: 40px;
  background: radial-gradient(circle, rgba(101, 220, 255, 0.35) 0%, rgba(101, 220, 255, 0) 70%);
}

.glass-card {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 12px 30px rgba(71, 99, 255, 0.09);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 16px;
  padding: 16px 18px;
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3556ff 0%, #5a75ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon svg {
  width: 20px;
  height: 20px;
  fill: #fff;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #3556ff;
  line-height: 1.1;
}

.logo-subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: #6a7692;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  max-width: 120px;
  font-size: 13px;
  color: #3f4f79;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.avatar-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(180deg, #fff 0%, #f4f7ff 100%);
  box-shadow: 0 8px 20px rgba(71, 99, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.avatar-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(71, 99, 255, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-btn svg {
  width: 21px;
  height: 21px;
  fill: #3556ff;
}

.logout-btn {
  border: 1px solid rgba(53, 86, 255, 0.25);
  background: rgba(255, 255, 255, 0.88);
  color: #3556ff;
  border-radius: 10px;
  font-size: 12px;
  padding: 7px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #3556ff;
  color: #fff;
}

.hero {
  text-align: center;
  border-radius: 22px;
  padding: 52px 24px;
}

.hero-tag {
  display: inline-block;
  margin-bottom: 12px;
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 999px;
  color: #3556ff;
  background: rgba(53, 86, 255, 0.12);
}

.hero h1 {
  font-size: 36px;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}

.hero p {
  color: #5c6b8a;
  margin-bottom: 18px;
}

.primary-btn {
  border: none;
  background: linear-gradient(135deg, #3556ff 0%, #5a75ff 100%);
  color: #fff;
  padding: 13px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  display: inline-flex;
  gap: 8px;
  align-items: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 12px 24px rgba(53, 86, 255, 0.28);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(53, 86, 255, 0.35);
}

.primary-btn svg {
  width: 18px;
  height: 18px;
  fill: #fff;
}

.quick-actions {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-items: stretch;
}

.action-card {
  text-align: left;
  border: none;
  background: #ffffff;
  border-radius: 14px;
  padding: 18px;
  min-height: 178px;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(71, 99, 255, 0.08);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 30px rgba(71, 99, 255, 0.15);
}

.action-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.action-icon svg {
  width: 22px;
  height: 22px;
  fill: #fff;
}

.cart-icon { background: linear-gradient(135deg, #4aa3ff 0%, #5c7dff 100%); }
.order-icon { background: linear-gradient(135deg, #7e6bff 0%, #b56dff 100%); }
.medicine-icon { background: linear-gradient(135deg, #26c5a3 0%, #3fbf7f 100%); }

.action-card h3 {
  margin-bottom: 8px;
  color: #2c3c66;
}

.action-card p {
  color: #6a7692;
  font-size: 14px;
}


@media (max-width: 900px) {
  .home-page {
    padding: 16px 16px 14px;
    gap: 12px;
  }

  .top-bar {
    padding: 14px 14px;
  }

  .user-name {
    display: none;
  }

  .logout-btn {
    padding: 6px 8px;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .hero {
    padding: 36px 16px;
  }

  .hero h1 {
    font-size: 30px;
  }

  .action-card {
    min-height: auto;
    padding: 16px;
  }
}
</style>
