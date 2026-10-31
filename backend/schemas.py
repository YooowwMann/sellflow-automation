from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    file_path: str
    file_name: str
    mime_type: str
    file_size: int
    is_primary: bool
    order: int
    created_at: datetime

class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    platform: str
    status: str
    external_url: str | None = None
    published_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

class ListingConfirmRequest(BaseModel):
    external_url: str | None = None
    notes: str | None = None

class PublishPackageOut(BaseModel):
    product_id: int
    product_name: str
    price: float
    platform: str
    platform_name: str
    destination_url: str
    listing_status: str
    external_url: str | None = None
    published_at: datetime | None = None
    instructions: list[str]
    draft_title: str
    draft_description: str
    draft_hashtags: str | None = None
    is_approved: bool
    photos: list[ProductImageOut]

class AIContentDraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    platform: str
    title: str
    description: str
    hashtags: str | None = None
    is_approved: bool
    tokens_used: int
    provider: str
    created_at: datetime
    updated_at: datetime | None = None

class AIDraftUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=5, max_length=15000)
    hashtags: str | None = Field(default=None, max_length=255)
    is_approved: bool | None = None

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    size: str | None = Field(default=None, max_length=40)
    price: float = Field(ge=0)
    condition: str = Field(default="Preloved - Baik", max_length=80)
    defects: str | None = Field(default=None, max_length=5000)
    stock: int = Field(default=1, ge=0)
    description: str = Field(default="", max_length=10000)
    status: str = Field(default="draft", max_length=30)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    brand: str | None = Field(default=None, max_length=80)
    size: str | None = Field(default=None, max_length=40)
    price: float | None = Field(default=None, ge=0)
    condition: str | None = Field(default=None, max_length=80)
    defects: str | None = Field(default=None, max_length=5000)
    stock: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=10000)
    status: str | None = Field(default=None, max_length=30)

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str | None = None
    brand: str | None = None
    size: str | None = None
    price: float
    condition: str
    defects: str | None = None
    stock: int
    description: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    images: list[ProductImageOut] = []
    listings: list[ListingOut] = []
    ai_drafts: list[AIContentDraftOut] = []

class ProductListResponse(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int

class MarkAsSoldRequest(BaseModel):
    channel: str = Field(min_length=2, max_length=40)
    sold_price: float = Field(ge=0)
    buyer_note: str | None = Field(default=None, max_length=2000)

class InventoryEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    product_name: str | None = None
    event_type: str
    channel: str | None = None
    sold_price: float | None = None
    quantity_change: int
    remaining_stock: int
    buyer_note: str | None = None
    created_at: datetime

class ChannelUnpublishItem(BaseModel):
    platform: str
    platform_name: str
    status: str
    external_url: str | None = None
    instruction: str

class UnpublishChecklistOut(BaseModel):
    product_id: int
    product_name: str
    sold_channel: str
    sold_price: float
    channels_to_unpublish: list[ChannelUnpublishItem]

class SalesHistorySummaryOut(BaseModel):
    total_sold_items: int
    total_revenue: float
    channel_breakdown: dict[str, int]
    recent_sales: list[InventoryEventOut]

class HealthOut(BaseModel):
    status: str
    app: str
    database: str
