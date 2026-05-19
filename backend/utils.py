import hashlib
import uuid

from flask import jsonify


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return hash_password(raw_password) == hashed_password


def json_response(data=None, message="ok", code=0, status=200):
    payload = {"code": code, "message": message, "data": data}
    return jsonify(payload), status


def error_response(message="error", code=1, status=400):
    return json_response(data=None, message=message, code=code, status=status)


def generate_order_no():
    return uuid.uuid4().hex[:16]
