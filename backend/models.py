from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Merchant(db.Model):
    __tablename__ = "merchants"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    spec = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    desc = db.Column(db.Text)
    usage = db.Column(db.Text)
    notice = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    on_sale = db.Column(db.Boolean, nullable=False, default=True)

    cart_items = db.relationship("CartItem", back_populates="medicine")
    order_items = db.relationship("OrderItem", back_populates="medicine")


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medicine_id = db.Column(db.BigInteger, db.ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selected = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", back_populates="cart_items")
    medicine = db.relationship("Medicine", back_populates="cart_items")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(40), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address = db.Column(db.String(255))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    medicine_id = db.Column(db.BigInteger, db.ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")
    medicine = db.relationship("Medicine", back_populates="order_items")
