export function useAudioQueue() {
  let queue = []
  let blobUrls = []

  function play(base64Data) {
    const byteChars = atob(base64Data)
    const bytes = new Uint8Array(byteChars.length)
    for (let i = 0; i < byteChars.length; i++) bytes[i] = byteChars.charCodeAt(i)

    const blob = new Blob([bytes], { type: 'audio/mp3' })
    const url = URL.createObjectURL(blob)
    blobUrls.push(url)

    const audio = new Audio(url)
    audio.onended = () => {
      URL.revokeObjectURL(url)
      blobUrls = blobUrls.filter((u) => u !== url)
      _next()
    }
    audio.onerror = () => {
      URL.revokeObjectURL(url)
      blobUrls = blobUrls.filter((u) => u !== url)
      _next()
    }
    queue.push(audio)
    if (queue.length === 1) {
      audio.play().catch(() => _next())
    }
  }

  function _next() {
    queue.shift()
    if (queue.length > 0) {
      queue[0].play().catch(() => _next())
    }
  }

  function stopAll() {
    for (const a of queue) a.pause()
    queue = []
    for (const url of blobUrls) URL.revokeObjectURL(url)
    blobUrls = []
  }

  return { play, stopAll }
}
