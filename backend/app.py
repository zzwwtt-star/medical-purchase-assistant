import logging

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import get_database_uri, load_env
from models import db
from routes import api
from utils import error_response
from voice_events import register_voice_events

socketio = SocketIO()


def create_app():
    load_env()
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")
    register_voice_events(socketio)

    # Preload medicine context at startup
    try:
        from voice_pipeline import _build_medicine_context

        _build_medicine_context()
    except Exception:
        pass

    # Preload Whisper + Ollama models in background (avoids first-request latency)
    try:
        from voice_pipeline import warmup_models

        warmup_models()
    except Exception:
        pass

    @app.get("/")
    def healthcheck():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(_):
        return error_response("not found", status=404)

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=False, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
