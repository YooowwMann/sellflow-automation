from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    size: Mapped[str | None] = mapped_column(String(40), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    condition: Mapped[str] = mapped_column(String(80), nullable=False, default="Preloved - Baik")
    defects: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)  # draft, active, archived, sold
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=True, onupdate=utc_now)

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.order"
    )
    listings: Mapped[list["Listing"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )
    ai_drafts: Mapped[list["AIContentDraft"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="AIContentDraft.id"
    )
    inventory_events: Mapped[list["InventoryEvent"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="InventoryEvent.created_at.desc()"
    )

class ProductImage(Base):
    __tablename__ = "product_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    product: Mapped[Product] = relationship(back_populates="images")

class AIContentDraft(Base):
    __tablename__ = "ai_content_drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(40), nullable=False)  # shopee, facebook, preloved
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    hashtags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="builtin", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=True, onupdate=utc_now)

    product: Mapped[Product] = relationship(back_populates="ai_drafts")

class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="not_published")  # not_published, draft_ready, manual_action_required, published
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=True, onupdate=utc_now)

    product: Mapped[Product] = relationship(back_populates="listings")

class InventoryEvent(Base):
    __tablename__ = "inventory_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)  # sold, restock, adjusted
    channel: Mapped[str | None] = mapped_column(String(40), nullable=True)  # shopee, facebook, preloved, offline, lainnya
    sold_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
    remaining_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    buyer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    product: Mapped[Product] = relationship(back_populates="inventory_events")

class PublishJob(Base):
    __tablename__ = "publish_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued")
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
