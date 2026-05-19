const VAD_FRAME_MS = 30
const NOISE_CALIB_FRAMES = 30     // ~0.9s calibration
const SPEECH_HANGOVER_FRAMES = 20 // ~600ms hangover

function rmsOf(frame) {
  let sum = 0
  for (let i = 0; i < frame.length; i++) sum += frame[i] * frame[i]
  return Math.sqrt(sum / frame.length)
}

export function useVAD() {
  let audioCtx = null
  let processor = null
  let micStream = null
  let micTrack = null

  // VAD state
  let noiseFloor = 0.001
  let noiseFloorSettled = false
  let noiseCalibFrames = 0
  let noiseCalibMin = Infinity
  let speechHangover = 0
  let ringBuf = new Float32Array(0)
  let vadFrameSamples = 480

  let onSpeechFrame = null
  let isPaused = null

  async function start(stream, opts = {}) {
    const { sampleRate = 16000, onFrame, paused } = opts
    onSpeechFrame = onFrame || null
    isPaused = paused || (() => false)

    micStream = stream
    micTrack = stream.getAudioTracks()[0]
    if (micTrack) {
      try { micTrack.applyConstraints({ sampleRate }) } catch (_) { /* best effort */ }
    }

    // Reset VAD state
    noiseFloor = 0.001
    noiseFloorSettled = false
    noiseCalibFrames = 0
    noiseCalibMin = Infinity
    speechHangover = 0
    ringBuf = new Float32Array(0)

    audioCtx = new AudioContext({ sampleRate })
    await audioCtx.resume()
    vadFrameSamples = Math.round((VAD_FRAME_MS / 1000) * audioCtx.sampleRate)

    const source = audioCtx.createMediaStreamSource(micStream)
    processor = audioCtx.createScriptProcessor(2048, 1, 1)

    processor.onaudioprocess = (e) => {
      if (isPaused()) return

      const input = e.inputBuffer.getChannelData(0)
      const newBuf = new Float32Array(ringBuf.length + input.length)
      newBuf.set(ringBuf)
      newBuf.set(input, ringBuf.length)
      ringBuf = newBuf

      while (ringBuf.length >= vadFrameSamples) {
        const frame = ringBuf.slice(0, vadFrameSamples)
        ringBuf = ringBuf.slice(vadFrameSamples)

        // Float32 → Int16
        const int16 = new Int16Array(frame.length)
        for (let i = 0; i < frame.length; i++) {
          const s = Math.max(-1, Math.min(1, frame[i]))
          int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff
        }

        const energy = rmsOf(frame)

        // Calibrate noise floor
        if (!noiseFloorSettled) {
          noiseCalibFrames++
          if (energy > 1e-6) noiseCalibMin = Math.min(noiseCalibMin, energy)
          if (noiseCalibFrames >= NOISE_CALIB_FRAMES) {
            noiseFloorSettled = true
            noiseFloor = Math.max(noiseCalibMin * 1.5, 0.0003)
            noiseFloor = Math.min(noiseFloor, 0.005)
          }
          if (noiseCalibFrames % 3 === 0) onSpeechFrame?.(int16)
          continue
        }

        // Adaptive threshold
        const threshold = Math.max(0.0015, Math.min(0.02, noiseFloor * 2.5))
        let isSpeech = false

        if (energy > threshold) {
          isSpeech = true
          speechHangover = SPEECH_HANGOVER_FRAMES
        } else if (speechHangover > 0) {
          speechHangover--
          isSpeech = true
        }

        if (isSpeech) onSpeechFrame?.(int16)
        // Silence: send nothing — backend timer triggers ASR
      }
    }

    source.connect(processor)
    processor.connect(audioCtx.destination)
  }

  function stop() {
    if (processor) {
      processor.disconnect()
      processor = null
    }
    if (audioCtx) {
      audioCtx.close()
      audioCtx = null
    }
    if (micStream) {
      micStream.getTracks().forEach((t) => t.stop())
      micStream = null
      micTrack = null
    }
    onSpeechFrame = null
    isPaused = null
  }

  return { start, stop }
}
