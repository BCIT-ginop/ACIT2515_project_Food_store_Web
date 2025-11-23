import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Float,
    DECIMAL,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import db
from typing import List, Optional


class Product(db.Model):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    price: Mapped[float] = mapped_column(Float)
    available: Mapped[int] = mapped_column(Integer, default=0)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="products")

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class Customer(db.Model):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    phone: Mapped[str] = mapped_column(unique=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="customer")


class Order(db.Model):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=db.func.now()
    )
    completed: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )
    amount: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2), nullable=True, default=None
    )

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def estimate(self):
        total = 0
        for i in self.order_items:
            total += i.product.price * i.quantity
        return total

    def complete(self):
        for i in self.order_items:
            if i.product.available < i.quantity:
                raise ValueError(
                    f"Not enough {i.product.name} in stock."
                    f"Need {i.quantity}, have {i.product.available}."
                )
        for i in self.order_items:
            i.product.available -= i.quantity

        self.completed = datetime.datetime.now()
        self.amount = self.estimate()


class OrderItem(db.Model):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    # id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)
    # order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    # product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))

    order: Mapped["Order"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    products: Mapped[List["Product"]] = relationship(back_populates="category")
