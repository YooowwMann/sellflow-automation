import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

@pytest.fixture
def auth_client():
    with TestClient(app) as client:
        # Login first
        login_res = client.post("/api/login", data={
            "username": settings.admin_username,
            "password": settings.admin_password
        })
        assert login_res.status_code == 200
        yield client

def test_product_crud_flow(auth_client):
    # 1. Create Product
    create_payload = {
        "name": "Jaket Bomber Kulit Vintage",
        "category": "Pakaian Pria",
        "brand": "Zara",
        "size": "XL",
        "price": 280000,
        "condition": "Preloved - Sangat Baik",
        "defects": "Sedikit kerut halus di siku kanan, resleting aman mulus.",
        "stock": 1,
        "description": "Jaket bomber preloved bahan kulit sintetis warna cokelat tua.",
        "status": "draft"
    }
    create_res = auth_client.post("/api/products", json=create_payload)
    assert create_res.status_code == 201
    prod = create_res.json()
    product_id = prod["id"]
    assert prod["name"] == create_payload["name"]
    assert prod["brand"] == "Zara"
    assert prod["size"] == "XL"
    assert prod["defects"] == create_payload["defects"]
    assert prod["images"] == []

    # 2. Get Product Detail
    get_res = auth_client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == product_id

    # 3. List with search and filter
    list_all = auth_client.get("/api/products")
    assert list_all.status_code == 200
    assert any(p["id"] == product_id for p in list_all.json())

    # Search by keyword
    search_res = auth_client.get("/api/products?search=Zara")
    assert search_res.status_code == 200
    assert any(p["id"] == product_id for p in search_res.json())

    # Filter by category
    cat_res = auth_client.get("/api/products?category=Pakaian Pria")
    assert cat_res.status_code == 200
    assert any(p["id"] == product_id for p in cat_res.json())

    # 4. Patch / Update Product
    update_res = auth_client.patch(f"/api/products/{product_id}", json={
        "price": 260000,
        "status": "active"
    })
    assert update_res.status_code == 200
    updated_prod = update_res.json()
    assert float(updated_prod["price"]) == 260000
    assert updated_prod["status"] == "active"

    # 5. Upload Valid Photo (JPEG with valid magic bytes)
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 200
    upload_res = auth_client.post(
        f"/api/products/{product_id}/images",
        files=[("files", ("jacket1.jpg", io.BytesIO(fake_jpeg), "image/jpeg"))]
    )
    assert upload_res.status_code == 201
    images = upload_res.json()
    assert len(images) == 1
    image1_id = images[0]["id"]
    assert images[0]["is_primary"] is True
    assert images[0]["file_path"].startswith("/uploads/products/")

    # Upload second photo (PNG with valid magic bytes)
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
    upload_res2 = auth_client.post(
        f"/api/products/{product_id}/images",
        files=[("files", ("jacket2.png", io.BytesIO(fake_png), "image/png"))]
    )
    assert upload_res2.status_code == 201
    image2_id = upload_res2.json()[0]["id"]
    assert upload_res2.json()[0]["is_primary"] is False

    # 6. Change primary image
    primary_res = auth_client.patch(f"/api/products/{product_id}/images/{image2_id}/primary")
    assert primary_res.status_code == 200

    refreshed = auth_client.get(f"/api/products/{product_id}").json()
    img2 = next(img for img in refreshed["images"] if img["id"] == image2_id)
    assert img2["is_primary"] is True

    # 7. Delete an image
    del_img_res = auth_client.delete(f"/api/products/{product_id}/images/{image1_id}")
    assert del_img_res.status_code == 200
    refreshed_after_del = auth_client.get(f"/api/products/{product_id}").json()
    assert len(refreshed_after_del["images"]) == 1

    # 8. Delete Product
    del_res = auth_client.delete(f"/api/products/{product_id}")
    assert del_res.status_code == 200

    # Verify not found after delete
    get_after_del = auth_client.get(f"/api/products/{product_id}")
    assert get_after_del.status_code == 404

def test_image_upload_security_validation(auth_client):
    # Create product to test upload security
    prod_res = auth_client.post("/api/products", json={
        "name": "Barang Tes Keamanan Upload",
        "price": 50000,
        "condition": "Preloved - Baik"
    })
    product_id = prod_res.json()["id"]

    # 1. Reject invalid file extension (.exe)
    exe_file = b"MZ\x90\x00" + b"\x00" * 150
    res_bad_ext = auth_client.post(
        f"/api/products/{product_id}/images",
        files=[("files", ("malware.exe", io.BytesIO(exe_file), "application/x-msdownload"))]
    )
    assert res_bad_ext.status_code == 400
    assert "tidak diizinkan" in res_bad_ext.json()["detail"]

    # 2. Reject spoofed extension (named .jpg but content is plain text / bad magic bytes)
    spoofed_jpg = b"INI BUKAN GAMBAR TAPI TEXT SCRIPT" + b"\x00" * 100
    res_spoofed = auth_client.post(
        f"/api/products/{product_id}/images",
        files=[("files", ("fake.jpg", io.BytesIO(spoofed_jpg), "image/jpeg"))]
    )
    assert res_spoofed.status_code == 400
    assert "tidak valid" in res_spoofed.json()["detail"]

    # Clean up product
    auth_client.delete(f"/api/products/{product_id}")
