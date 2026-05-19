<template>
  <div class="voice-page">
    <div class="voice-container">
      <div class="status-area">
        <div class="call-status" :class="{ active: connected }">
          <div class="status-dot"></div>
          <span>{{ statusText }}</span>
        </div>
        <button class="back-btn" @click="goHome">返回首页</button>
      </div>

      <div class="main-call-area">
        <div class="avatar-ring" :class="{ ringing: connected, speaking: aiSpeaking }">
          <div class="avatar-icon">🤖</div>
        </div>

        <div v-if="connected" class="live-text">
          <div v-if="userText" class="user-speech">{{ userText }}</div>
          <div v-if="aiText" class="ai-speech">{{ aiText }}</div>
          <div v-if="!userText && !aiText" class="hint">请说出你的症状...</div>
        </div>
        <div v-else class="ready-text">
          <p>AI 语音购药助手</p>
          <p class="sub">点击通话按钮开始实时语音对话</p>
        </div>
      </div>

      <div class="call-btn-area">
        <button
          class="call-btn"
          :class="{ active: connected, connecting: connecting }"
          :disabled="connecting"
          @click="toggleCall"
        >
          <svg v-if="!connected" viewBox="0 0 24 24" width="36" height="36">
            <path
              d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z"
              fill="currentColor"
            />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="36" height="36">
            <path
              d="M12 2a10 10 0 00-9.95 9h19.9A10 10 0 0012 2zM2.05 13a10 10 0 0019.9 0h-19.9z"
              fill="currentColor"
            />
            <line x1="12" y1="2" x2="12" y2="22" stroke="currentColor" stroke-width="2" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAudioQueue } from '../../composables/useAudioQueue.js'
import { useMicCapture } from '../../composables/useMicCapture.js'
import { useVoiceSocket } from '../../composables/useVoiceSocket.js'

const router = useRouter()
const goHome = () => router.push('/')

// ---- Composables ----
const audioQueue = useAudioQueue()
const mic = useMicCapture()
const socket = useVoiceSocket()

// ---- UI state ----
const { connected, connecting } = socket
const aiSpeaking = ref(false)
const userText = ref('')
const aiText = ref('')

const statusText = computed(() => {
  if (connecting.value) return '连接中...'
  if (!connected.value) return '准备就绪'
  if (aiSpeaking.value) return 'AI 回复中...'
  return '通话中'
})

// ---- Wire socket events → UI ----
socket.onASR((text) => {
  userText.value = text
  aiText.value = ''
  audioQueue.stopAll()
})

socket.onAIText((delta) => {
  aiSpeaking.value = true
  aiText.value += delta
})

socket.onAIAudio((data) => {
  audioQueue.play(data)
})

socket.onAIDone(() => {
  aiSpeaking.value = false
})

// ---- Call control ----
async function startCall() {
  connecting.value = true

  try {
    await socket.connect()
  } catch {
    connecting.value = false
    alert('无法连接到语音服务，请确认后端已启动。')
    return
  }

  try {
    await mic.start({
      onSend: (base64, sampleRate) => socket.sendAudio(base64, sampleRate),
      isPaused: () => aiSpeaking.value,
    })
  } catch (err) {
    stopCall()
    if (err.name === 'NotAllowedError') {
      alert('请允许麦克风权限后重试。')
    } else {
      alert('麦克风启动失败: ' + (err.message || '未知错误'))
    }
  }
}

function stopCall() {
  audioQueue.stopAll()
  socket.disconnect()
  mic.stop()
  aiSpeaking.value = false
  userText.value = ''
  aiText.value = ''
}

function toggleCall() {
  if (connected.value) {
    stopCall()
  } else {
    startCall()
  }
}

onBeforeUnmount(() => {
  stopCall()
})
</script>

<style scoped>
.voice-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f0f4ff 0%, #e8eeff 100%);
}

.voice-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 20px;
}

.status-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.call-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7b89a9;
  font-size: 14px;
}

.call-status.active {
  color: #3f5dff;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c4cddf;
}

.call-status.active .status-dot {
  background: #3f5dff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.back-btn {
  border: none;
  background: rgba(63, 93, 255, 0.08);
  color: #3f5dff;
  border-radius: 8px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 13px;
}

.main-call-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.avatar-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: #e8ecff;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #d4dbff;
  transition: all 0.4s ease;
}

.avatar-ring.ringing {
  border-color: #3f5dff;
  box-shadow: 0 0 32px rgba(63, 93, 255, 0.25);
}

.avatar-ring.speaking {
  border-color: #ff7033;
  box-shadow: 0 0 32px rgba(255, 112, 51, 0.3);
  animation: speak-pulse 0.6s infinite alternate;
}

@keyframes speak-pulse {
  from { transform: scale(1); }
  to { transform: scale(1.06); }
}

.avatar-icon {
  font-size: 64px;
  line-height: 1;
}

.live-text {
  text-align: center;
  max-width: 360px;
  min-height: 80px;
}

.user-speech {
  background: #e8efff;
  border-radius: 14px;
  padding: 12px 16px;
  margin-bottom: 8px;
  color: #2f3f65;
  font-size: 15px;
  text-align: left;
  animation: fadeIn 0.3s ease;
}

.ai-speech {
  background: #fff7f0;
  border-radius: 14px;
  padding: 12px 16px;
  color: #634b2e;
  font-size: 15px;
  text-align: left;
  animation: fadeIn 0.3s ease;
}

.hint {
  color: #b4bed4;
  font-size: 14px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.ready-text {
  text-align: center;
}

.ready-text p {
  margin: 0 0 6px;
  color: #2f4270;
  font-size: 20px;
  font-weight: 600;
}

.ready-text .sub {
  font-size: 14px;
  color: #8e9ab8;
  font-weight: 400;
}

.call-btn-area {
  margin-top: 16px;
}

.call-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: #3f5dff;
  color: #fff;
  box-shadow: 0 8px 32px rgba(63, 93, 255, 0.4);
}

.call-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 36px rgba(63, 93, 255, 0.5);
}

.call-btn.active {
  background: #ff4757;
  box-shadow: 0 8px 32px rgba(255, 71, 87, 0.4);
}

.call-btn.connecting {
  opacity: 0.6;
  pointer-events: none;
}

.call-btn svg {
  width: 36px;
  height: 36px;
  fill: currentColor;
}
</style>
