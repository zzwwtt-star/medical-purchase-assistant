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
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { ollamaChatStream } from '../../api'

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

onBeforeUnmount(() => {
  stopAllAudio()
  if (recording.value) stopRecord()
  if (socket) {
    socket.emit('voice_chat_stop')
    socket.disconnect()
  }
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
</style>
