from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Time, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# 👤 Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="user")
    todos = relationship("Todo", back_populates="user")


# 📦 Products
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)
    active = Column(Boolean, default=True)

    order_items = relationship("OrderItem", back_populates="product")


# 🧾 Orders
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


# 🧩 Order Items (bridge table)
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# 📋 Todos
class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    due_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    # FIX: Wrapped CURRENT_TIMESTAMP in text() to prevent MySQL syntax error
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # FIX: Wrapped CURRENT_TIMESTAMP in text()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="todos"
    )
