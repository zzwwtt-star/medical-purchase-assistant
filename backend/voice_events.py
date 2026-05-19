import logging

from flask import request
from flask_socketio import SocketIO, emit

from voice_pipeline import ChatSession, VoiceSession

LOGGER = logging.getLogger("voice_events")

voice_sessions = {}
chat_sessions = {}


def register_voice_events(socketio: SocketIO):

    @socketio.on("connect")
    def on_connect():
        LOGGER.info("socket connected: %s", request.sid)

    # ---- Voice Call (continuous real-time) ----
    @socketio.on("voice_start")
    def on_voice_start():
        sid = request.sid
        if sid in voice_sessions:
            voice_sessions[sid].close()
        session = VoiceSession(sid, socketio.emit)
        voice_sessions[sid] = session
        LOGGER.info("voice session started: %s", sid)

    @socketio.on("voice_audio")
    def on_voice_audio(data):
        sid = request.sid
        session = voice_sessions.get(sid)
        if session:
            try:
                session.feed_audio(data["audio"])
            except Exception as exc:
                LOGGER.error("voice %s: audio feed error: %s", sid, exc)

    @socketio.on("voice_stop")
    def on_voice_stop():
        sid = request.sid
        session = voice_sessions.pop(sid, None)
        if session:
            session.close()
            LOGGER.info("voice session stopped: %s", sid)

    # ---- Text Chat (text input → AI text + TTS output) ----
    @socketio.on("text_chat_start")
    def on_text_chat_start():
        sid = request.sid
        if sid in chat_sessions:
            chat_sessions[sid].close()
        session = ChatSession(sid, socketio.emit, event_prefix="text_chat")
        chat_sessions[sid] = session
        LOGGER.info("text chat session started: %s", sid)

    @socketio.on("text_chat_message")
    def on_text_chat_message(data):
        sid = request.sid
        session = chat_sessions.get(sid)
        if session:
            try:
                session.feed_text(data.get("text", ""))
            except Exception as exc:
                LOGGER.error("text_chat %s: feed error: %s", sid, exc)

    @socketio.on("text_chat_stop")
    def on_text_chat_stop():
        sid = request.sid
        session = chat_sessions.pop(sid, None)
        if session:
            session.close()
            LOGGER.info("text chat session stopped: %s", sid)

    # ---- Voice Record (press-to-talk → ASR → AI text + TTS output) ----
    @socketio.on("voice_record_start")
    def on_voice_record_start():
        sid = request.sid
        if sid in chat_sessions:
            chat_sessions[sid].close()
        session = ChatSession(sid, socketio.emit, event_prefix="voice_record")
        chat_sessions[sid] = session
        LOGGER.info("voice record session started: %s", sid)

    @socketio.on("voice_record_audio")
    def on_voice_record_audio(data):
        sid = request.sid
        session = chat_sessions.get(sid)
        if session:
            try:
                session.feed_audio(data.get("audio", ""), sample_rate=data.get("sampleRate", 16000))
            except Exception as exc:
                LOGGER.error("voice_record %s: audio error: %s", sid, exc)

    @socketio.on("voice_record_stop")
    def on_voice_record_stop():
        sid = request.sid
        session = chat_sessions.pop(sid, None)
        if session:
            session.close()
            LOGGER.info("voice record session stopped: %s", sid)

    # ---- Unified Voice Chat (text + voice input on same page) ----
    @socketio.on("voice_chat_start")
    def on_voice_chat_start():
        sid = request.sid
        if sid in chat_sessions:
            chat_sessions[sid].close()
        session = ChatSession(sid, socketio.emit, event_prefix="voice_chat")
        chat_sessions[sid] = session
        LOGGER.info("voice_chat session started: %s", sid)


    @socketio.on("voice_chat_text")
    def on_voice_chat_text(data):
        sid = request.sid
        session = chat_sessions.get(sid)
        if session:
            try:
                session.feed_text(data.get("text", ""))
            except Exception as exc:
                LOGGER.error("voice_chat %s: text error: %s", sid, exc)

    @socketio.on("voice_chat_audio")
    def on_voice_chat_audio(data):
        sid = request.sid
        session = chat_sessions.get(sid)
        if session:
            try:
                session.feed_audio(data.get("audio", ""), sample_rate=data.get("sampleRate", 16000))
            except Exception as exc:
                LOGGER.error("voice_chat %s: audio error: %s", sid, exc)

    @socketio.on("voice_chat_stop")
    def on_voice_chat_stop():
        sid = request.sid
        session = chat_sessions.pop(sid, None)
        if session:
            session.close()
            LOGGER.info("voice_chat session stopped: %s", sid)

    @socketio.on("disconnect")
    def on_disconnect():
        sid = request.sid
        for sessions_map in (voice_sessions, chat_sessions):
            session = sessions_map.pop(sid, None)
            if session:
                session.close()
        LOGGER.info("socket cleaned up: %s", sid)
