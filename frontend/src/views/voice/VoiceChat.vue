<template>
  <div class="desktop-chat">
    <!-- Left Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <button class="back-link" @click="goHome">← 返回首页</button>
      </div>

      <div class="ai-profile">
        <div class="ai-avatar">
          <div class="avatar-circle" :class="{ active: connected }">
            <svg viewBox="0 0 24 24" width="36" height="36"><path d="M12 2a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" fill="#fff"/><path d="M12 18a6 6 0 0 0 6-6 1 1 0 0 0-2 0 4 4 0 0 1-8 0 1 1 0 0 0-2 0 6 6 0 0 0 6 6Z" fill="#fff"/><path d="M12 18v3h3a1 1 0 0 1 0 2H9a1 1 0 0 1 0-2h3v-3Z" fill="#fff"/></svg>
          </div>
        </div>
        <h3>智能购药助手</h3>
        <p class="ai-desc">基于本地大模型 · 语音交互</p>
        <div class="status-line">
          <span class="status-dot" :class="{ on: connected }"></span>
          {{ connected ? '在线中' : '未连接' }}
        </div>
      </div>

      <div class="sidebar-actions">
        <button class="action-btn call-action" @click="goCall">
          <svg viewBox="0 0 24 24" width="18" height="18"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z" fill="currentColor"/></svg>
          语音通话
        </button>
      </div>

      <div class="sidebar-footer">
        <p>按 Enter 发送文字</p>
        <p>按住 🎤 语音录入</p>
      </div>
    </aside>

    <!-- Main Chat -->
    <main class="chat-main">
      <div class="msg-area" ref="msgList">
        <div v-if="messages.length === 0" class="welcome">
          <p class="welcome-title">有什么可以帮您的？</p>
          <p class="welcome-sub">输入症状或药品名称，AI 助手会为您推荐合适的药品</p>
          <div class="suggestion-chips">
            <button class="chip" @click="quickAsk('我头痛怎么办')">我头痛怎么办</button>
            <button class="chip" @click="quickAsk('咳嗽有痰推荐什么药')">咳嗽有痰推荐什么药</button>
            <button class="chip" @click="quickAsk('胃不舒服吃什么药')">胃不舒服吃什么药</button>
          </div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-wrapper', msg.role]">
          <!-- System messages -->
          <div v-if="msg.role === 'system'" class="system-msg">
            <span class="system-icon">ℹ️</span>
            <span>{{ msg.text }}</span>
          </div>

          <!-- AI messages show avatar, user messages don't -->
          <template v-else>
          <div v-if="msg.role === 'assistant'" class="msg-avatar">
            <div class="avatar-circle small">
              <svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" fill="#3f5dff"/><path d="M12 18a6 6 0 0 0 6-6 1 1 0 0 0-2 0 4 4 0 0 1-8 0 1 1 0 0 0-2 0 6 6 0 0 0 6 6Z" fill="#3f5dff"/><path d="M12 18v3h3a1 1 0 0 1 0 2H9a1 1 0 0 1 0-2h3v-3Z" fill="#3f5dff"/></svg>
            </div>
          </div>
          <div class="msg-body">
            <div class="msg-bubble">
              <span class="msg-text">{{ msg.text }}</span>
            </div>
            <div
              v-if="msg.role === 'assistant' && msg._medicines && msg._medicines.length && !msg._medDismissed"
              class="med-recommend"
            >
              <!-- Step 1: confirm prompt -->
              <div v-if="!msg._medConfirmed" class="med-prompt">
                <svg viewBox="0 0 24 24" width="18" height="18" class="med-prompt-icon"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#34d399"/></svg>
                <span>检测到药品推荐，是否需要购买？</span>
                <button class="med-prompt-yes" @click="msg._medConfirmed = true">是</button>
                <button class="med-prompt-no" @click="msg._medDismissed = true">否</button>
              </div>
              <!-- Step 2: stacked card summaries (click to open detail modal) -->
              <div v-else class="med-cards-stack">
                <div
                  v-for="(med, i) in msg._medicines"
                  :key="med.id"
                  class="med-item-card"
                  @click="openMedModal(med)"
                >
                  <div class="med-item-top">
                    <div class="med-item-icon" :class="'c' + ((i % 5) + 1)">💊</div>
                    <div class="med-item-info">
                      <span class="med-item-name">{{ med.name }}</span>
                      <span class="med-item-meta">￥{{ med.price }}</span>
                    </div>
                    <svg viewBox="0 0 24 24" width="16" height="16" class="med-item-arrow"><path d="M8 5l7 7-7 7" stroke="#b4bed4" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
                  </div>
                </div>
              </div>
            </div>
            <button
              v-if="msg.role === 'assistant' && msg._audioChunks && msg._audioChunks.length"
              class="replay-btn"
              @click="replayMsg(msg)"
            >
              <svg viewBox="0 0 24 24" width="14" height="14"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>
              重播语音
            </button>
          </div>
          </template>
        </div>

        <div v-if="aiTyping" class="msg-wrapper assistant">
          <div class="msg-avatar">
            <div class="avatar-circle small">
              <svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" fill="#3f5dff"/><path d="M12 18a6 6 0 0 0 6-6 1 1 0 0 0-2 0 4 4 0 0 1-8 0 1 1 0 0 0-2 0 6 6 0 0 0 6 6Z" fill="#3f5dff"/><path d="M12 18v3h3a1 1 0 0 1 0 2H9a1 1 0 0 1 0-2h3v-3Z" fill="#3f5dff"/></svg>
            </div>
          </div>
          <div class="msg-body">
            <div class="msg-bubble typing">
              <span class="typing-dots"><i>•</i><i>•</i><i>•</i></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <input
            v-model="inputText"
            class="chat-input"
            :placeholder="inputPlaceholder"
            :disabled="!connected || aiBusy"
            @keyup.enter="sendText"
          />
          <div class="input-actions">
            <button
              v-if="inputText.trim()"
              class="send-btn"
              :disabled="!connected || aiBusy"
              @click="sendText"
            >
              <svg viewBox="0 0 24 24" width="18" height="18"><path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/></svg>
            </button>
            <button
              v-else
              class="mic-btn"
              :class="{ recording: recording, disabled: !connected || aiBusy }"
              :disabled="!connected || aiBusy"
              @mousedown.prevent="startRecord"
              @mouseup="stopRecord"
              @touchstart.prevent="startRecord"
              @touchend.prevent="stopRecord"
              @contextmenu.prevent
              title="按住说话"
            >
              <svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 3a4 4 0 0 0-4 4v4a4 4 0 1 0 8 0V7a4 4 0 0 0-4-4Zm-6 8a1 1 0 0 1 1 1 5 5 0 0 0 10 0 1 1 0 1 1 2 0 7 7 0 0 1-6 6.9V21h2a1 1 0 1 1 0 2H9a1 1 0 0 1 0-2h2v-2.1A7 7 0 0 1 5 12a1 1 0 0 1 1-1Z" fill="currentColor"/></svg>
            </button>
          </div>
        </div>
        <p class="input-hint" v-if="!connected">未连接 — 请确认后端已启动</p>
        <p class="input-hint busy" v-else-if="aiBusy">AI 思考中，请稍候...</p>
      </div>
    </main>

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

    <!-- Medicine Detail Modal -->
    <div v-if="medModal.visible" class="med-modal-overlay" @click.self="closeMedModal">
      <div class="med-modal" :class="{ show: medModal.visible }">
        <button class="med-modal-close" @click="closeMedModal" aria-label="关闭">
          <svg viewBox="0 0 24 24" width="18" height="18"><path d="M18 6L6 18M6 6l12 12" stroke="#8e9ab8" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        </button>

        <h2 class="med-modal-title">{{ medModal.med.name }}</h2>

        <div class="med-modal-sections">
          <div class="med-modal-section">
            <h4>功效</h4>
            <p>{{ medModal.med.symptoms || medModal.med.desc || '暂无说明' }}</p>
          </div>
          <div class="med-modal-section">
            <h4>用法</h4>
            <p>{{ medModal.med.usage || '暂无说明' }}</p>
          </div>
          <div class="med-modal-section">
            <h4>禁用人群</h4>
            <p>{{ medModal.med.notice || '暂无说明' }}</p>
          </div>
        </div>

        <div class="med-modal-qty-row">
          <div class="med-modal-qty">
            <button class="med-modal-qty-btn" @click="medModal.qty > 1 ? medModal.qty-- : null">-</button>
            <span class="med-modal-qty-num">{{ medModal.qty }}</span>
            <button class="med-modal-qty-btn" @click="medModal.qty++">+</button>
          </div>
          <div class="med-modal-total">
            <span class="med-modal-total-label">总价</span>
            <span class="med-modal-total-price">￥{{ (medModal.med.price * medModal.qty).toFixed(2) }}</span>
          </div>
        </div>

        <button
          class="med-modal-cart-btn"
          :class="{ added: medModal.added }"
          @click="addToCartFromModal"
        >
          {{ medModal.added ? '已加入购物车 ✓' : '加入购物车' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { addCartItem, fetchCart, getLoginUser, ollamaChatStream, removeCartItem, updateCartItem } from '../../api'

const router = useRouter()
const goHome = () => router.push('/')
const goCall = () => router.push('/voice-agent')

const SOCKET_URL = 'http://127.0.0.1:5000'

const connected = ref(false)
const recording = ref(false)
const aiBusy = ref(false)
const aiTyping = ref(false)
const inputText = ref('')
const messages = ref([])
const msgList = ref(null)
let currentAiIdx = -1
let aiTimeout = null

function ensureAiMsg() {
  if (currentAiIdx >= messages.value.length) {
    messages.value.push({ role: 'assistant', text: '', _audioChunks: [] })
    currentAiIdx = messages.value.length - 1
  }
  return messages.value[currentAiIdx]
}

const inputPlaceholder = computed(() => {
  if (!connected.value) return '未连接后端...'
  if (aiBusy.value) return 'AI 正在回复，请稍候...'
  return '输入症状或药品名称，按 Enter 发送...'
})

let socket = null

// ---- Cart state ----
const CART_TOP_KEY = 'demo_cart_top'
const cartExpanded = ref(false)
const cartDrawerOpen = ref(false)
const cartItems = ref([])
const currentUser = ref(getLoginUser())

const defaultCartTop = Math.round(window.innerHeight * 0.56)
const savedCartTop = Number(localStorage.getItem(CART_TOP_KEY))
const cartTop = ref(Number.isFinite(savedCartTop) && savedCartTop > 0 ? savedCartTop : defaultCartTop)
const isDragging = ref(false)
const dragMoved = ref(false)
let startPointerY = 0
let startCartTop = 0
let suppressClick = false

const cartCount = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity, 0))
const cartTotalPrice = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity * Number(item.price), 0))

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

const goCart = () => router.push('/cart')

// ---- Medicine Modal ----
const medModal = ref({
  visible: false,
  med: null,
  qty: 1,
  added: false,
})

function openMedModal(med) {
  medModal.value = { visible: true, med, qty: 1, added: false }
  document.body.style.overflow = 'hidden'
  document.addEventListener('keydown', onModalKeydown)
}

function closeMedModal() {
  medModal.value.visible = false
  document.body.style.overflow = ''
  document.removeEventListener('keydown', onModalKeydown)
}

async function addToCartFromModal() {
  const { med, qty } = medModal.value
  if (!currentUser.value?.id) {
    window.alert('请先登录')
    return
  }
  try {
    await addCartItem({
      user_id: currentUser.value.id,
      medicine_id: med.id,
      quantity: qty,
    })
    await loadCart()
    medModal.value.added = true
    setTimeout(() => {
      medModal.value.added = false
      closeMedModal()
    }, 800)
  } catch (error) {
    window.alert(error.message || '加入购物车失败')
  }
}

function onModalKeydown(e) {
  if (e.key === 'Escape') closeMedModal()
}

// ---- Legacy (kept for existing stacked card flow) ----
const addToCartFromCard = async (med) => {
  if (!currentUser.value?.id) {
    window.alert('请先登录')
    return
  }
  try {
    await addCartItem({
      user_id: currentUser.value.id,
      medicine_id: med.id,
      quantity: med._qty || 1
    })
    await loadCart()
    med._added = true
    setTimeout(() => { med._added = false }, 2000)
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

// ---- Browser Speech Recognition ----
let recognition = null
let recordingBusy = false
let recordStartTime = 0

// ---- Audio playback ----
let audioQueue = []

function playAudio(base64Data) {
  const blob = new Blob(
    [Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0))],
    { type: 'audio/mp3' }
  )
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  audio.onended = () => { URL.revokeObjectURL(url); playNext() }
  audioQueue.push(audio)
  if (audioQueue.length === 1) audio.play().catch(() => playNext())
}

function playNext() {
  audioQueue.shift()
  if (audioQueue.length > 0) audioQueue[0].play().catch(() => playNext())
}

function stopAllAudio() {
  for (const a of audioQueue) a.pause()
  audioQueue = []
}

function replayMsg(msg) {
  if (!msg._audioChunks || !msg._audioChunks.length) return
  stopAllAudio()
  for (const b64 of msg._audioChunks) playAudio(b64)
}

function addSystemMsg(text) {
  messages.value.push({ role: 'system', text })
}

function quickAsk(text) {
  inputText.value = text
  sendText()
}

// Shared: send user text to AI via SSE endpoint (used by both text input and voice)
async function sendToAI(userText) {
  stopAllAudio()

  const historyMsgs = messages.value
    .filter(m => m.role === 'user' || m.role === 'assistant')
    .map(m => ({ role: m.role, text: m.text }))

  messages.value.push({ role: 'user', text: userText })
  currentAiIdx = messages.value.length

  aiBusy.value = true
  aiTyping.value = true
  scrollBottom()

  clearTimeout(aiTimeout)
  aiTimeout = setTimeout(() => {
    if (aiBusy.value) {
      const msg = ensureAiMsg()
      if (!msg.text) {
        msg.text = '回复超时，请重新发送消息。'
      }
      aiBusy.value = false
      aiTyping.value = false
      currentAiIdx = -1
    }
  }, 90000)

  try {
    const response = await ollamaChatStream(userText, historyMsgs)
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data:')) continue
        const dataStr = trimmed.slice(5).trim()
        if (!dataStr) continue

        let payload
        try { payload = JSON.parse(dataStr) } catch { continue }

        if (payload.type === 'delta') {
          clearTimeout(aiTimeout)
          aiTyping.value = false
          ensureAiMsg().text += payload.content
          scrollBottom()
        } else if (payload.type === 'recommend') {
          const meds = payload.medicines.map(m => ({ ...m, _qty: 1, _added: false }))
          ensureAiMsg()._medicines = meds
          scrollBottom()
        } else if (payload.type === 'ai_audio') {
          clearTimeout(aiTimeout)
          ensureAiMsg()._audioChunks.push(payload.data)
          playAudio(payload.data)
        } else if (payload.type === 'error') {
          clearTimeout(aiTimeout)
          ensureAiMsg().text = payload.message || 'AI 服务异常'
          aiBusy.value = false
          aiTyping.value = false
          currentAiIdx = -1
        } else if (payload.type === 'done') {
          clearTimeout(aiTimeout)
          aiBusy.value = false
          aiTyping.value = false
          currentAiIdx = -1
        }
      }
    }
  } catch (err) {
    clearTimeout(aiTimeout)
    ensureAiMsg().text = '网络错误: ' + (err.message || '连接失败')
    aiBusy.value = false
    aiTyping.value = false
    currentAiIdx = -1
  }
}

async function sendText() {
  const text = inputText.value.trim()
  if (!text || !connected.value || aiBusy.value) return
  inputText.value = ''
  sendToAI(text)
}

// ---- Browser Speech Recognition (press-to-talk) ----
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

async function startRecord() {
  if (!SpeechRecognition) {
    addSystemMsg('当前浏览器不支持语音识别，请使用 Chrome 或 Edge。')
    return
  }
  if (!connected.value) {
    addSystemMsg('未连接后端，无法使用语音。请确认后端已启动。')
    return
  }
  if (aiBusy.value) {
    addSystemMsg('AI 正在回复中，请等待回复完成后再录音。')
    return
  }
  if (recordingBusy) return
  recordingBusy = true

  try {
    recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.interimResults = true
    recognition.continuous = true
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          recognition._finalText = (recognition._finalText || '') + event.results[i][0].transcript
        }
      }
    }

    recognition.onerror = (event) => {
      if (event.error === 'no-speech') {
        recognition._noSpeech = true
      } else if (event.error === 'not-allowed') {
        addSystemMsg('麦克风权限被拒绝，请在浏览器设置中允许本站使用麦克风。')
      } else if (event.error !== 'aborted') {
        addSystemMsg('语音识别错误: ' + event.error)
      }
    }

    recognition.onend = () => {
      if (recognition._resolveOnEnd) {
        recognition._resolveOnEnd()
        recognition._resolveOnEnd = null
        return
      }
      if (recording.value && recognition) {
        try { recognition.start() } catch {}
      }
    }

    recognition._finalText = ''
    recognition._noSpeech = false
    recognition.start()
    recording.value = true
    recordStartTime = Date.now()
  } catch (err) {
    recordingBusy = false
    addSystemMsg('语音识别启动失败: ' + (err.message || '未知错误'))
  }
}

async function stopRecord() {
  recordingBusy = false
  if (!recording.value) return
  recording.value = false

  const elapsed = Date.now() - recordStartTime

  if (recognition) {
    // Wait for onend to fire so all onresult callbacks are delivered
    await new Promise(resolve => {
      recognition._resolveOnEnd = resolve
      recognition.stop()
    })
  }

  // Too short — ignore
  if (elapsed < 500) {
    recognition = null
    return
  }

  const text = ((recognition && recognition._finalText) || '').trim()
  recognition = null

  if (!text) {
    addSystemMsg('未检测到语音内容，请重试。')
    return
  }

  sendToAI(text)
}

function setupSocket() {
  socket = io(SOCKET_URL, { transports: ['polling'] })

  socket.on('connect', () => {
    connected.value = true
    socket.emit('voice_chat_start')
  })

  socket.on('disconnect', () => {
    connected.value = false
    recording.value = false
    aiBusy.value = false
    aiTyping.value = false
  })

  socket.on('connect_error', () => {
    connected.value = false
    alert('无法连接到语音服务，请确认后端已启动。')
  })

  // Global listener for all voice_chat_msg events
  socket.on('voice_chat_msg', (msg) => {
    switch (msg.type) {
      case 'system_msg':
        addSystemMsg(msg.text)
        scrollBottom()
        break
      case 'ai_text':
        clearTimeout(aiTimeout)
        aiTyping.value = false
        ensureAiMsg().text += msg.delta
        scrollBottom()
        break
      case 'ai_audio':
        ensureAiMsg()._audioChunks.push(msg.data)
        playAudio(msg.data)
        break
      case 'ai_done':
        clearTimeout(aiTimeout)
        aiBusy.value = false
        aiTyping.value = false
        currentAiIdx = -1
        break
    }
  })
}

function scrollBottom() {
  nextTick(() => {
    if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
  })
}

setupSocket()

onMounted(() => {
  loadCart()
})

onBeforeUnmount(() => {
  stopAllAudio()
  if (recording.value) stopRecord()
  if (socket) {
    socket.emit('voice_chat_stop')
    socket.disconnect()
  }
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchmove', onDragMove)
  window.removeEventListener('touchend', endDrag)
  document.removeEventListener('keydown', onModalKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.desktop-chat {
  display: flex;
  height: 100vh;
  background: #f5f6fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== Sidebar ===== */
.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #eef0f5;
  padding: 20px 16px;
  flex-shrink: 0;
}

.sidebar-top {
  margin-bottom: 24px;
}

.back-link {
  border: none;
  background: none;
  color: #6b7aaa;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}

.back-link:hover { color: #3f5dff; }

.ai-profile {
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f2f8;
}

.ai-avatar {
  margin-bottom: 12px;
}

.avatar-circle {
  width: 72px; height: 72px;
  border-radius: 50%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  transition: box-shadow 0.3s;
}

.avatar-circle.active {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.avatar-circle.small {
  width: 34px; height: 34px;
  margin: 0;
  background: linear-gradient(135deg, #e8ecff, #dde4ff);
}

.ai-profile h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #1e2a4a;
  font-weight: 600;
}

.ai-desc {
  margin: 0 0 10px;
  font-size: 12px;
  color: #9aa3c0;
}

.status-line {
  font-size: 12px;
  color: #8e9ab8;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #ccc;
}

.status-dot.on {
  background: #34d399;
  animation: dotPulse 2s infinite;
}

@keyframes dotPulse {
  0%,100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.sidebar-actions {
  padding: 20px 0;
  border-bottom: 1px solid #f0f2f8;
}

.action-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid #3f5dff;
  background: #fff;
  color: #3f5dff;
  border-radius: 10px;
  padding: 10px 0;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #3f5dff;
  color: #fff;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
}

.sidebar-footer p {
  margin: 0 0 4px;
  font-size: 11px;
  color: #b4bed4;
}

/* ===== Main Chat ===== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.msg-area {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Welcome */
.welcome {
  margin: auto;
  text-align: center;
  max-width: 520px;
}

.welcome-title {
  font-size: 22px;
  color: #1e2a4a;
  font-weight: 600;
  margin: 0 0 8px;
}

.welcome-sub {
  font-size: 14px;
  color: #9aa3c0;
  margin: 0 0 24px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.chip {
  border: 1px solid #dde2f5;
  background: #fff;
  border-radius: 20px;
  padding: 8px 18px;
  font-size: 13px;
  color: #4a5088;
  cursor: pointer;
  transition: all 0.15s;
}

.chip:hover {
  border-color: #3f5dff;
  color: #3f5dff;
}

/* Messages */
.msg-wrapper {
  display: flex;
  gap: 12px;
  max-width: 720px;
}

.msg-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-wrapper.assistant {
  align-self: flex-start;
}

.msg-avatar {
  flex-shrink: 0;
}

.msg-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 100%;
}

.msg-bubble {
  padding: 12px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.msg-wrapper.user .msg-bubble {
  background: #3f5dff;
  color: #fff;
  border-bottom-right-radius: 6px;
}

.msg-wrapper.assistant .msg-bubble {
  background: #fff;
  color: #2e3856;
  border-bottom-left-radius: 6px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.system-msg {
  align-self: center;
  font-size: 12px;
  color: #8e9ab8;
  background: #f0f3fa;
  border-radius: 10px;
  padding: 6px 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
}

.system-icon { flex-shrink: 0; }

.msg-bubble.typing {
  padding: 12px 24px;
}

.typing-dots i {
  font-style: normal;
  animation: dotBounce 1.2s infinite;
  color: #b4bed4;
  font-size: 18px;
}

.typing-dots i:nth-child(2) { animation-delay: 0.2s; }
.typing-dots i:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotBounce {
  0%,80%,100% { opacity: 0.2; }
  40% { opacity: 1; }
}

.msg-text { white-space: pre-wrap; }

.replay-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  color: #3f5dff;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 0 0 4px;
}

/* ===== Medicine Recommend ===== */
.med-recommend {
  margin-top: 6px;
}

/* Prompt */
.med-prompt {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  color: #166534;
}

.med-prompt-icon {
  flex-shrink: 0;
}

.med-prompt-yes,
.med-prompt-no {
  border: none;
  border-radius: 6px;
  padding: 4px 14px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.med-prompt-yes {
  background: #22c55e;
  color: #fff;
}

.med-prompt-yes:hover { background: #16a34a; }

.med-prompt-no {
  background: #e5e7eb;
  color: #6b7280;
}

.med-prompt-no:hover { background: #d1d5db; }

/* Stacked summary cards */
.med-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.med-item-card {
  background: #fff;
  border: 1px solid #e8ecf8;
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 2px 10px rgba(63, 93, 255, 0.06);
  max-width: 300px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
}

.med-item-card:hover {
  box-shadow: 0 4px 18px rgba(63, 93, 255, 0.14);
  transform: translateY(-1px);
}

.med-item-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.med-item-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.c1 { background: #dce6ff; }
.c2 { background: #e9dcff; }
.c3 { background: #d9f6ff; }
.c4 { background: #e2ffe2; }
.c5 { background: #fff0d9; }

.med-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.med-item-name {
  font-weight: 600;
  color: #1e2a4a;
  font-size: 14px;
}

.med-item-meta {
  font-size: 12px;
  color: #8e9ab8;
}

.med-item-arrow {
  flex-shrink: 0;
}

/* ===== Medicine Detail Modal ===== */
.med-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.med-modal {
  background: #fff;
  border-radius: 18px;
  width: 380px;
  max-width: 92vw;
  max-height: 88vh;
  overflow-y: auto;
  padding: 28px 24px 22px;
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  animation: modalIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.med-modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #f0f2f8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.med-modal-close:hover {
  background: #e0e3f0;
}

.med-modal-title {
  margin: 0 0 18px;
  font-size: 18px;
  font-weight: 700;
  color: #1e2a4a;
  padding-right: 30px;
}

.med-modal-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.med-modal-section {
  background: #f8f9fd;
  border-radius: 10px;
  padding: 10px 14px;
}

.med-modal-section h4 {
  margin: 0 0 4px;
  font-size: 12px;
  color: #8e9ab8;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.med-modal-section p {
  margin: 0;
  font-size: 13px;
  color: #3a4a6e;
  line-height: 1.5;
}

.med-modal-qty-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.med-modal-qty {
  display: flex;
  align-items: center;
  gap: 10px;
}

.med-modal-qty-btn {
  width: 30px;
  height: 30px;
  border: 1px solid #dde2f5;
  border-radius: 8px;
  background: #fff;
  color: #3f5dff;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.med-modal-qty-btn:hover {
  background: #eef2ff;
  border-color: #3f5dff;
}

.med-modal-qty-num {
  min-width: 22px;
  text-align: center;
  font-weight: 700;
  color: #1e2a4a;
  font-size: 16px;
}

.med-modal-total {
  text-align: right;
}

.med-modal-total-label {
  display: block;
  font-size: 11px;
  color: #8e9ab8;
  margin-bottom: 2px;
}

.med-modal-total-price {
  font-size: 20px;
  font-weight: 700;
  color: #ff4d4f;
}

.med-modal-cart-btn {
  width: 100%;
  border: none;
  border-radius: 12px;
  background: #1e2a4a;
  color: #fff;
  padding: 13px 0;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.med-modal-cart-btn:hover {
  background: #2f3b5c;
}

.med-modal-cart-btn.added {
  background: #34d399;
}

/* Input */
.input-area {
  padding: 16px 24px 24px;
  background: #fff;
  border-top: 1px solid #eef0f5;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f6fb;
  border: 1px solid #e4e7f4;
  border-radius: 16px;
  padding: 4px 6px 4px 18px;
  transition: border-color 0.2s;
  max-width: 760px;
}

.input-wrapper:focus-within {
  border-color: #b5beff;
  background: #fff;
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #2e3856;
  padding: 8px 0;
}

.chat-input::placeholder { color: #b4bed4; }

.input-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.send-btn {
  width: 36px; height: 36px;
  border: none;
  border-radius: 10px;
  background: #3f5dff;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.send-btn:hover { background: #2f4de0; }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.mic-btn {
  width: 42px; height: 42px;
  border: none;
  border-radius: 50%;
  background: #f0f3fa;
  color: #8a93b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.mic-btn:hover { color: #3f5dff; background: #e8ecff; }

.mic-btn.recording {
  background: #3f5dff;
  color: #fff;
  box-shadow: 0 0 0 6px rgba(63, 93, 255, 0.25);
}

.mic-btn.disabled { opacity: 0.3; cursor: not-allowed; }

.input-hint {
  margin: 8px 0 0 18px;
  font-size: 12px;
  color: #ff4757;
}

.input-hint.busy {
  color: #3f5dff;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== Floating Cart ===== */
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

/* ===== Cart Drawer ===== */
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
</style>
