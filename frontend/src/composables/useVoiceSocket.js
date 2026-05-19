import { ref } from 'vue'
import { io } from 'socket.io-client'

const SOCKET_URL = 'http://127.0.0.1:5000'

export function useVoiceSocket() {
  const connected = ref(false)
  const connecting = ref(false)

  let socket = null
  let _aiSpeakingTimeout = null

  const _callbacks = {
    asr: null,
    aiText: null,
    aiAudio: null,
    aiDone: null,
    error: null,
  }

  function onASR(fn) { _callbacks.asr = fn }
  function onAIText(fn) { _callbacks.aiText = fn }
  function onAIAudio(fn) { _callbacks.aiAudio = fn }
  function onAIDone(fn) { _callbacks.aiDone = fn }
  function onError(fn) { _callbacks.error = fn }

  function connect() {
    return new Promise((resolve, reject) => {
      socket = io(SOCKET_URL, { transports: ['websocket', 'polling'] })

      socket.on('connect', () => {
        connected.value = true
        connecting.value = false
        socket.emit('voice_start')
        resolve()
      })

      socket.on('disconnect', () => {
        connected.value = false
        connecting.value = false
        _clearAiTimeout()
      })

      socket.on('voice_msg', (msg) => {
        switch (msg.type) {
          case 'asr':
            _callbacks.asr?.(msg.text)
            break
          case 'ai_text': {
            _callbacks.aiText?.(msg.delta)
            // Safety timeout: auto-reset after 30s if no ai_done
            if (_aiSpeakingTimeout) clearTimeout(_aiSpeakingTimeout)
            _aiSpeakingTimeout = setTimeout(() => {
              _callbacks.aiDone?.()
            }, 30000)
            break
          }
          case 'ai_audio':
            _callbacks.aiAudio?.(msg.data)
            break
          case 'ai_done':
            _clearAiTimeout()
            _callbacks.aiDone?.()
            break
        }
      })

      socket.on('connect_error', () => {
        connecting.value = false
        connected.value = false
        reject(new Error('连接失败'))
      })
    })
  }

  function disconnect() {
    _clearAiTimeout()
    if (socket) {
      socket.emit('voice_stop')
      socket.disconnect()
      socket = null
    }
    connected.value = false
    connecting.value = false
  }

  function sendAudio(base64, sampleRate) {
    if (socket?.connected) {
      socket.emit('voice_audio', { audio: base64, sampleRate })
    }
  }

  function _clearAiTimeout() {
    if (_aiSpeakingTimeout) {
      clearTimeout(_aiSpeakingTimeout)
      _aiSpeakingTimeout = null
    }
  }

  return { connected, connecting, connect, disconnect, sendAudio, onASR, onAIText, onAIAudio, onAIDone, onError }
}
