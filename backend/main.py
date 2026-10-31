from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, Form, File, UploadFile, Query, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from backend.config import settings
from backend.database import Base, engine, get_db, SessionLocal
from backend.models import Product, ProductImage, AIContentDraft, Listing, InventoryEvent
from backend.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductImageOut,
    AIContentDraftOut,
    AIDraftUpdate,
    ListingOut,
    ListingConfirmRequest,
    PublishPackageOut,
    MarkAsSoldRequest,
    InventoryEventOut,
    UnpublishChecklistOut,
    ChannelUnpublishItem,
    SalesHistorySummaryOut,
    HealthOut
)
from backend.auth import (
    authenticate_user,
    require_login,
    ensure_initial_admin,
    check_login_rate_limit,
    record_login_failure,
    clear_login_failures,
)
from backend.storage import save_upload_image, delete_stored_image, UPLOAD_DIR
from backend.ai_service import generate_product_copy

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Buat direktori upload jika belum ada
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Buat tabel jika belum ada (development fallback)
    Base.metadata.create_all(bind=engine)
    # Pastikan admin default terdaftar dengan password hash Argon2id
    with SessionLocal() as db:
        ensure_initial_admin(db)
    yield

app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)

# Proteksi CSRF berbasis W3C Fetch Metadata (Sec-Fetch-Site)
class FetchMetadataCSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            sec_fetch_site = request.headers.get("sec-fetch-site")
            if sec_fetch_site == "cross-site":
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Cross-site request forgery ditolak."}
                )
        return await call_next(request)

app.add_middleware(FetchMetadataCSRFMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="sellflow_session",
    same_site="lax",
    https_only=settings.session_https_only,
    max_age=60 * 60 * 12,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

@app.get("/api/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "app": settings.app_name,
        "database": db_status
    }

@app.get("/api/session")
def session_status(request: Request):
    return {
        "authenticated": bool(request.session.get("authenticated")),
        "username": request.session.get("username"),
        "ai_provider": settings.ai_provider,
        "ai_model": settings.ai_model
    }

@app.post("/api/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{username}"
    check_login_rate_limit(rate_key)

    user = authenticate_user(db, username, password)
    if not user:
        record_login_failure(rate_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah."
        )

    clear_login_failures(rate_key)
    request.session.clear()
    request.session["authenticated"] = True
    request.session["username"] = user.username
    request.session["user_id"] = user.id
    return {"ok": True}

@app.post("/api/logout")
def logout(request: Request, _: None = Depends(require_login)):
    request.session.clear()
    return {"ok": True}

@app.get("/api/dashboard")
def dashboard(_: None = Depends(require_login), db: Session = Depends(get_db)):
    total = db.query(Product).count()
    active = db.query(Product).filter(Product.status == "active").count()
    drafts = db.query(Product).filter(Product.status == "draft").count()
    return {
        "total_products": total,
        "active_products": active,
        "draft_products": drafts,
        "platforms": [
            {"name": "Shopee", "state": "Belum dihubungkan"},
            {"name": "Facebook Group", "state": "Konfirmasi manual"},
            {"name": "Preloved", "state": "Belum dihubungkan"}
        ]
    }

# ==================== PRODUCT CRUD ENDPOINTS ====================

@app.get("/api/products", response_model=list[ProductOut])
def list_products(
    status: str | None = Query(None, description="Filter status (draft, active, archived, sold)"),
    category: str | None = Query(None, description="Filter kategori produk"),
    search: str | None = Query(None, description="Pencarian nama atau brand"),
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if status:
        query = query.filter(Product.status == status)
    if category:
        query = query.filter(Product.category == category)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Product.brand.ilike(search_filter),
                Product.description.ilike(search_filter)
            )
        )
    return query.order_by(Product.created_at.desc()).all()

@app.post("/api/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")
    return product

@app.patch("/api/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@app.delete("/api/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    # Hapus file foto dari disk fisik
    for img in product.images:
        delete_stored_image(img.file_path)

    db.delete(product)
    db.commit()
    return {"ok": True, "message": f"Produk #{product_id} berhasil dihapus."}

# ==================== PRODUCT IMAGE MANAGEMENT ====================

@app.post("/api/products/{product_id}/images", response_model=list[ProductImageOut], status_code=status.HTTP_201_CREATED)
async def upload_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    current_image_count = len(product.images)
    max_images = 10
    if current_image_count + len(files) > max_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maksimal {max_images} foto per produk. Saat ini sudah ada {current_image_count} foto."
        )

    has_primary = any(img.is_primary for img in product.images)
    uploaded_images: list[ProductImage] = []

    for idx, file in enumerate(files):
        relative_path, original_name, mime_type, file_size = await save_upload_image(file)
        is_primary = False
        if not has_primary and idx == 0:
            is_primary = True
            has_primary = True

        new_image = ProductImage(
            product_id=product.id,
            file_path=relative_path,
            file_name=original_name,
            mime_type=mime_type,
            file_size=file_size,
            is_primary=is_primary,
            order=current_image_count + idx
        )
        db.add(new_image)
        uploaded_images.append(new_image)

    db.commit()
    for img in uploaded_images:
        db.refresh(img)
    return uploaded_images

@app.delete("/api/products/{product_id}/images/{image_id}", status_code=status.HTTP_200_OK)
def delete_product_image(
    product_id: int,
    image_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto tidak ditemukan.")

    was_primary = image.is_primary
    file_path = image.file_path
    db.delete(image)
    db.commit()

    delete_stored_image(file_path)

    if was_primary:
        remaining = db.query(ProductImage).filter(ProductImage.product_id == product_id).order_by(ProductImage.order.asc()).first()
        if remaining:
            remaining.is_primary = True
            db.commit()

    return {"ok": True, "message": "Foto berhasil dihapus."}

@app.patch("/api/products/{product_id}/images/{image_id}/primary", status_code=status.HTTP_200_OK)
def set_primary_image(
    product_id: int,
    image_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    target = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto tidak ditemukan.")

    db.query(ProductImage).filter(ProductImage.product_id == product_id).update({"is_primary": False})
    target.is_primary = True
    db.commit()
    return {"ok": True, "message": "Foto utama berhasil diatur."}

# ==================== AI LISTING GENERATOR ====================

@app.post("/api/products/{product_id}/ai/generate", response_model=list[AIContentDraftOut], status_code=status.HTTP_201_CREATED)
async def generate_ai_listing(
    product_id: int,
    platform: str = Query("all", description="Target: shopee, facebook, preloved, or all"),
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    targets = ["shopee", "facebook", "preloved"] if platform == "all" else [platform.lower()]
    drafts_result: list[AIContentDraft] = []

    for target in targets:
        content = await generate_product_copy(product, target)
        draft = db.query(AIContentDraft).filter(
            AIContentDraft.product_id == product.id,
            AIContentDraft.platform == target
        ).first()

        if draft:
            draft.title = content.title
            draft.description = content.description
            draft.hashtags = content.hashtags
            draft.tokens_used = content.tokens_used
            draft.provider = content.provider
            draft.is_approved = False  # Reset persetujuan karena baru di-generate ulang
        else:
            draft = AIContentDraft(
                product_id=product.id,
                platform=target,
                title=content.title,
                description=content.description,
                hashtags=content.hashtags,
                tokens_used=content.tokens_used,
                provider=content.provider,
                is_approved=False
            )
            db.add(draft)

        drafts_result.append(draft)

    db.commit()
    for d in drafts_result:
        db.refresh(d)
    return drafts_result

@app.get("/api/products/{product_id}/ai/drafts", response_model=list[AIContentDraftOut])
def get_ai_drafts(
    product_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")
    return db.query(AIContentDraft).filter(AIContentDraft.product_id == product_id).all()

@app.patch("/api/products/{product_id}/ai/drafts/{draft_id}", response_model=AIContentDraftOut)
def update_ai_draft(
    product_id: int,
    draft_id: int,
    payload: AIDraftUpdate,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    draft = db.query(AIContentDraft).filter(
        AIContentDraft.id == draft_id,
        AIContentDraft.product_id == product_id
    ).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft AI tidak ditemukan.")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(draft, field, val)

    db.commit()
    db.refresh(draft)
    return draft

@app.post("/api/products/{product_id}/ai/drafts/{draft_id}/approve", response_model=AIContentDraftOut)
def approve_ai_draft(
    product_id: int,
    draft_id: int,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    draft = db.query(AIContentDraft).filter(
        AIContentDraft.id == draft_id,
        AIContentDraft.product_id == product_id
    ).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft AI tidak ditemukan.")

    draft.is_approved = True
    db.commit()
    db.refresh(draft)
    return draft

# ==================== PUBLISHING & ASSISTED POSTING ====================

PLATFORM_DESTINATIONS = {
    "shopee": "https://seller.shopee.co.id/portal/product/new",
    "facebook": "https://www.facebook.com/groups/",
    "preloved": "https://preloved.co.id"
}

PLATFORM_NAMES = {
    "shopee": "Shopee Seller Center",
    "facebook": "Facebook Groups (Komunitas)",
    "preloved": "Aplikasi Preloved"
}

PLATFORM_INSTRUCTIONS = {
    "shopee": [
        "Pastikan akun Shopee Seller Anda telah login di browser.",
        "Klik tombol 'Buka Seller Center ↗' untuk membuka form tambah produk Shopee.",
        "Unggah foto produk yang telah disiapkan dari SellFlow.",
        "Salin Judul SEO Listing dan tempelkan ke kolom Nama Produk Shopee.",
        "Salin Deskripsi Lengkap dan tempelkan ke kolom Deskripsi Produk.",
        "Atur harga, kategori, dan jasa kirim sesuai data produk.",
        "Simpan produk di Shopee, lalu salin tautan produk dan tekan 'Konfirmasi Sudah Terbit'."
    ],
    "facebook": [
        "Buka grup jual beli Facebook tujuan melalui tombol 'Buka Facebook Group ↗'.",
        "Klik 'Tulis Sesuatu...' atau 'Jual Sesuatu'.",
        "Unggah foto-foto produk preloved Anda.",
        "Salin Teks Lengkap (format WTS ramah komunitas) lalu tempel ke postingan grup.",
        "Pastikan harga dan kondisi minus telah tercantum secara transparan.",
        "Publikasikan postingan di grup Facebook.",
        "Salin tautan postingan Facebook Anda dan tekan 'Konfirmasi Sudah Terbit' di bawah."
    ],
    "preloved": [
        "Buka aplikasi / website Preloved tempat Anda berjualan.",
        "Buat listing barang baru dan unggah foto produk.",
        "Salin judul dan deskripsi yang menonjolkan kondisi preloved serta catatan minus.",
        "Terbitkan barang di aplikasi Preloved.",
        "Konfirmasi di SellFlow agar status katalog terpusat Anda sinkron."
    ]
}

def get_or_create_listing(db: Session, product_id: int, platform: str) -> Listing:
    listing = db.query(Listing).filter(
        Listing.product_id == product_id,
        Listing.platform == platform
    ).first()
    if not listing:
        initial_status = "manual_action_required" if platform == "facebook" else "not_published"
        listing = Listing(
            product_id=product_id,
            platform=platform,
            status=initial_status
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)
    return listing

@app.get("/api/publications", response_model=list[ProductOut])
def list_publications(
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    # Pastikan listing untuk 3 platform ada untuk setiap produk
    for p in products:
        existing_platforms = {l.platform for l in p.listings}
        for plat in ["shopee", "facebook", "preloved"]:
            if plat not in existing_platforms:
                get_or_create_listing(db, p.id, plat)
        db.refresh(p)
    return products

@app.get("/api/products/{product_id}/publish-package/{platform}", response_model=PublishPackageOut)
async def get_publish_package(
    product_id: int,
    platform: str,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    plat_key = platform.lower()
    if plat_key not in PLATFORM_DESTINATIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' tidak didukung. Pilih shopee, facebook, atau preloved."
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    listing = get_or_create_listing(db, product.id, plat_key)

    # Ambil draft AI
    draft = db.query(AIContentDraft).filter(
        AIContentDraft.product_id == product.id,
        AIContentDraft.platform == plat_key
    ).first()

    if not draft:
        # Jika belum ada draft, generate langsung
        generated = await generate_product_copy(product, plat_key)
        draft = AIContentDraft(
            product_id=product.id,
            platform=plat_key,
            title=generated.title,
            description=generated.description,
            hashtags=generated.hashtags,
            tokens_used=generated.tokens_used,
            provider=generated.provider,
            is_approved=False
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

    return PublishPackageOut(
        product_id=product.id,
        product_name=product.name,
        price=float(product.price),
        platform=plat_key,
        platform_name=PLATFORM_NAMES.get(plat_key, plat_key),
        destination_url=PLATFORM_DESTINATIONS.get(plat_key, "#"),
        listing_status=listing.status,
        external_url=listing.external_url,
        published_at=listing.published_at,
        instructions=PLATFORM_INSTRUCTIONS.get(plat_key, []),
        draft_title=draft.title,
        draft_description=draft.description,
        draft_hashtags=draft.hashtags,
        is_approved=draft.is_approved,
        photos=product.images
    )

@app.post("/api/products/{product_id}/publish/{platform}/confirm", response_model=ListingOut)
def confirm_publish(
    product_id: int,
    platform: str,
    payload: ListingConfirmRequest,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    plat_key = platform.lower()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    listing = get_or_create_listing(db, product.id, plat_key)
    listing.status = "published"
    listing.external_url = payload.external_url
    listing.notes = payload.notes
    from backend.models import utc_now
    listing.published_at = utc_now()

    # Jika produk masih draft, ubah menjadi aktif
    if product.status == "draft":
        product.status = "active"

    db.commit()
    db.refresh(listing)
    return listing

@app.post("/api/products/{product_id}/publish/{platform}/reset", response_model=ListingOut)
def reset_publish_status(
    product_id: int,
    platform: str,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    plat_key = platform.lower()
    listing = get_or_create_listing(db, product_id, plat_key)
    listing.status = "manual_action_required" if plat_key == "facebook" else "not_published"
    listing.external_url = None
    listing.published_at = None
    listing.notes = None
    db.commit()
    db.refresh(listing)
    return listing

# ==================== INVENTORY SYNC & SALES HISTORY ====================

@app.post("/api/products/{product_id}/mark-sold", response_model=UnpublishChecklistOut)
def mark_product_as_sold(
    product_id: int,
    payload: MarkAsSoldRequest,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    product.stock = max(0, product.stock - 1)
    if product.stock == 0:
        product.status = "sold"

    event = InventoryEvent(
        product_id=product.id,
        event_type="sold",
        channel=payload.channel.lower(),
        sold_price=payload.sold_price,
        quantity_change=-1,
        remaining_stock=product.stock,
        buyer_note=payload.buyer_note
    )
    db.add(event)

    # Identifikasi kanal lain yang masih terbit untuk ditarik
    unpublish_items: list[ChannelUnpublishItem] = []
    sold_chan = payload.channel.lower()

    for listing in product.listings:
        if listing.platform.lower() != sold_chan and listing.status == "published":
            inst = {
                "shopee": "Ubah stok menjadi 0 atau arsipkan produk di Shopee Seller Center.",
                "facebook": "Tandai postingan sebagai [SOLD] atau hapus postingan di Facebook Group.",
                "preloved": "Ubah status barang menjadi Terjual / Hapus listing di aplikasi Preloved."
            }.get(listing.platform.lower(), "Tarik atau nonaktifkan listing di kanal ini.")

            unpublish_items.append(ChannelUnpublishItem(
                platform=listing.platform,
                platform_name=PLATFORM_NAMES.get(listing.platform, listing.platform),
                status=listing.status,
                external_url=listing.external_url,
                instruction=inst
            ))

    db.commit()
    db.refresh(product)

    return UnpublishChecklistOut(
        product_id=product.id,
        product_name=product.name,
        sold_channel=payload.channel,
        sold_price=payload.sold_price,
        channels_to_unpublish=unpublish_items
    )

@app.post("/api/products/{product_id}/unpublish-channel/{platform}")
def unpublish_channel(
    product_id: int,
    platform: str,
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(
        Listing.product_id == product_id,
        Listing.platform == platform.lower()
    ).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing tidak ditemukan.")

    listing.status = "not_published"
    listing.notes = "Ditarik karena barang sudah terjual di kanal lain."
    db.commit()
    return {"ok": True, "message": f"Listing di {platform} berhasil ditandai ditarik."}

@app.get("/api/history", response_model=SalesHistorySummaryOut)
def get_sales_history(
    _: None = Depends(require_login),
    db: Session = Depends(get_db)
):
    events = db.query(InventoryEvent).filter(
        InventoryEvent.event_type == "sold"
    ).order_by(InventoryEvent.created_at.desc()).all()

    total_sold = len(events)
    total_rev = sum(float(e.sold_price or 0) for e in events)

    breakdown: dict[str, int] = {}
    event_outs: list[InventoryEventOut] = []

    for e in events:
        ch = e.channel or "lainnya"
        breakdown[ch] = breakdown.get(ch, 0) + 1
        event_outs.append(InventoryEventOut(
            id=e.id,
            product_id=e.product_id,
            product_name=e.product.name if e.product else "Produk Dihapus",
            event_type=e.event_type,
            channel=e.channel,
            sold_price=float(e.sold_price) if e.sold_price is not None else None,
            quantity_change=e.quantity_change,
            remaining_stock=e.remaining_stock,
            buyer_note=e.buyer_note,
            created_at=e.created_at
        ))

    return SalesHistorySummaryOut(
        total_sold_items=total_sold,
        total_revenue=total_rev,
        channel_breakdown=breakdown,
        recent_sales=event_outs
    )

# ==================== STATIC FILES & FRONTEND ====================

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads")
