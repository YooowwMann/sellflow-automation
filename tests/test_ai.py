import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.models import Product
from backend.ai_service import generate_builtin_content

@pytest.fixture
def auth_client():
    with TestClient(app) as client:
        login_res = client.post("/api/login", data={
            "username": settings.admin_username,
            "password": settings.admin_password
        })
        assert login_res.status_code == 200
        yield client

def test_ai_copy_generator_facts_preservation():
    fake_product = Product(
        name="Sepatu Sneakers Chuck Taylor 70s",
        category="Sepatu",
        brand="Converse",
        size="42",
        price=450000,
        condition="Preloved - Baik",
        defects="Minus pemakaian wajar di bagian outsole, insole masih empuk original.",
        stock=1,
        description="Warna parchment / off-white, pemakaian santai.",
        status="active"
    )

    # Test Shopee generation
    shopee = generate_builtin_content(fake_product, "shopee")
    assert shopee.platform == "shopee"
    assert "Converse" in shopee.title
    assert "Chuck Taylor" in shopee.title
    assert "Size 42" in shopee.title
    assert "Minus pemakaian wajar di bagian outsole" in shopee.description
    assert "#preloved" in shopee.hashtags

    # Test Facebook Group generation
    fb = generate_builtin_content(fake_product, "facebook")
    assert fb.platform == "facebook"
    assert "[WTS]" in fb.title
    assert "Converse" in fb.title
    assert "450.000" in fb.description
    assert "Minus pemakaian wajar di bagian outsole" in fb.description

    # Test Preloved generation
    preloved = generate_builtin_content(fake_product, "preloved")
    assert preloved.platform == "preloved"
    assert "Chuck Taylor" in preloved.title
    assert "Size: 42" in preloved.description

def test_ai_endpoints_workflow(auth_client):
    # 1. Create a product
    prod_res = auth_client.post("/api/products", json={
        "name": "Kemeja Flanel Uniqlo Tartan",
        "category": "Pakaian Pria",
        "brand": "Uniqlo",
        "size": "L",
        "price": 140000,
        "condition": "Preloved - Sangat Baik",
        "defects": "Tidak ada sobek atau noda, kancing lengkap.",
        "description": "Motif kotak-kotak merah navy."
    })
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 2. Generate AI Drafts for all platforms
    gen_res = auth_client.post(f"/api/products/{product_id}/ai/generate?platform=all")
    assert gen_res.status_code == 201
    drafts = gen_res.json()
    assert len(drafts) == 3

    platforms = {d["platform"] for d in drafts}
    assert platforms == {"shopee", "facebook", "preloved"}
    assert all(d["is_approved"] is False for d in drafts)

    shopee_draft = next(d for d in drafts if d["platform"] == "shopee")
    assert "Uniqlo" in shopee_draft["title"]
    shopee_draft_id = shopee_draft["id"]

    # 3. Get Drafts
    get_drafts_res = auth_client.get(f"/api/products/{product_id}/ai/drafts")
    assert get_drafts_res.status_code == 200
    assert len(get_drafts_res.json()) == 3

    # 4. User edits draft
    patch_res = auth_client.patch(
        f"/api/products/{product_id}/ai/drafts/{shopee_draft_id}",
        json={"title": "Uniqlo Kemeja Flanel Tartan Size L Original Preloved"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Uniqlo Kemeja Flanel Tartan Size L Original Preloved"

    # 5. User approves draft
    appr_res = auth_client.post(f"/api/products/{product_id}/ai/drafts/{shopee_draft_id}/approve")
    assert appr_res.status_code == 200
    assert appr_res.json()["is_approved"] is True

    # 6. Clean up product
    auth_client.delete(f"/api/products/{product_id}")
