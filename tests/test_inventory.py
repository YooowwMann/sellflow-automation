import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

@pytest.fixture
def auth_client():
    with TestClient(app) as client:
        login_res = client.post("/api/login", data={
            "username": settings.admin_username,
            "password": settings.admin_password
        })
        assert login_res.status_code == 200
        yield client

def test_inventory_sync_and_sales_history(auth_client):
    # 1. Create a product with stock 1
    prod_res = auth_client.post("/api/products", json={
        "name": "Sepatu Boots Kulit Dr Martens 1460",
        "category": "Sepatu",
        "brand": "Dr. Martens",
        "size": "42",
        "price": 1200000,
        "condition": "Preloved - Sangat Baik",
        "defects": "Kerut pemakaian wajar, sol bawah masih tebal.",
        "stock": 1,
        "description": "Boots kulit warna cherry red 8 hole.",
        "status": "draft"
    })
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 2. Publish to both Facebook and Shopee
    auth_client.post(
        f"/api/products/{product_id}/publish/facebook/confirm",
        json={"external_url": "https://facebook.com/groups/docmart/posts/101", "notes": "Postingan FB"}
    )
    auth_client.post(
        f"/api/products/{product_id}/publish/shopee/confirm",
        json={"external_url": "https://shopee.co.id/product/101", "notes": "Listing Shopee"}
    )

    # 3. Mark product as sold via Facebook Group (deal negotiated to 1.150.000)
    sold_payload = {
        "channel": "facebook",
        "sold_price": 1150000,
        "buyer_note": "COD di Jakarta Selatan, buyer: Mas Budi"
    }
    sold_res = auth_client.post(f"/api/products/{product_id}/mark-sold", json=sold_payload)
    assert sold_res.status_code == 200
    checklist_data = sold_res.json()
    assert checklist_data["sold_channel"] == "facebook"
    assert checklist_data["sold_price"] == 1150000

    # Verify that Shopee is included in the unpublish checklist!
    unpub_platforms = [item["platform"] for item in checklist_data["channels_to_unpublish"]]
    assert "shopee" in unpub_platforms
    assert "facebook" not in unpub_platforms  # Facebook was where it was sold

    # 4. Verify product status and stock
    refreshed_prod = auth_client.get(f"/api/products/{product_id}").json()
    assert refreshed_prod["stock"] == 0
    assert refreshed_prod["status"] == "sold"

    # 5. Unpublish from Shopee
    unpub_res = auth_client.post(f"/api/products/{product_id}/unpublish-channel/shopee")
    assert unpub_res.status_code == 200

    # 6. Check Sales History API
    hist_res = auth_client.get("/api/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert history["total_sold_items"] >= 1
    assert history["total_revenue"] >= 1150000
    assert history["channel_breakdown"]["facebook"] >= 1
    assert any(sale["product_id"] == product_id for sale in history["recent_sales"])

    # Clean up
    auth_client.delete(f"/api/products/{product_id}")
