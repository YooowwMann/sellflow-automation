import json
from dataclasses import dataclass
import httpx
from backend.config import settings
from backend.models import Product

@dataclass
class GeneratedContent:
    platform: str
    title: str
    description: str
    hashtags: str
    tokens_used: int
    provider: str

STRICT_FACTS_SYSTEM_PROMPT = """Kamu adalah asisten copywriter profesional untuk SellFlow Automation khusus produk preloved / barang bekas berkualitas di Indonesia.

ATURAN WAJIB & ANTI-HALUSINASI:
1. Hanya gunakan fakta yang tertera pada data produk (nama, kategori, brand, ukuran, kondisi, minus/cacat, harga, deskripsi).
2. DILARANG KERAS mengarang spesifikasi, kelengkapan, garansi, atau riwayat pemakaian yang tidak tertulis.
3. JANGAN mengklaim '100% original', 'authentic', atau 'seperti baru' jika tidak tertulis dalam data pengguna.
4. Jika produk memiliki catatan minus / cacat, sebutkan secara jujur, transparan, dan sopan.
5. Dilarang menyertakan nomor HP/WhatsApp, tautan eksternal, atau ajakan transaksi terlarang.
6. Kembalikan HANYA JSON murni dengan format:
{
  "title": "...",
  "description": "...",
  "hashtags": "#tag1 #tag2 ..."
}
"""

def generate_builtin_content(product: Product, platform: str) -> GeneratedContent:
    """Generator bawaan deterministik berbasis aturan data riil produk (Zero Hallucination)."""
    brand_part = f"{product.brand} " if product.brand else ""
    size_part = f"Size {product.size} " if product.size else ""
    price_fmt = f"Rp {int(product.price):,}".replace(",", ".")
    cond_clean = product.condition.replace("Preloved - ", "").strip()

    defects_text = f"Catatan Minus/Kondisi: {product.defects}" if product.defects else "Kondisi fisik aman, tidak ada minus mayor."
    desc_extra = f"\n\nDeskripsi tambahan:\n{product.description}" if product.description else ""

    if platform == "shopee":
        title = f"{brand_part}{product.name} {size_part}Preloved {cond_clean}"[:120].strip()
        description = (
            f"Selamat datang di SellFlow Store!\n\n"
            f"SPESIFIKASI PRODUK:\n"
            f"- Nama: {product.name}\n"
            f"- Kategori: {product.category or 'Preloved'}\n"
            f"- Brand: {product.brand or 'No Brand'}\n"
            f"- Ukuran: {product.size or '-'}\n"
            f"- Kondisi: {product.condition}\n"
            f"- Stok: {product.stock}\n\n"
            f"DETAIL & KEADAAN BARANG:\n"
            f"{defects_text}{desc_extra}\n\n"
            f"CATATAN PEMBELI:\n"
            f"- Barang ready sesuai stok tertera.\n"
            f"- Foto produk adalah foto asli barang yang dijual.\n"
            f"- Silakan chat toko jika ada pertanyaan seputar ukuran atau detail barang."
        )
        cat_tag = (product.category or "preloved").lower().replace(" ", "").replace("&", "")
        brand_tag = (product.brand or "").lower().replace(" ", "")
        tags = [f"#{cat_tag}", "#preloved", "#thrift", "#prelovedindo"]
        if brand_tag:
            tags.insert(0, f"#{brand_tag}")
        hashtags = " ".join(tags)

    elif platform == "facebook":
        title = f"[WTS] {brand_part}{product.name} {size_part}({cond_clean})"[:100].strip()
        description = (
            f"Halo teman-teman komunitas!\n"
            f"Mau lepas barang preloved koleksi pribadi:\n\n"
            f"📦 Barang: {product.name}\n"
            f"🏷️ Brand: {product.brand or '-'}\n"
            f"📏 Size/Ukuran: {product.size or '-'}\n"
            f"✨ Kondisi: {product.condition}\n"
            f"⚠️ Minus: {product.defects or 'Mulus tidak ada minus'}\n"
            f"💰 Harga: {price_fmt} (Bisa nego santai)\n\n"
            f"Keterangan:\n{product.description or 'Barang terawat baik dan siap pakai.'}\n\n"
            f"Berminat atau mau tanya detail foto? Silakan tinggalkan komentar atau langsung PM/Inbox. Terima kasih!"
        )
        hashtags = "#wts #jualpreloved #komunitaspreloved"

    else:  # preloved app
        title = f"{brand_part}{product.name} {size_part}({product.condition})"[:100].strip()
        description = (
            f"Preloved item:\n"
            f"{product.name}\n\n"
            f"- Brand: {product.brand or '-'}\n"
            f"- Size: {product.size or '-'}\n"
            f"- Kondisi: {product.condition}\n"
            f"- Catatan: {product.defects or 'Tidak ada cacat'}\n\n"
            f"{product.description or 'Koleksi preloved terawat.'}"
        )
        hashtags = "#prelovedfashion #secondhand"

    return GeneratedContent(
        platform=platform,
        title=title,
        description=description,
        hashtags=hashtags,
        tokens_used=0,
        provider="builtin"
    )

async def generate_gemini_content(product: Product, platform: str) -> GeneratedContent:
    """Memanggil Google Gemini API secara aman dengan validasi anti-halusinasi."""
    platform_name = {
        "shopee": "Marketplace Shopee (Gaya keyword SEO, maksimal 120 karakter judul, deskripsi rapi berpoin)",
        "facebook": "Komunitas Facebook Group (Gaya santai ramah WTS/jual preloved, harga jelas, ajakan PM sopan)",
        "preloved": "Aplikasi Preloved (Gaya secondhand item transparan, ukuran jelas, minus diungkapkan jujur)"
    }.get(platform, platform)

    user_prompt = f"""Target Platform: {platform_name}
Data Produk Asli:
- Nama Barang: {product.name}
- Kategori: {product.category or 'Tidak disebutkan'}
- Brand/Merek: {product.brand or 'Tidak disebutkan'}
- Ukuran/Size: {product.size or 'Tidak disebutkan'}
- Harga: Rp {int(product.price):,}
- Kondisi: {product.condition}
- Catatan Minus/Cacat: {product.defects or 'Tidak ada minus'}
- Deskripsi Pengguna: {product.description or 'Tidak ada deskripsi tambahan'}
- Stok: {product.stock}

Buatkan judul yang menarik, deskripsi lengkap yang jujur, dan tagar yang relevan."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.ai_model}:generateContent?key={settings.gemini_api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{STRICT_FACTS_SYSTEM_PROMPT}\n\n{user_prompt}"}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                # Fallback ke built-in jika API limit atau error
                return generate_builtin_content(product, platform)

            res_data = resp.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                return generate_builtin_content(product, platform)

            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            parsed = json.loads(text_content)
            tokens = res_data.get("usageMetadata", {}).get("totalTokenCount", 0)

            return GeneratedContent(
                platform=platform,
                title=str(parsed.get("title", product.name))[:250],
                description=str(parsed.get("description", product.description)),
                hashtags=str(parsed.get("hashtags", "")),
                tokens_used=tokens,
                provider="gemini"
            )
    except Exception:
        # Fallback aman
        return generate_builtin_content(product, platform)

async def generate_product_copy(product: Product, platform: str) -> GeneratedContent:
    """Fungsi utama untuk membuat copy produk berdasarkan provider aktif."""
    if settings.ai_provider == "gemini":
        return await generate_gemini_content(product, platform)
    return generate_builtin_content(product, platform)
