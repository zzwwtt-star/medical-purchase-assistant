import json
from datetime import datetime, timedelta, timezone

from flask import Blueprint, Response, request, stream_with_context
from sqlalchemy import or_
from sqlalchemy.sql import func

from models import CartItem, Medicine, Merchant, Order, OrderItem, User, db
from utils import error_response, generate_order_no, hash_password, json_response, verify_password

api = Blueprint("api", __name__)

@api.post("/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    address = payload.get("address")

    if not username or not password:
        return error_response("username and password required")

    if User.query.filter_by(username=username).first():
        return error_response("username already exists")

    user = User(username=username, password=hash_password(password), address=address)
    db.session.add(user)
    db.session.commit()

    return json_response({"id": user.id, "username": user.username, "address": user.address})


@api.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return error_response("username and password required")

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return error_response("invalid username or password", status=401)

    return json_response({"id": user.id, "username": user.username, "address": user.address})


@api.get("/users/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("user not found", status=404)

    return json_response({"id": user.id, "username": user.username, "address": user.address})


@api.put("/users/<int:user_id>")
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("user not found", status=404)

    payload = request.get_json(silent=True) or {}
    address = payload.get("address")

    if address is not None:
        user.address = address

    db.session.commit()

    return json_response({"id": user.id, "username": user.username, "address": user.address})


@api.get("/medicines")
def list_medicines():
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    query = Medicine.query

    if category:
        like_category = f"%{category}%"
        query = query.filter(Medicine.category.like(like_category))

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Medicine.name.like(like),
                Medicine.desc.like(like),
                Medicine.symptoms.like(like),
                Medicine.category.like(like),
            )
        )

    items = query.order_by(Medicine.id.desc()).all()
    data = [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "price": float(item.price),
            "spec": item.spec,
            "manufacturer": item.manufacturer,
            "desc": item.desc,
            "usage": item.usage,
            "notice": item.notice,
            "symptoms": item.symptoms,
            "on_sale": item.on_sale,
        }
        for item in items
    ]

    return json_response(data)


@api.get("/medicines/<int:medicine_id>")
def medicine_detail(medicine_id):
    item = Medicine.query.get(medicine_id)
    if not item:
        return error_response("medicine not found", status=404)

    return json_response(
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "price": float(item.price),
            "spec": item.spec,
            "manufacturer": item.manufacturer,
            "desc": item.desc,
            "usage": item.usage,
            "notice": item.notice,
            "symptoms": item.symptoms,
            "on_sale": item.on_sale,
        }
    )


@api.get("/cart")
def cart_list():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return error_response("user_id required")

    items = (
        CartItem.query.filter_by(user_id=user_id)
        .join(Medicine, CartItem.medicine_id == Medicine.id)
        .all()
    )

    data = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "medicine_id": item.medicine_id,
            "quantity": item.quantity,
            "selected": item.selected,
            "medicine": {
                "name": item.medicine.name,
                "price": float(item.medicine.price),
                "spec": item.medicine.spec,
            },
        }
        for item in items
    ]

    return json_response(data)


@api.post("/cart")
def cart_add():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    medicine_id = payload.get("medicine_id")
    quantity = int(payload.get("quantity", 1))

    if not user_id or not medicine_id:
        return error_response("user_id and medicine_id required")

    if quantity <= 0:
        return error_response("quantity must be positive")

    item = CartItem.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, medicine_id=medicine_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return json_response({"id": item.id})


@api.put("/cart/<int:item_id>")
def cart_update(item_id):
    payload = request.get_json(silent=True) or {}
    quantity = payload.get("quantity")
    selected = payload.get("selected")

    item = CartItem.query.get(item_id)
    if not item:
        return error_response("cart item not found", status=404)

    if quantity is not None:
        quantity = int(quantity)
        if quantity <= 0:
            return error_response("quantity must be positive")
        item.quantity = quantity

    if selected is not None:
        item.selected = bool(selected)

    db.session.commit()
    return json_response({"id": item.id})


@api.delete("/cart/<int:item_id>")
def cart_remove(item_id):
    item = CartItem.query.get(item_id)
    if not item:
        return error_response("cart item not found", status=404)

    db.session.delete(item)
    db.session.commit()
    return json_response({"id": item.id})


@api.post("/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    address = payload.get("address")

    if not user_id:
        return error_response("user_id required")

    cart_items = (
        CartItem.query.filter_by(user_id=user_id, selected=True)
        .join(Medicine, CartItem.medicine_id == Medicine.id)
        .all()
    )
    if not cart_items:
        return error_response("no selected items")

    total = sum(item.quantity * float(item.medicine.price) for item in cart_items)
    order = Order(
        order_no=generate_order_no(),
        user_id=user_id,
        address=address,
        total=total,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            price=item.medicine.price,
        )
        db.session.add(order_item)
        db.session.delete(item)

    db.session.commit()
    return json_response({"order_id": order.id, "order_no": order.order_no})


@api.get("/orders")
def order_list():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return error_response("user_id required")

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.id.desc()).all()
    data = [
        {
            "id": order.id,
            "order_no": order.order_no,
            "total": float(order.total),
            "address": order.address,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]

    return json_response(data)


@api.get("/orders/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get(order_id)
    if not order:
        return error_response("order not found", status=404)

    data = {
        "id": order.id,
        "order_no": order.order_no,
        "total": float(order.total),
        "address": order.address,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "medicine_id": item.medicine_id,
                "quantity": item.quantity,
                "price": float(item.price),
                "medicine": {
                    "name": item.medicine.name,
                    "spec": item.medicine.spec,
                },
            }
            for item in order.items
        ],
    }

    return json_response(data)


@api.route("/orders/<int:order_id>", methods=["DELETE"])
def order_remove(order_id):
    order = Order.query.get(order_id)
    if not order:
        return error_response("order not found", status=404)

    OrderItem.query.filter_by(order_id=order_id).delete()
    db.session.delete(order)
    db.session.commit()
    return json_response({"id": order_id})


@api.post("/merchant/register")
def merchant_register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return error_response("username and password required")

    if Merchant.query.filter_by(username=username).first():
        return error_response("username already exists")

    merchant = Merchant(username=username, password=hash_password(password), name=username)
    db.session.add(merchant)
    db.session.commit()
    return json_response({"id": merchant.id, "username": merchant.username, "name": merchant.name})


@api.post("/merchant/login")
def merchant_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return error_response("username and password required")

    merchant = Merchant.query.filter_by(username=username).first()
    if not merchant or not verify_password(password, merchant.password):
        return error_response("invalid username or password", status=401)

    return json_response({"id": merchant.id, "username": merchant.username, "name": merchant.name})


@api.get("/merchant/overview")
def merchant_overview():
    today = datetime.now(timezone.utc).date()
    today_orders = Order.query.filter(func.date(Order.created_at) == today).count()
    today_revenue = (
        db.session.query(func.coalesce(func.sum(Order.total), 0))
        .filter(func.date(Order.created_at) == today)
        .scalar()
    )
    pending_orders = Order.query.filter_by(status="pending").count()
    shipped_orders = Order.query.filter_by(status="shipped").count()

    recent_orders = (
        db.session.query(func.date(Order.created_at), func.count(Order.id))
        .filter(Order.created_at >= datetime.now(timezone.utc) - timedelta(days=6))
        .group_by(func.date(Order.created_at))
        .all()
    )
    recent_map = {str(day): count for day, count in recent_orders}
    recent_trend = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        key = day.isoformat()
        recent_trend.append({"date": key, "count": int(recent_map.get(key, 0))})

    return json_response(
        {
            "todayOrders": today_orders,
            "todayRevenue": float(today_revenue or 0),
            "pendingOrders": pending_orders,
            "shippedOrders": shipped_orders,
            "recentOrders": recent_trend,
        }
    )


@api.get("/merchant/orders")
def merchant_orders():
    status = (request.args.get("status") or "").strip()
    query = Order.query
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).all()
    data = [
        {
            "id": order.id,
            "order_no": order.order_no,
            "total": float(order.total),
            "address": order.address,
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "user_name": order.user.username if order.user else "",
            "items": [
                {
                    "id": item.id,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "medicine": {
                        "name": item.medicine.name,
                        "spec": item.medicine.spec,
                    },
                }
                for item in order.items
            ],
        }
        for order in orders
    ]

    return json_response(data)


@api.get("/merchant/analytics")
def merchant_analytics():
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)
    order_counts = (
        db.session.query(func.date(Order.created_at), func.count(Order.id))
        .filter(Order.created_at >= start_date)
        .group_by(func.date(Order.created_at))
        .all()
    )

    counts_map = {item[0]: item[1] for item in order_counts}
    days = []
    counts = []
    for idx in range(7):
        day = start_date + timedelta(days=idx)
        days.append(day.strftime("%m-%d"))
        counts.append(int(counts_map.get(day, 0)))

    status_counts = (
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    status_map = {item[0]: int(item[1]) for item in status_counts}

    return json_response(
        {
            "recentDays": days,
            "orderCounts": counts,
            "statusBreakdown": {
                "pending": status_map.get("pending", 0),
                "shipped": status_map.get("shipped", 0),
            },
        }
    )


@api.put("/merchant/orders/<int:order_id>/status")
def merchant_order_status(order_id):
    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or "").strip()

    if status not in {"pending", "shipped"}:
        return error_response("invalid status")

    order = Order.query.get(order_id)
    if not order:
        return error_response("order not found", status=404)

    order.status = status
    db.session.commit()
    return json_response({"id": order.id, "status": order.status})


@api.get("/merchant/medicines")
def merchant_medicines():
    items = Medicine.query.order_by(Medicine.id.desc()).all()
    data = [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "price": float(item.price),
            "spec": item.spec,
            "manufacturer": item.manufacturer,
            "desc": item.desc,
            "usage": item.usage,
            "notice": item.notice,
            "symptoms": item.symptoms,
            "on_sale": item.on_sale,
        }
        for item in items
    ]

    return json_response(data)


@api.post("/merchant/medicines")
def merchant_create_medicine():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    price = payload.get("price", 0)
    category = payload.get("category")
    on_sale = bool(payload.get("on_sale", True))
    spec = payload.get("spec")
    manufacturer = payload.get("manufacturer")
    desc = payload.get("desc")
    usage = payload.get("usage")
    notice = payload.get("notice")
    symptoms = payload.get("symptoms")

    if not name:
        return error_response("name required")

    try:
        price = float(price)
    except (TypeError, ValueError):
        return error_response("invalid price")

    item = Medicine(
        name=name,
        price=price,
        category=category,
        on_sale=on_sale,
        spec=spec,
        manufacturer=manufacturer,
        desc=desc,
        usage=usage,
        notice=notice,
        symptoms=symptoms,
    )
    db.session.add(item)
    db.session.commit()

    return json_response({"id": item.id})


@api.put("/merchant/medicines/<int:medicine_id>")
def merchant_update_medicine(medicine_id):
    payload = request.get_json(silent=True) or {}
    item = Medicine.query.get(medicine_id)
    if not item:
        return error_response("medicine not found", status=404)

    for field in ["name", "category", "spec", "manufacturer", "desc", "usage", "notice", "symptoms"]:
        if field in payload:
            setattr(item, field, payload.get(field))

    if "price" in payload:
        try:
            item.price = float(payload.get("price"))
        except (TypeError, ValueError):
            return error_response("invalid price")

    if "on_sale" in payload:
        item.on_sale = bool(payload.get("on_sale"))

    db.session.commit()
    return json_response({"id": item.id})


@api.delete("/merchant/medicines/<int:medicine_id>")
def merchant_delete_medicine(medicine_id):
    item = Medicine.query.get(medicine_id)
    if not item:
        return error_response("medicine not found", status=404)

    db.session.delete(item)
    db.session.commit()
    return json_response({"id": medicine_id})


@api.post("/ollama/chat")
def ollama_chat():
    """Text chat using local Ollama model with SSE streaming."""
    from voice_pipeline import _ollama_chat_stream

    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    history = payload.get("messages") or []
    if not prompt:
        return error_response("prompt required")

    from voice_pipeline import _build_chat_system_prompt

    system_prompt = _build_chat_system_prompt(prompt)

    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        role = "assistant" if item.get("role") == "assistant" else "user"
        text = (item.get("text") or "").strip()
        if text:
            messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": prompt})

    def stream():
        import queue
        import threading

        from voice_pipeline import _generate_tts_audio, _ollama_chat_stream

        output_queue = queue.Queue()

        def process():
            all_text = ""
            pending = ""
            tts_queue = queue.Queue()

            def tts_worker():
                while True:
                    sentence = tts_queue.get()
                    if sentence is None:
                        break
                    b64 = _generate_tts_audio(sentence)
                    if b64:
                        output_queue.put(("audio", b64))

            tts_thread = threading.Thread(target=tts_worker, daemon=True)
            tts_thread.start()

            try:
                for chunk in _ollama_chat_stream(messages):
                    output_queue.put(("delta", chunk))
                    all_text += chunk
                    pending += chunk
                    while True:
                        earliest = -1
                        for sep in ["。", "！", "？", "\n"]:
                            pos = pending.find(sep)
                            if pos != -1 and (earliest == -1 or pos < earliest):
                                earliest = pos
                        if earliest == -1:
                            break
                        sentence = pending[:earliest + 1].strip()
                        pending = pending[earliest + 1:]
                        if sentence:
                            tts_queue.put(sentence)
            except Exception as exc:
                output_queue.put(("error", f"Ollama 请求失败: {exc}"))
                return
            finally:
                pending = pending.strip()
                if pending:
                    tts_queue.put(pending)
                tts_queue.put(None)
                tts_thread.join()
                output_queue.put(("done", None))

        threading.Thread(target=process, daemon=True).start()

        yield ": ready\n\n"
        while True:
            msg_type, data = output_queue.get()
            if msg_type == "delta":
                yield f"data: {json.dumps({'type': 'delta', 'content': data}, ensure_ascii=False)}\n\n"
            elif msg_type == "audio":
                yield f"data: {json.dumps({'type': 'ai_audio', 'data': data}, ensure_ascii=False)}\n\n"
            elif msg_type == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data}, ensure_ascii=False)}\n\n"
                break
            elif msg_type == "done":
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break

    response = Response(stream_with_context(stream()), mimetype="text/event-stream; charset=utf-8")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@api.get("/voice/health")
def voice_health():
    from voice_pipeline import _build_medicine_context

    ctx_available = False
    try:
        ctx = _build_medicine_context()
        ctx_available = bool(ctx)
    except Exception:
        pass

    # Quick Ollama connectivity test
    ollama_ok = False
    ollama_msg = ""
    try:
        r_test = __import__("requests").get("http://localhost:11434/api/tags", timeout=5)
        if r_test.ok:
            models = [m.get("name", "") for m in r_test.json().get("models", [])]
            ollama_ok = any("qwen" in m.lower() for m in models)
            ollama_msg = f"found models: {', '.join(models[:3])}" if models else "no models"
        else:
            ollama_msg = f"ollama returned {r_test.status_code}"
    except Exception as e:
        ollama_msg = str(e)

    return json_response({
        "medicine_context_ready": ctx_available,
        "ollama_ok": ollama_ok,
        "ollama_msg": ollama_msg,
        "version": "2026-05-17-fix2",
    })


@api.get("/voice/test-chat")
def voice_test_chat():
    """Directly test the Ollama chat pipeline and return full response."""
    from voice_pipeline import _ollama_chat_stream

    text = (request.args.get("text") or "你好").strip()
    messages = [{"role": "user", "content": text}]

    try:
        chunks = []
        for delta in _ollama_chat_stream(messages):
            chunks.append(delta)
        full_text = "".join(chunks)
        return json_response({
            "input": text,
            "response": full_text,
            "chunks": len(chunks),
        })
    except Exception as e:
        return error_response(f"Ollama chat test failed: {e}")
