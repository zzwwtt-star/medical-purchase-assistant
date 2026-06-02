import asyncio
import base64
import json
import logging
import os
import queue
import tempfile
import threading
import time

import edge_tts
import numpy as np
import requests

LOGGER = logging.getLogger("voice")

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# Preload CUDA DLLs from Ollama so ctranslate2 can find them
_ollama_cuda = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\lib\ollama\cuda_v12")
if os.path.isdir(_ollama_cuda):
    import ctypes

    try:
        ctypes.CDLL(os.path.join(_ollama_cuda, "cublas64_12.dll"))
        LOGGER.info("Preloaded CUDA DLLs from %s", _ollama_cuda)
    except Exception as exc:
        LOGGER.warning("Failed to preload CUDA DLLs: %s", exc)

_whisper_model = None
_whisper_lock = threading.Lock()

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    with _whisper_lock:
        if _whisper_model is not None:
            return _whisper_model
        from faster_whisper import WhisperModel

        _whisper_model = WhisperModel("medium", device="cuda", compute_type="float16")
        LOGGER.info("Whisper model loaded: medium (cuda, float16)")
    return _whisper_model


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _resample_to_16k(audio: np.ndarray, orig_rate: int) -> np.ndarray:
    """Resample audio to 16kHz using linear interpolation."""
    if orig_rate == 16000:
        return audio
    if orig_rate <= 0:
        return audio
    ratio = 16000.0 / orig_rate
    n_out = int(len(audio) * ratio)
    if n_out < 1600:  # minimum 0.1s
        return audio
    indices = np.arange(n_out, dtype=np.float64) / ratio
    lo = np.floor(indices).astype(np.int64)
    hi = np.minimum(lo + 1, len(audio) - 1)
    frac = (indices - lo).astype(np.float32)
    return (audio[lo] * (1.0 - frac) + audio[hi] * frac).astype(np.float32)


_medicine_context_cache = ""
_medicine_list_cache = None  # raw list of dicts for dynamic matching
_medicine_app = None


def _get_medicine_app():
    global _medicine_app
    if _medicine_app is not None:
        return _medicine_app
    from flask import Flask

    from config import get_database_uri

    _medicine_app = Flask(__name__)
    _medicine_app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    _medicine_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    from models import db

    db.init_app(_medicine_app)
    return _medicine_app


def _get_medicine_list():
    """Return cached list of medicine dicts for dynamic matching."""
    global _medicine_list_cache
    if _medicine_list_cache is not None:
        return _medicine_list_cache
    try:
        from models import Medicine

        app = _get_medicine_app()
        with app.app_context():
            items = Medicine.query.filter_by(on_sale=True).order_by(Medicine.id.desc()).all()
            _medicine_list_cache = [
                {
                    "id": item.id,
                    "name": item.name,
                    "category": (item.category or "").strip(),
                    "symptoms": (item.symptoms or "").strip(),
                    "desc": (item.desc or "").strip(),
                    "usage": (item.usage or "").strip(),
                    "notice": (item.notice or "").strip(),
                    "price": float(item.price),
                }
                for item in items
            ]
            LOGGER.info("voice: medicine list cached, %d entries", len(_medicine_list_cache))
            return _medicine_list_cache
    except Exception as exc:
        LOGGER.warning("voice: failed to load medicine list: %s", exc)
        return []


SYMPTOM_SYNONYMS = {
    '发烧': '发热', '退烧': '发热', '拉肚子': '腹泻', '肚子疼': '腹痛',
    '胃痛': '腹痛', '消化不良': '腹胀', '打喷嚏': '流涕', '鼻涕': '流涕',
    '咳痰': '痰多', '嗓子疼': '咽痛', '咽喉痛': '咽痛', '过敏性鼻炎': '鼻炎',
    '皮肤痒': '瘙痒', '眼睛红': '结膜炎', '睡不着': '失眠', '没精神': '乏力',
}


def _normalize_symptom(text: str) -> str:
    """Map colloquial terms to standardized symptom keywords."""
    t = text.strip()
    for k, v in SYMPTOM_SYNONYMS.items():
        t = t.replace(k, v)
    return t


def _match_medicines(user_text: str, max_items: int = 5):
    """Match relevant medicines from user input via keyword/substring search."""
    if not user_text or not user_text.strip():
        return ""
    medicines = _get_medicine_list()
    if not medicines:
        return ""

    # Normalize colloquial terms
    normalized = _normalize_symptom(user_text)

    # Build 2-gram tokens for substring matching
    tokens = set()
    for text in (user_text, normalized):
        for i in range(len(text)):
            if i + 1 < len(text):
                tokens.add(text[i:i + 2])
        tokens.add(text)

    scored = []
    for m in medicines:
        score = 0
        symptoms = m.get('symptoms', '')
        category = m.get('category', '')
        name = m.get('name', '')
        desc = m.get('desc', '')

        for token in tokens:
            if token in symptoms or token in category:
                score += 10
            elif token in name:
                score += 5
            elif token in desc:
                score += 2

        if score > 0:
            scored.append((score, m))

    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_items]

    lines = ["【药品数据库 — 以下为匹配到的相关药品】"]
    for _, m in top:
        parts = [f"名称:{m['name']}"]
        if m["symptoms"]:
            parts.append(f"主治:{m['symptoms']}")
        if m["usage"]:
            parts.append(f"用法:{m['usage']}")
        if m["notice"]:
            parts.append(f"注意:{m['notice']}")
        parts.append(f"价格:¥{m['price']:.2f}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _build_medicine_context():
    global _medicine_context_cache
    if _medicine_context_cache:
        return _medicine_context_cache
    medicines = _get_medicine_list()
    if not medicines:
        return ""
    lines = ["【药品数据库 — 以下为本站全部在售药品，推荐时只能从中选择】"]
    for m in medicines:
        parts = [f"名称:{m['name']}"]
        if m["symptoms"]:
            parts.append(f"主治:{m['symptoms']}")
        if m["usage"]:
            parts.append(f"用法:{m['usage']}")
        if m["notice"]:
            parts.append(f"注意:{m['notice']}")
        parts.append(f"价格:¥{m['price']:.2f}")
        lines.append(" | ".join(parts))
    _medicine_context_cache = "\n".join(lines)
    LOGGER.info("voice: medicine context built, %d entries", len(lines) - 1)
    return _medicine_context_cache


def warmup_models():
    """Preload Whisper + Ollama in background threads so first request isn't slow."""

    def _warmup_whisper():
        try:
            LOGGER.info("warmup: loading Whisper model...")
            _get_whisper_model()
            LOGGER.info("warmup: Whisper model ready")
        except Exception as exc:
            LOGGER.warning("warmup: Whisper failed (%s)", exc)

    def _warmup_ollama():
        try:
            LOGGER.info("warmup: pinging Ollama to load %s...", OLLAMA_MODEL)
            resp = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": "你好"}],
                    "stream": False,
                    "options": {"num_predict": 1},
                },
                timeout=120,
            )
            if resp.ok:
                LOGGER.info("warmup: Ollama model ready")
            else:
                LOGGER.warning("warmup: Ollama returned %s", resp.status_code)
        except Exception as exc:
            LOGGER.warning("warmup: Ollama not available (%s)", exc)

    threading.Thread(target=_warmup_whisper, daemon=True).start()
    threading.Thread(target=_warmup_ollama, daemon=True).start()


def _build_chat_system_prompt(user_text: str = ""):
    """Unified system prompt for text-based AI chats, with dynamic medicine matching."""
    ctx = _match_medicines(user_text) if user_text else _build_medicine_context()
    return (
        "你是医疗购药助手。必须严格遵守以下规则：\n"
        "1. 用自然对话的方式回复，像医生朋友一样说话，不要用固定的格式模板。\n"
        "2. 药品推荐必须优先从上方药品数据库中挑选，给出名称、用法和注意事项，但不要提及编号或价格。\n"
        "3. 只有在数据库中确实没有任何对症药品时，才可以说\"暂无完全匹配的药品\"，并建议用户就医或咨询药师。\n"
        "4. 严禁编造任何药品名称、功效、用法。不能推荐数据库中没有的药品。\n"
        "5. 先简短询问症状关键信息（持续多久、具体部位、有无其他症状），信息足够后再推荐。\n"
        "6. 症状严重或不确定时，优先建议就医。\n"
        "7. 每次回复控制在1-3句话，语气温和专业。\n"
        "\n" + ctx
    )


def _build_agent_system_prompt(user_text: str = ""):
    """System prompt for text-chat agent, with medicine recommendation marker."""
    ctx = _match_medicines(user_text) if user_text else _build_medicine_context()
    return (
        "你是医疗购药助手。必须严格遵守以下规则：\n"
        "1. 用自然对话的方式回复，像医生朋友一样说话，不要用固定的格式模板。\n"
        "2. 推荐药品时只说药名和针对的症状，一句话带过即可。\n"
        "   例如：\"你可以试试布洛芬，退热效果不错。\"\n"
        "3. 绝对不要输出药品的用法用量、注意事项、禁忌人群、价格等详细信息。\n"
        "   系统会自动弹出卡片展示这些内容。\n"
        "4. 只有在数据库中确实没有任何对症药品时，才说\"暂无完全匹配的药品\"。\n"
        "5. 严禁编造任何药品名称、功效、用法。不能推荐数据库中没有的药品。\n"
        "6. 先简短询问症状关键信息（持续多久、具体部位、有无其他症状），信息足够后再推荐。\n"
        "7. 症状严重或不确定时，优先建议就医。\n"
        "8. 每次回复控制在1-3句话，语气温和专业。\n"
        "\n" + ctx
    )


def _extract_recommendations(text: str):
    """Detect medicine recommendations from LLM response automatically.

    In a pharmacy assistant context, mentioning a medicine name is itself
    a recommendation. Only skip when the mention is clearly negative.
    """
    medicines = _get_medicine_list()
    if not medicines:
        return []

    negation_words = ['不能', '不建议', '不推荐', '禁用', '慎用', '不要用', '避免', '不可']

    def _name_matches(med_name, chat_text):
        """Check if a medicine name (or its core part) appears in the chat text."""
        if med_name in chat_text:
            return chat_text.find(med_name)
        # Try stripping common suffixes to get the core name
        suffixes = ['胶囊', '片', '颗粒', '口服液', '注射液', '滴眼液', '软膏',
                    '栓', '糖浆', '冲剂', '丸', '口服溶液', '混悬液', '喷雾剂']
        core = med_name
        for sfx in suffixes:
            if core.endswith(sfx):
                core = core[:-len(sfx)]
                break
        if len(core) >= 2 and core in chat_text:
            return chat_text.find(core)
        # Try 3-gram sliding window from med_name against chat_text
        for i in range(len(med_name) - 2):
            chunk = med_name[i:i + 3]
            if chunk in chat_text:
                return chat_text.find(chunk)
        return -1

    results = []
    seen = set()
    for m in medicines:
        if m['id'] in seen:
            continue
        if not m['name']:
            continue
        idx = _name_matches(m['name'], text)
        if idx >= 0:
            context = text[max(0, idx - 15):idx]
            negated = any(nw in context for nw in negation_words)
            if not negated:
                results.append(_med_to_card(m))
                seen.add(m['id'])

    LOGGER.info("extract_recommendations: found_meds=%d, text_len=%d", len(results), len(text))
    return results[:3]


def _med_to_card(m: dict) -> dict:
    return {
        'id': m['id'],
        'name': m['name'],
        'price': m['price'],
        'desc': m.get('desc', ''),
        'symptoms': m.get('symptoms', ''),
        'usage': m.get('usage', ''),
        'notice': m.get('notice', ''),
    }


def _generate_tts_audio(text: str) -> str | None:
    """Generate TTS audio for a sentence, return base64-encoded MP3 data."""
    tts_text = text[:200]
    if not tts_text:
        return None
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        _run_async(
            edge_tts.Communicate(text=tts_text, voice="zh-CN-XiaoxiaoNeural").save(tmp.name)
        )
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as exc:
        LOGGER.error("TTS generation failed: %s", exc)
        return None
    finally:
        if tmp:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass


class VoiceSession:

    def __init__(self, sid: str, emit_fn):
        self.sid = sid
        self.emit_fn = emit_fn
        self.audio_buffer = bytearray()
        self.messages = [{"role": "system", "content": self._build_system_prompt()}]
        self.ai_speaking = False
        self.running = True
        self.lock = threading.Lock()
        self.session_version = 0
        self._asr_busy = False
        self._silence_timer = None  # triggers ASR after silence
        self._last_audio_time = 0

    def _emit(self, event, data):
        self.emit_fn(event, data, to=self.sid)

    def _build_system_prompt(self, user_text: str = ""):
        ctx = _match_medicines(user_text) if user_text else _build_medicine_context()
        return (
            "你是智能语音购药助手，通过语音与用户对话。\n"
            "规则：\n"
            "1. 用中文回答，控制在1-3句话，总长不超过60字。\n"
            "2. 用自然口语化的方式说话，像医生朋友聊天一样，不要用固定格式。\n"
            "3. 先简短询问关键症状细节（时长、部位、伴随症状）。\n"
            "4. 信息足够时，从下方药品数据库中推荐具体药品，说出药名和用法，但不要提编号或价格。\n"
            "5. 数据库中确实无对症药品时，建议就医，不要编造药品。\n"
            "6. 不要输出编号、价格、markdown、列表或emoji。\n"
            "\n" + ctx
        )

    def feed_audio(self, audio_b64: str):
        if not self.running:
            return
        try:
            chunk = base64.b64decode(audio_b64)
        except Exception:
            return

        with self.lock:
            if self.ai_speaking:
                return
            self.audio_buffer.extend(chunk)
            self._last_audio_time = time.time()
            if self._asr_busy:
                return
            self._reset_silence_timer_locked()
            self._maybe_start_asr()

    def _reset_silence_timer_locked(self):
        """Must hold self.lock."""
        if self._silence_timer:
            self._silence_timer.cancel()
        self._silence_timer = threading.Timer(1.5, self._on_silence_timeout)
        self._silence_timer.daemon = True
        self._silence_timer.start()

    def _on_silence_timeout(self):
        """Silence timeout: if there's buffered audio, trigger ASR."""
        with self.lock:
            if not self.running or self._asr_busy or self.ai_speaking:
                return
            if len(self.audio_buffer) < 2000:  # < ~62ms — nothing meaningful
                return
            # Enough buffered audio accumulated during silence, trigger ASR
            self._trigger_asr_locked()

    def _maybe_start_asr(self):
        """Start ASR if enough audio is buffered. Must hold self.lock."""
        # 80000 samples = 5s at 16kHz — safety valve for long utterances
        # Normal trigger is the silence timer at 1.5s
        n_samples = len(self.audio_buffer) // 2
        min_samples = 80000  # 5s
        if n_samples >= min_samples:
            self._trigger_asr_locked()

    def _trigger_asr_locked(self):
        """Must hold self.lock. Send current buffer to ASR thread."""
        audio_bytes = bytes(self.audio_buffer)
        if len(audio_bytes) < 2000:
            return
        # Cancel silence timer while ASR runs
        if self._silence_timer:
            self._silence_timer.cancel()
            self._silence_timer = None
        # Keep last 1.0s as overlap to avoid splitting words across chunks
        overlap_samples = 16000
        overlap_bytes = bytes(self.audio_buffer[-overlap_samples * 2:])
        self.audio_buffer = bytearray(overlap_bytes)
        self._asr_busy = True
        LOGGER.info("voice %s: ASR triggered, samples=%d", self.sid, len(audio_bytes) // 2)
        threading.Thread(target=self._process_audio, args=(audio_bytes, 16000), daemon=True).start()

    def _process_audio(self, audio_bytes: bytes, sample_rate: int = 16000):
        try:
            text = self._run_asr(audio_bytes, sample_rate)
            if not text:
                return

            self._emit("voice_msg", {"type": "asr", "text": text})
            self._handle_user_speech(text)
        finally:
            with self.lock:
                self._asr_busy = False
                # If more audio piled up while ASR was busy, process it now
                if not self.ai_speaking:
                    self._maybe_start_asr()
                    # Restart silence timer if buffer has pending audio
                    if not self._asr_busy and len(self.audio_buffer) > 2000:
                        self._reset_silence_timer_locked()

    def _run_asr(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        try:
            audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Resample to 16kHz if needed
            if sample_rate != 16000 and sample_rate > 0:
                audio = _resample_to_16k(audio, sample_rate)
                LOGGER.info("voice %s: resampled from %dHz to 16kHz", self.sid, sample_rate)

            # --- Conservative energy trim: only remove obvious silence ---
            frame_len = 320  # 20ms at 16kHz
            n_frames = len(audio) // frame_len
            if n_frames < 10:
                return ""

            frame_rms = np.array([
                float(np.sqrt(np.mean(np.square(audio[i * frame_len:(i + 1) * frame_len]))))
                for i in range(n_frames)
            ])

            # Estimate noise floor from the quietest 20% of frames
            sorted_rms = np.sort(frame_rms)
            n_quiet = max(1, n_frames // 5)
            noise_floor = float(np.mean(sorted_rms[:n_quiet]))
            # Very lenient threshold: 2x noise floor, loose clamps
            threshold = max(0.0008, min(0.03, noise_floor * 2.0))

            speech = frame_rms > threshold
            n_speech = int(np.sum(speech))

            if n_speech < 3:
                LOGGER.info("voice %s: energy trim rejected, n_speech=%d, threshold=%.6f, max_rms=%.6f",
                            self.sid, n_speech, threshold, float(np.max(frame_rms)))
                return ""

            idx = np.where(speech)[0]
            pad = 20  # 400ms padding for soft beginnings/endings
            start = max(0, idx[0] - pad)
            end = min(n_frames, idx[-1] + pad + 1)
            audio = audio[start * frame_len:end * frame_len]

            if len(audio) < 12000:  # 0.75s minimum
                return ""
            # -------------------------------------------------

            segments, info = _get_whisper_model().transcribe(
                audio,
                language="zh",
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.4,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=200,
                ),
                beam_size=5,
                best_of=5,
                condition_on_previous_text=False,
                temperature=0,
            )
            seg_list = list(segments)
            text = "".join(seg.text for seg in seg_list).strip()

            # Only reject if Whisper is highly confident it's non-speech
            if seg_list and hasattr(seg_list[0], 'no_speech_prob'):
                if all(seg.no_speech_prob > 0.9 for seg in seg_list):
                    return ""

            # Filter known hallucination patterns
            noise_patterns = [
                "字幕", "索兰娅", "by", "By", "BY",
                "谢谢观看", "感谢", "谢谢", "再见",
                "嗯", "啊", "哦", "呃", "喔", "嘘",
                "咚咚", "叮", "嘣", "嘀", "哗",
            ]
            cleaned = text
            for w in noise_patterns:
                cleaned = cleaned.replace(w, "")
            cleaned = cleaned.strip()
            cleaned = "".join(ch for ch in cleaned if ch not in ".。，,!！?？")

            if len(cleaned) < 2:
                return ""
            LOGGER.info("voice %s: ASR = %s", self.sid, cleaned)
            return cleaned
        except Exception as exc:
            LOGGER.error("voice %s: ASR failed: %s", self.sid, exc)
            return ""

    def _handle_user_speech(self, text: str):
        with self.lock:
            self.session_version += 1
            version = self.session_version
            self.ai_speaking = True
            self.audio_buffer = bytearray()

            # Dynamic medicine context based on latest user input
            self.messages[0] = {"role": "system", "content": self._build_system_prompt(text)}
            self.messages.append({"role": "user", "content": text})
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-9:]

        threading.Thread(target=self._run_ai_response, args=(version,), daemon=True).start()

    def _run_ai_response(self, version: int):
        if self.session_version != version:
            return

        LOGGER.info("voice %s: AI response started, version=%d", self.sid, version)

        all_text = ""
        pending = ""  # Text not yet sent to TTS
        aborted = False

        # Sequential TTS queue: one worker processes sentences in order
        tts_queue = queue.Queue()

        def _tts_worker():
            while True:
                sentence = tts_queue.get()
                if sentence is None:
                    break
                self._generate_tts(sentence)

        threading.Thread(target=_tts_worker, daemon=True).start()

        def _emit_sentences(text):
            nonlocal pending
            pending += text
            while True:
                earliest = -1
                earliest_sep = ""
                for sep in ["。", "！", "？", "\n"]:
                    pos = pending.find(sep)
                    if pos != -1 and (earliest == -1 or pos < earliest):
                        earliest = pos
                        earliest_sep = sep
                if earliest == -1:
                    break
                sentence = pending[:earliest + 1].strip()
                pending = pending[earliest + 1:]
                if sentence:
                    tts_queue.put(sentence)

        try:
            for delta in _ollama_chat_stream(self.messages):
                if self.session_version != version:
                    aborted = True
                    break
                all_text += delta
                self._emit("voice_msg", {"type": "ai_text", "delta": delta})
                _emit_sentences(delta)
        except Exception as exc:
            LOGGER.error("voice %s: Ollama failed: %s", self.sid, exc)
            fallback = "抱歉，我暂时无法回复，请稍后再试。"
            self._emit("voice_msg", {"type": "ai_text", "delta": fallback})
            all_text = fallback
        finally:
            if aborted:
                tts_queue.put(None)
                with self.lock:
                    self.ai_speaking = False
                return

        # Flush remaining pending text and signal TTS worker to finish
        pending = pending.strip()
        if pending and self.session_version == version:
            tts_queue.put(pending)
        tts_queue.put(None)

        if all_text and self.session_version == version:
            self.messages.append({"role": "assistant", "content": all_text})
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-9:]

        if self.session_version == version:
            self._emit("voice_msg", {"type": "ai_done"})
            with self.lock:
                self.ai_speaking = False

    def _generate_tts(self, text: str):
        b64 = _generate_tts_audio(text)
        if b64:
            self._emit("voice_msg", {"type": "ai_audio", "data": b64})
            LOGGER.info("voice %s: TTS sent, %d chars", self.sid, len(b64))

    def close(self):
        self.running = False
        self.session_version += 999
        if self._silence_timer:
            self._silence_timer.cancel()
            self._silence_timer = None


class ChatSession:
    """Unified chat session for text-chat and voice-record modes, sharing AI + TTS pipeline."""

    def __init__(self, sid: str, emit_fn, event_prefix: str):
        self.sid = sid
        self.emit_fn = emit_fn
        self.event_prefix = event_prefix  # "voice_chat" / "text_chat" / "voice_record"
        self.messages = [{"role": "system", "content": self._build_system_prompt()}]
        self.running = True
        self.lock = threading.Lock()
        self.session_version = 0
        self.ai_busy = False

    def _emit(self, event, data):
        """Thread-safe emit that always routes to this client's sid."""
        self.emit_fn(event, data, to=self.sid)

    def _build_system_prompt(self, user_text: str = ""):
        ctx = _match_medicines(user_text) if user_text else _build_medicine_context()
        return (
            "你是智能语音购药助手，通过语音与用户对话。\n"
            "规则：\n"
            "1. 用中文回答，控制在1-3句话，总长不超过60字。\n"
            "2. 用自然口语化的方式说话，像医生朋友聊天一样，不要用固定格式。\n"
            "3. 先简短询问关键症状细节（时长、部位、伴随症状）。\n"
            "4. 信息足够时，从下方药品数据库中推荐具体药品，说出药名和用法，但不要提编号或价格。\n"
            "5. 数据库中确实无对症药品时，建议就医，不要编造药品。\n"
            "6. 不要输出编号、价格、markdown、列表或emoji。\n"
            "\n" + ctx
        )

    def feed_text(self, text: str):
        if not self.running:
            return
        text = text.strip()
        if not text:
            return
        with self.lock:
            if self.ai_busy:
                self._emit(f"{self.event_prefix}_msg", {"type": "system_msg", "text": "我正在回复上一条，请稍候..."})
                return
            self.ai_busy = True
            self.session_version += 1
            version = self.session_version
            self.messages[0] = {"role": "system", "content": self._build_system_prompt(text)}
            self.messages.append({"role": "user", "content": text})
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-9:]

        # Echo back what the user said
        self._emit(f"{self.event_prefix}_msg", {"type": "user_text", "text": text})
        threading.Thread(target=self._run_ai_response, args=(version,), daemon=True).start()

    def feed_audio(self, audio_b64: str, sample_rate: int = 16000):
        if not self.running:
            return
        try:
            chunk = base64.b64decode(audio_b64)
        except Exception:
            return

        with self.lock:
            if self.ai_busy:
                self._emit(f"{self.event_prefix}_msg", {"type": "system_msg", "text": "我正在回复，请稍候再录音..."})
                return
            self.ai_busy = True
            self.session_version += 1
            version = self.session_version

        threading.Thread(target=self._process_audio, args=(chunk, version, sample_rate), daemon=True).start()

    def _process_audio(self, audio_bytes: bytes, version: int, sample_rate: int = 16000):
        try:
            text = self._run_asr(audio_bytes, sample_rate)
            if not text or self.session_version != version:
                with self.lock:
                    self.ai_busy = False
                return

            self._emit(f"{self.event_prefix}_msg", {"type": "asr", "text": text})

            with self.lock:
                if self.session_version != version:
                    self.ai_busy = False
                    return
                self.messages[0] = {"role": "system", "content": self._build_system_prompt(text)}
                self.messages.append({"role": "user", "content": text})
                if len(self.messages) > 10:
                    self.messages = [self.messages[0]] + self.messages[-9:]

            self._run_ai_response(version)
        except Exception as exc:
            LOGGER.error("chat %s: audio process error: %s", self.sid, exc)
            with self.lock:
                self.ai_busy = False

    def _run_asr(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        try:
            audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Resample to 16kHz if needed
            if sample_rate != 16000 and sample_rate > 0:
                audio = _resample_to_16k(audio, sample_rate)
                LOGGER.info("chat %s: resampled from %dHz to 16kHz", self.sid, sample_rate)

            frame_len = 320
            n_frames = len(audio) // frame_len
            if n_frames < 10:
                return ""

            frame_rms = np.array([
                float(np.sqrt(np.mean(np.square(audio[i * frame_len:(i + 1) * frame_len]))))
                for i in range(n_frames)
            ])

            sorted_rms = np.sort(frame_rms)
            n_quiet = max(1, n_frames // 5)
            noise_floor = float(np.mean(sorted_rms[:n_quiet]))
            threshold = max(0.0008, min(0.03, noise_floor * 2.0))

            speech = frame_rms > threshold
            n_speech = int(np.sum(speech))
            if n_speech < 3:
                LOGGER.info("chat %s: energy trim rejected, n_speech=%d, threshold=%.6f, max_rms=%.6f",
                            self.sid, n_speech, threshold, float(np.max(frame_rms)))
                return ""

            idx = np.where(speech)[0]
            pad = 20
            start = max(0, idx[0] - pad)
            end = min(n_frames, idx[-1] + pad + 1)
            audio = audio[start * frame_len:end * frame_len]

            if len(audio) < 12000:
                return ""

            segments, info = _get_whisper_model().transcribe(
                audio,
                language="zh",
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.4,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=200,
                ),
                beam_size=5,
                best_of=5,
                condition_on_previous_text=False,
                temperature=0,
            )
            seg_list = list(segments)
            text = "".join(seg.text for seg in seg_list).strip()

            if seg_list and hasattr(seg_list[0], 'no_speech_prob'):
                if all(seg.no_speech_prob > 0.9 for seg in seg_list):
                    return ""

            noise_patterns = [
                "字幕", "索兰娅", "by", "By", "BY",
                "谢谢观看", "感谢", "谢谢", "再见",
                "嗯", "啊", "哦", "呃", "喔", "嘘",
                "咚咚", "叮", "嘣", "嘀", "哗",
            ]
            cleaned = text
            for w in noise_patterns:
                cleaned = cleaned.replace(w, "")
            cleaned = cleaned.strip()
            cleaned = "".join(ch for ch in cleaned if ch not in ".。，,!！?？")

            if len(cleaned) < 2:
                return ""
            LOGGER.info("chat %s: ASR = %s", self.sid, cleaned)
            return cleaned
        except Exception as exc:
            LOGGER.error("chat %s: ASR failed: %s", self.sid, exc)
            return ""

    def _run_ai_response(self, version: int):
        if self.session_version != version:
            with self.lock:
                self.ai_busy = False
            return

        LOGGER.info("chat %s: AI response started, version=%d", self.sid, version)

        all_text = ""
        pending = ""
        aborted = False

        # Sequential TTS queue: one worker processes sentences in order
        tts_queue = queue.Queue()

        def _tts_worker():
            while True:
                sentence = tts_queue.get()
                if sentence is None:
                    break
                self._generate_tts(sentence)

        threading.Thread(target=_tts_worker, daemon=True).start()

        def _clear_busy():
            with self.lock:
                self.ai_busy = False

        # Safety: force clear ai_busy after 120s no matter what
        safety_timer = threading.Timer(120, _clear_busy)
        safety_timer.daemon = True
        safety_timer.start()

        def _emit_sentences(text):
            nonlocal pending
            pending += text
            while True:
                earliest = -1
                earliest_sep = ""
                for sep in ["。", "！", "？", "\n"]:
                    pos = pending.find(sep)
                    if pos != -1 and (earliest == -1 or pos < earliest):
                        earliest = pos
                        earliest_sep = sep
                if earliest == -1:
                    break
                sentence = pending[:earliest + 1].strip()
                pending = pending[earliest + 1:]
                if sentence:
                    tts_queue.put(sentence)

        chunk_count = 0
        try:
            for delta in _ollama_chat_stream(self.messages):
                if self.session_version != version:
                    aborted = True
                    break
                all_text += delta
                chunk_count += 1
                self._emit(f"{self.event_prefix}_msg", {"type": "ai_text", "delta": delta})
                _emit_sentences(delta)
            LOGGER.info("chat %s: AI stream ended, %d chars, %d chunks", self.sid, len(all_text), chunk_count)
        except Exception as exc:
            LOGGER.error("chat %s: AI failed: %s", self.sid, exc)
            fallback = "抱歉，我暂时无法回复，请稍后再试。"
            self._emit(f"{self.event_prefix}_msg", {"type": "ai_text", "delta": fallback})
            all_text = fallback
        finally:
            safety_timer.cancel()
            if aborted:
                LOGGER.info("chat %s: AI response aborted (version mismatch)", self.sid)
                tts_queue.put(None)
                with self.lock:
                    self.ai_busy = False
                return

        # Flush remaining pending text and signal TTS worker to finish
        pending = pending.strip()
        if pending and self.session_version == version:
            tts_queue.put(pending)
        tts_queue.put(None)

        if all_text and self.session_version == version:
            self.messages.append({"role": "assistant", "content": all_text})
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-9:]

        if self.session_version == version:
            self._emit(f"{self.event_prefix}_msg", {"type": "ai_done"})
            with self.lock:
                self.ai_busy = False
            LOGGER.info("chat %s: AI response complete", self.sid)

    def _generate_tts(self, text: str):
        b64 = _generate_tts_audio(text)
        if b64:
            self._emit(f"{self.event_prefix}_msg", {"type": "ai_audio", "data": b64})
            LOGGER.info("chat %s: TTS sent, %d chars", self.sid, len(b64))

    def close(self):
        self.running = False
        self.session_version += 999


def _ollama_chat_stream(messages):
    resp = None
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": True,
                "options": {"temperature": 0.7, "num_predict": 128},
            },
            stream=True,
            timeout=(10, 120),
        )
        resp.raise_for_status()

        deadline = time.time() + 120
        for line in resp.iter_lines(decode_unicode=True):
            if time.time() > deadline:
                LOGGER.warning("Ollama stream deadline exceeded")
                break
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = data.get("message", {}).get("content", "")
            if content:
                yield content
            if data.get("done"):
                break
    except requests.ConnectionError:
        raise RuntimeError("Ollama 未启动，请先运行 ollama serve 并下载 qwen2.5:3b 模型")
    except Exception:
        raise RuntimeError("AI 服务异常，请确认 Ollama 已安装并运行")
    finally:
        if resp is not None:
            try:
                resp.close()
            except Exception:
                pass
