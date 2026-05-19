import { useVAD } from './useVAD.js'

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer)
  const chunks = []
  for (let i = 0; i < bytes.length; i += 8192) {
    chunks.push(String.fromCharCode(...bytes.slice(i, i + 8192)))
  }
  return btoa(chunks.join(''))
}

export function useMicCapture() {
  const vad = useVAD()
  let sendAudioFn = null

  async function start(opts = {}) {
    const { onSend, isPaused } = opts
    sendAudioFn = onSend || null

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        channelCount: 1,
        sampleRate: 16000,
      },
    })

    await vad.start(stream, {
      sampleRate: 16000,
      paused: isPaused || (() => false),
      onFrame: (int16) => {
        if (sendAudioFn) {
          sendAudioFn(arrayBufferToBase64(int16.buffer), 16000)
        }
      },
    })
  }

  function stop() {
    sendAudioFn = null
    vad.stop()
  }

  return { start, stop }
}
