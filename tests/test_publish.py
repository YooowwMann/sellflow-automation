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

def test_publish_package_and_assisted_posting_workflow(auth_client):
    # 1. Create a product
    prod_res = auth_client.post("/api/products", json={
        "name": "Hoodie H&M Divided Vintage",
        "category": "Pakaian Pria",
        "brand": "H&M",
        "size": "M",
        "price": 110000,
        "condition": "Preloved - Sangat Baik",
        "defects": "Warna pekat, karet rib lengan masih kencang.",
        "description": "Hoodie preloved warna abu misty.",
        "status": "draft"
    })
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 2. Get Publications list
    pub_res = auth_client.get("/api/publications")
    assert pub_res.status_code == 200
    products = pub_res.json()
    target_prod = next(p for p in products if p["id"] == product_id)
    platforms = {l["platform"] for l in target_prod["listings"]}
    assert {"shopee", "facebook", "preloved"}.issubset(platforms)

    # 3. Get Publish Package for Facebook Assisted Posting
    fb_pkg = auth_client.get(f"/api/products/{product_id}/publish-package/facebook")
    assert fb_pkg.status_code == 200
    pkg_data = fb_pkg.json()
    assert pkg_data["platform"] == "facebook"
    assert "https://www.facebook.com/groups/" in pkg_data["destination_url"]
    assert len(pkg_data["instructions"]) >= 3
    assert "[WTS]" in pkg_data["draft_title"]
    assert pkg_data["listing_status"] in ("not_published", "manual_action_required")

    # 4. Confirm Facebook publication with post URL
    post_url = "https://facebook.com/groups/12345/posts/67890"
    confirm_res = auth_client.post(
        f"/api/products/{product_id}/publish/facebook/confirm",
        json={"external_url": post_url, "notes": "Diposting di grup Thrift Indo"}
    )
    assert confirm_res.status_code == 200
    listing = confirm_res.json()
    assert listing["status"] == "published"
    assert listing["external_url"] == post_url
    assert listing["published_at"] is not None

    # Check that product status transitioned from draft to active
    prod_refreshed = auth_client.get(f"/api/products/{product_id}").json()
    assert prod_refreshed["status"] == "active"

    # 5. Reset status
    reset_res = auth_client.post(f"/api/products/{product_id}/publish/facebook/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "manual_action_required"
    assert reset_res.json()["external_url"] is None

    # 6. Test invalid platform rejection
    bad_plat = auth_client.get(f"/api/products/{product_id}/publish-package/invalid_platform")
    assert bad_plat.status_code == 400
    assert "tidak didukung" in bad_plat.json()["detail"]

    # Clean up
    auth_client.delete(f"/api/products/{product_id}")
