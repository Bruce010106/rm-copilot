"""Core business tables. All data is synthetic (see data/seed)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RelationshipManager(Base):
    __tablename__ = "relationship_managers"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    team: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16))  # rm | manager


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(8))
    birth_date: Mapped[date] = mapped_column(Date)
    city: Mapped[str] = mapped_column(String(32))
    occupation: Mapped[str] = mapped_column(String(64))
    tier: Mapped[str] = mapped_column(String(16))  # 普通 | 黄金 | 铂金 | 钻石
    risk_level: Mapped[str] = mapped_column(String(8))  # R1..R5
    aum: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    rm_id: Mapped[str] = mapped_column(ForeignKey("relationship_managers.id"), index=True)
    onboarded_at: Mapped[date] = mapped_column(Date)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    rm: Mapped[RelationshipManager] = relationship()
    holdings: Mapped[list["Holding"]] = relationship(back_populates="customer")
    interactions: Mapped[list["Interaction"]] = relationship(
        back_populates="customer", order_by="desc(Interaction.occurred_at)"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(16))  # 现金管理 | 固收 | 权益 | 另类 | 保险
    risk_level: Mapped[str] = mapped_column(String(8))


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    start_date: Mapped[date] = mapped_column(Date)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="holdings")
    product: Mapped[Product] = relationship()


class Interaction(Base):
    """A service record: call, IM chat, meeting, etc. Free text feeds summaries and KYC tags."""

    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    rm_id: Mapped[str] = mapped_column(ForeignKey("relationship_managers.id"))
    channel: Mapped[str] = mapped_column(String(16))  # 电话 | 企微 | 面谈 | 活动
    occurred_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    content: Mapped[str] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="interactions")
