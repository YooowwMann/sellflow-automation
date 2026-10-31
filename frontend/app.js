// ==================== STATE & DOM REFS ====================
const loginView = document.getElementById("loginView");
const appView = document.getElementById("appView");
const dashboardSection = document.getElementById("dashboardSection");
const productsSection = document.getElementById("productsSection");
const publishSection = document.getElementById("publishSection");
const historySection = document.getElementById("historySection");
const pageTitle = document.getElementById("pageTitle");

const navDashboard = document.getElementById("navDashboard");
const navProducts = document.getElementById("navProducts");
const navPublish = document.getElementById("navPublish");
const navHistory = document.getElementById("navHistory");

const productSearchInput = document.getElementById("productSearchInput");
const productStatusFilter = document.getElementById("productStatusFilter");
const productCategoryFilter = document.getElementById("productCategoryFilter");
const productListContainer = document.getElementById("productListContainer");

const productModal = document.getElementById("productModal");
const productForm = document.getElementById("productForm");
const productModalTitle = document.getElementById("productModalTitle");

const photoModal = document.getElementById("photoModal");
const photoGalleryContainer = document.getElementById("photoGalleryContainer");
const photoCountBadge = document.getElementById("photoCountBadge");
const photoFileInput = document.getElementById("photoFileInput");
const uploadDropzone = document.getElementById("uploadDropzone");
const uploadProgress = document.getElementById("uploadProgress");

let currentActiveProductForPhotos = null;
let searchDebounceTimer = null;

// ==================== API HELPER ====================
const api = async (url, options = {}) => {
  const response = await fetch(url, { credentials: "same-origin", ...options });
  if (response.status === 401) {
    showLogin();
    throw new Error("Sesi berakhir. Silakan login kembali.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Terjadi kesalahan pada sistem.");
  }
  return data;
};

// ==================== TOAST & UTILS ====================
function showToast(message, isError = false) {
  const toast = document.getElementById("toastNotification");
  toast.textContent = message;
  toast.style.background = isError ? "#b91c1c" : "#1e293b";
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3500);
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function formatRupiah(num) {
  return "Rp " + Number(num || 0).toLocaleString("id-ID");
}

// ==================== NAVIGATION & VIEWS ====================
function showLogin() {
  appView.classList.add("hidden");
  loginView.classList.remove("hidden");
}

function showApp() {
  loginView.classList.add("hidden");
  appView.classList.remove("hidden");
}

function switchView(viewName) {
  dashboardSection.classList.add("hidden");
  productsSection.classList.add("hidden");
  publishSection.classList.add("hidden");
  historySection.classList.add("hidden");

  navDashboard.classList.remove("selected");
  navProducts.classList.remove("selected");
  navPublish.classList.remove("selected");
  navHistory.classList.remove("selected");

  if (viewName === "products") {
    productsSection.classList.remove("hidden");
    navProducts.classList.add("selected");
    pageTitle.textContent = "Katalog Produk";
    loadProducts();
  } else if (viewName === "publish") {
    publishSection.classList.remove("hidden");
    navPublish.classList.add("selected");
    pageTitle.textContent = "Publikasi Multi-Kanal";
    loadPublications();
  } else if (viewName === "history") {
    historySection.classList.remove("hidden");
    navHistory.classList.add("selected");
    pageTitle.textContent = "Riwayat Penjualan";
    loadHistory();
  } else {
    dashboardSection.classList.remove("hidden");
    navDashboard.classList.add("selected");
    pageTitle.textContent = "Dashboard";
    loadDashboard();
  }
}

navDashboard.addEventListener("click", e => { e.preventDefault(); switchView("dashboard"); });
navProducts.addEventListener("click", e => { e.preventDefault(); switchView("products"); });
navPublish.addEventListener("click", e => { e.preventDefault(); switchView("publish"); });
navHistory.addEventListener("click", e => { e.preventDefault(); switchView("history"); });

// ==================== DASHBOARD ====================
async function loadDashboard() {
  try {
    const d = await api("/api/dashboard");
    document.getElementById("totalProducts").textContent = d.total_products;
    document.getElementById("activeProducts").textContent = d.active_products;
    document.getElementById("draftProducts").textContent = d.draft_products;
    document.getElementById("platformList").innerHTML = d.platforms.map(p => `
      <div class="platform">
        <b>${escapeHtml(p.name)}</b>
        <p>${escapeHtml(p.state)}</p>
        <span class="status">Belum terhubung</span>
      </div>
    `).join("");
  } catch (err) {
    showToast(err.message, true);
  }
}

// ==================== PRODUCT MANAGER ====================
async function loadProducts() {
  productListContainer.innerHTML = `<div class="empty-state"><p class="muted">Memuat produk...</p></div>`;
  const search = productSearchInput.value.trim();
  const status = productStatusFilter.value;
  const category = productCategoryFilter.value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);
  if (category) params.append("category", category);

  try {
    const products = await api(`/api/products?${params.toString()}`);
    renderProductList(products);
  } catch (err) {
    showToast(err.message, true);
    productListContainer.innerHTML = `<div class="empty-state"><p class="error">${escapeHtml(err.message)}</p></div>`;
  }
}

function renderProductList(products) {
  if (!products || products.length === 0) {
    productListContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">□</div>
        <h3>Belum ada produk ditemukan</h3>
        <p>Mulai tambahkan produk preloved pertama Anda ke dalam katalog.</p>
        <button class="btn primary" onclick="openProductModal()">+ Tambah Produk Baru</button>
      </div>
    `;
    return;
  }

  productListContainer.innerHTML = products.map(p => {
    // Cari foto utama
    const primaryImg = p.images?.find(i => i.is_primary) || p.images?.[0];
    const imageCount = p.images?.length || 0;
    const mediaHtml = primaryImg
      ? `<img src="${primaryImg.file_path}" alt="${escapeHtml(p.name)}">`
      : `<div class="no-image-placeholder"><span>📷</span>Belum ada foto</div>`;

    const statusBadgeClass = {
      active: "badge-active",
      draft: "badge-draft",
      sold: "badge-sold",
      archived: "badge-archived"
    }[p.status] || "badge-draft";

    const statusLabel = {
      active: "Aktif",
      draft: "Draft",
      sold: "Terjual",
      archived: "Diarsipkan"
    }[p.status] || p.status;

    return `
      <article class="product-card">
        <div class="product-media">
          ${mediaHtml}
          ${imageCount > 0 ? `<span class="photo-count-pill">${imageCount} Foto</span>` : ""}
        </div>
        <div class="product-body">
          <div class="product-meta">
            ${p.category ? `<span class="badge badge-category">${escapeHtml(p.category)}</span>` : ""}
            ${p.brand ? `<span class="badge badge-brand">${escapeHtml(p.brand)}</span>` : ""}
            <span class="badge ${statusBadgeClass}">${escapeHtml(statusLabel)}</span>
          </div>
          <h4 class="product-title">${escapeHtml(p.name)}</h4>
          <div class="product-condition">
            ${escapeHtml(p.condition)} ${p.size ? `· Size ${escapeHtml(p.size)}` : ""}
          </div>
          ${p.defects ? `<div class="product-defects-preview">⚠️ <b>Minus/Catatan:</b> ${escapeHtml(p.defects)}</div>` : ""}
          <div class="product-price-stock">
            <span class="product-price">${formatRupiah(p.price)}</span>
            <span class="product-stock">Stok: <b>${p.stock}</b></span>
          </div>
          <div class="product-actions" style="flex-wrap: wrap;">
            <button class="btn btn-ai btn-sm" onclick="openAiModal(${p.id})">✨ AI Copy</button>
            ${p.status !== 'sold' ? `<button class="btn outline btn-sm" style="border-color:#f59e0b; color:#b45309;" onclick="openSoldModal(${p.id})">🏷️ Terjual</button>` : ''}
            <button class="btn outline btn-sm" onclick="openProductModal(${p.id})">Edit</button>
            <button class="btn outline btn-sm" onclick="openPhotoModal(${p.id})">Foto (${imageCount})</button>
            <button class="btn btn-danger btn-sm" onclick="handleDeleteProduct(${p.id})">Hapus</button>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

// Search & Filter event listeners
productSearchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(loadProducts, 300);
});
productStatusFilter.addEventListener("change", loadProducts);
productCategoryFilter.addEventListener("change", loadProducts);

// ==================== PRODUCT MODAL (CREATE / EDIT) ====================
document.getElementById("btnOpenNewProductModal").addEventListener("click", () => openProductModal());
document.getElementById("btnCloseProductModal").addEventListener("click", closeProductModal);
document.getElementById("btnCancelProductForm").addEventListener("click", closeProductModal);

window.openProductModal = async function(productId = null) {
  productForm.reset();
  document.getElementById("formProductId").value = "";

  if (productId) {
    productModalTitle.textContent = "Edit Produk";
    try {
      const p = await api(`/api/products/${productId}`);
      document.getElementById("formProductId").value = p.id;
      document.getElementById("formProductName").value = p.name || "";
      document.getElementById("formProductCategory").value = p.category || "";
      document.getElementById("formProductBrand").value = p.brand || "";
      document.getElementById("formProductSize").value = p.size || "";
      document.getElementById("formProductPrice").value = p.price || 0;
      document.getElementById("formProductStock").value = p.stock || 1;
      document.getElementById("formProductCondition").value = p.condition || "Preloved - Sangat Baik";
      document.getElementById("formProductDefects").value = p.defects || "";
      document.getElementById("formProductDescription").value = p.description || "";
      document.getElementById("formProductStatus").value = p.status || "active";
    } catch (err) {
      showToast(err.message, true);
      return;
    }
  } else {
    productModalTitle.textContent = "Tambah Produk Baru";
    document.getElementById("formProductStatus").value = "active";
  }
  productModal.classList.remove("hidden");
};

function closeProductModal() {
  productModal.classList.add("hidden");
}

productForm.addEventListener("submit", async e => {
  e.preventDefault();
  const id = document.getElementById("formProductId").value;
  const payload = {
    name: document.getElementById("formProductName").value.trim(),
    category: document.getElementById("formProductCategory").value || null,
    brand: document.getElementById("formProductBrand").value.trim() || null,
    size: document.getElementById("formProductSize").value.trim() || null,
    price: parseFloat(document.getElementById("formProductPrice").value) || 0,
    stock: parseInt(document.getElementById("formProductStock").value, 10) || 1,
    condition: document.getElementById("formProductCondition").value,
    defects: document.getElementById("formProductDefects").value.trim() || null,
    description: document.getElementById("formProductDescription").value.trim(),
    status: document.getElementById("formProductStatus").value
  };

  try {
    if (id) {
      await api(`/api/products/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      showToast("Produk berhasil diperbarui.");
    } else {
      await api("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      showToast("Produk baru berhasil ditambahkan.");
    }
    closeProductModal();
    loadProducts();
  } catch (err) {
    showToast(err.message, true);
  }
});

window.handleDeleteProduct = async function(productId) {
  if (!confirm("Apakah Anda yakin ingin menghapus produk ini? Semua foto produk juga akan dihapus.")) {
    return;
  }
  try {
    await api(`/api/products/${productId}`, { method: "DELETE" });
    showToast("Produk berhasil dihapus.");
    loadProducts();
  } catch (err) {
    showToast(err.message, true);
  }
};

// ==================== PHOTO MANAGEMENT MODAL ====================
document.getElementById("btnClosePhotoModal").addEventListener("click", closePhotoModal);
document.getElementById("btnDonePhotos").addEventListener("click", closePhotoModal);
document.getElementById("btnTriggerUpload").addEventListener("click", () => photoFileInput.click());

window.openPhotoModal = async function(productId) {
  currentActiveProductForPhotos = productId;
  await refreshPhotoGallery();
  photoModal.classList.remove("hidden");
};

function closePhotoModal() {
  photoModal.classList.add("hidden");
  currentActiveProductForPhotos = null;
  loadProducts(); // Refresh foto di katalog
}

async function refreshPhotoGallery() {
  if (!currentActiveProductForPhotos) return;
  try {
    const product = await api(`/api/products/${currentActiveProductForPhotos}`);
    document.getElementById("photoModalTitle").textContent = `Foto: ${product.name}`;
    const images = product.images || [];
    photoCountBadge.textContent = images.length;

    if (images.length === 0) {
      photoGalleryContainer.innerHTML = `<p class="muted" style="grid-column:1/-1;">Belum ada foto yang diunggah.</p>`;
      return;
    }

    photoGalleryContainer.innerHTML = images.map(img => `
      <div class="photo-item">
        <img src="${img.file_path}" alt="${escapeHtml(img.file_name)}">
        ${img.is_primary ? `<span class="photo-item-badge">UTAMA</span>` : ""}
        <div class="photo-item-actions">
          ${!img.is_primary ? `<button type="button" onclick="handleSetPrimaryPhoto(${img.id})">Jadikan Utama</button>` : `<span></span>`}
          <button type="button" class="btn-del-photo" onclick="handleDeletePhoto(${img.id})">Hapus</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    showToast(err.message, true);
  }
}

// Drag & drop upload handler
uploadDropzone.addEventListener("dragover", e => { e.preventDefault(); uploadDropzone.classList.add("dragover"); });
uploadDropzone.addEventListener("dragleave", () => uploadDropzone.classList.remove("dragover"));
uploadDropzone.addEventListener("drop", async e => {
  e.preventDefault();
  uploadDropzone.classList.remove("dragover");
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    await uploadSelectedFiles(e.dataTransfer.files);
  }
});

photoFileInput.addEventListener("change", async e => {
  if (e.target.files && e.target.files.length > 0) {
    await uploadSelectedFiles(e.target.files);
    e.target.value = ""; // Reset file input
  }
});

async function uploadSelectedFiles(fileList) {
  if (!currentActiveProductForPhotos) return;
  uploadProgress.classList.remove("hidden");
  const formData = new FormData();
  for (const file of fileList) {
    formData.append("files", file);
  }

  try {
    await api(`/api/products/${currentActiveProductForPhotos}/images`, {
      method: "POST",
      body: formData
    });
    showToast("Foto berhasil diunggah.");
    await refreshPhotoGallery();
  } catch (err) {
    showToast(err.message, true);
  } finally {
    uploadProgress.classList.add("hidden");
  }
}

window.handleSetPrimaryPhoto = async function(imageId) {
  if (!currentActiveProductForPhotos) return;
  try {
    await api(`/api/products/${currentActiveProductForPhotos}/images/${imageId}/primary`, {
      method: "PATCH"
    });
    showToast("Foto utama berhasil diperbarui.");
    await refreshPhotoGallery();
  } catch (err) {
    showToast(err.message, true);
  }
};

window.handleDeletePhoto = async function(imageId) {
  if (!currentActiveProductForPhotos) return;
  if (!confirm("Hapus foto ini?")) return;
  try {
    await api(`/api/products/${currentActiveProductForPhotos}/images/${imageId}`, {
      method: "DELETE"
    });
    showToast("Foto berhasil dihapus.");
    await refreshPhotoGallery();
  } catch (err) {
    showToast(err.message, true);
  }
};

// ==================== AI COPYWRITER MODAL ====================
let currentActiveProductForAi = null;
let currentAiDrafts = [];
let activeAiPlatform = "shopee";

const aiModal = document.getElementById("aiModal");
const aiDraftForm = document.getElementById("aiDraftForm");
const aiDraftTitle = document.getElementById("aiDraftTitle");
const aiDraftDescription = document.getElementById("aiDraftDescription");
const aiDraftHashtags = document.getElementById("aiDraftHashtags");
const aiApprovalStatus = document.getElementById("aiApprovalStatus");
const aiTokenUsage = document.getElementById("aiTokenUsage");
const aiEngineBadge = document.getElementById("aiEngineBadge");

document.getElementById("btnCloseAiModal").addEventListener("click", () => aiModal.classList.add("hidden"));

// Platform tabs
document.querySelectorAll(".ai-tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".ai-tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeAiPlatform = btn.dataset.platform;
    displayCurrentAiDraft();
  });
});

window.openAiModal = async function(productId) {
  currentActiveProductForAi = productId;
  activeAiPlatform = "shopee";
  document.querySelectorAll(".ai-tab-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.platform === "shopee");
  });

  try {
    const product = await api(`/api/products/${productId}`);
    document.getElementById("aiModalTitle").textContent = `✨ AI Copywriter — ${product.name}`;

    currentAiDrafts = await api(`/api/products/${productId}/ai/drafts`);
    if (!currentAiDrafts || currentAiDrafts.length === 0) {
      showToast("Membuat draft copywriting AI...");
      currentAiDrafts = await api(`/api/products/${productId}/ai/generate?platform=all`, { method: "POST" });
    }

    displayCurrentAiDraft();
    aiModal.classList.remove("hidden");
  } catch (err) {
    showToast(err.message, true);
  }
};

function displayCurrentAiDraft() {
  const draft = currentAiDrafts.find(d => d.platform === activeAiPlatform);
  if (!draft) {
    aiDraftTitle.value = "";
    aiDraftDescription.value = "";
    aiDraftHashtags.value = "";
    document.getElementById("aiDraftId").value = "";
    aiApprovalStatus.className = "badge badge-draft";
    aiApprovalStatus.textContent = "Belum Ada Draft";
    aiTokenUsage.textContent = "";
    return;
  }

  document.getElementById("aiDraftId").value = draft.id;
  aiDraftTitle.value = draft.title;
  aiDraftDescription.value = draft.description;
  aiDraftHashtags.value = draft.hashtags || "";
  aiEngineBadge.textContent = `Engine: ${draft.provider}`;

  if (draft.is_approved) {
    aiApprovalStatus.className = "badge badge-approved";
    aiApprovalStatus.textContent = "✓ Sudah Disetujui";
  } else {
    aiApprovalStatus.className = "badge badge-draft";
    aiApprovalStatus.textContent = "Draft (Belum Disetujui)";
  }

  aiTokenUsage.textContent = draft.tokens_used > 0 ? `${draft.tokens_used} token` : "";
}

// Regenerate single platform draft
document.getElementById("btnRegenerateAi").addEventListener("click", async () => {
  if (!currentActiveProductForAi) return;
  showToast(`Membuat ulang draft ${activeAiPlatform.toUpperCase()}...`);
  try {
    const res = await api(`/api/products/${currentActiveProductForAi}/ai/generate?platform=${activeAiPlatform}`, { method: "POST" });
    const updated = res[0];
    const idx = currentAiDrafts.findIndex(d => d.platform === activeAiPlatform);
    if (idx !== -1) currentAiDrafts[idx] = updated;
    else currentAiDrafts.push(updated);

    displayCurrentAiDraft();
    showToast("Draft AI berhasil dibuat ulang.");
  } catch (err) {
    showToast(err.message, true);
  }
});

// Save draft edits
aiDraftForm.addEventListener("submit", async e => {
  e.preventDefault();
  const draftId = document.getElementById("aiDraftId").value;
  if (!draftId || !currentActiveProductForAi) return;

  const payload = {
    title: aiDraftTitle.value.trim(),
    description: aiDraftDescription.value.trim(),
    hashtags: aiDraftHashtags.value.trim()
  };

  try {
    const updated = await api(`/api/products/${currentActiveProductForAi}/ai/drafts/${draftId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const idx = currentAiDrafts.findIndex(d => d.id === updated.id);
    if (idx !== -1) currentAiDrafts[idx] = updated;

    displayCurrentAiDraft();
    showToast("Perubahan draft berhasil disimpan.");
  } catch (err) {
    showToast(err.message, true);
  }
});

// Approve draft
document.getElementById("btnApproveAiDraft").addEventListener("click", async () => {
  const draftId = document.getElementById("aiDraftId").value;
  if (!draftId || !currentActiveProductForAi) return;

  try {
    const updated = await api(`/api/products/${currentActiveProductForAi}/ai/drafts/${draftId}/approve`, {
      method: "POST"
    });
    const idx = currentAiDrafts.findIndex(d => d.id === updated.id);
    if (idx !== -1) currentAiDrafts[idx] = updated;

    displayCurrentAiDraft();
    showToast("Draft berhasil disetujui untuk publikasi.");
  } catch (err) {
    showToast(err.message, true);
  }
});

// Copy content to clipboard
document.getElementById("btnCopyAiContent").addEventListener("click", () => {
  const title = aiDraftTitle.value.trim();
  const desc = aiDraftDescription.value.trim();
  const tags = aiDraftHashtags.value.trim();

  const fullText = `${title}\n\n${desc}${tags ? `\n\n${tags}` : ""}`;
  navigator.clipboard.writeText(fullText).then(() => {
    showToast("Teks lengkap disalin ke clipboard!");
  }).catch(() => {
    showToast("Gagal menyalin secara otomatis.", true);
  });
});

// ==================== PUBLISHING & ASSISTED POSTING ====================
let currentPublishProductId = null;
let currentPublishPlatform = null;

const publishModal = document.getElementById("publishModal");
const pubModalTitle = document.getElementById("pubModalTitle");
const pubPlatformBadge = document.getElementById("pubPlatformBadge");
const pubInstructionsList = document.getElementById("pubInstructionsList");
const pubDestinationBtn = document.getElementById("pubDestinationBtn");
const pubPhotosContainer = document.getElementById("pubPhotosContainer");
const pubPreviewTitle = document.getElementById("pubPreviewTitle");
const pubPreviewDescription = document.getElementById("pubPreviewDescription");
const pubPreviewHashtags = document.getElementById("pubPreviewHashtags");
const pubConfirmUrl = document.getElementById("pubConfirmUrl");
const pubConfirmNotes = document.getElementById("pubConfirmNotes");

document.getElementById("btnClosePublishModal").addEventListener("click", () => publishModal.classList.add("hidden"));

async function loadPublications() {
  const tbody = document.getElementById("publicationsTableBody");
  tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align:center; padding:30px;">Memuat status publikasi...</td></tr>`;

  try {
    const products = await api("/api/publications");
    if (!products || products.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align:center; padding:30px;">Belum ada produk di katalog. Tambahkan produk terlebih dahulu.</td></tr>`;
      return;
    }

    tbody.innerHTML = products.map(p => {
      const primaryImg = p.images?.find(i => i.is_primary) || p.images?.[0];
      const thumbHtml = primaryImg
        ? `<img class="prod-thumb-sm" src="${primaryImg.file_path}" alt="${escapeHtml(p.name)}">`
        : `<div class="no-thumb-sm">□</div>`;

      const renderPlatformCell = (platKey) => {
        const listing = p.listings?.find(l => l.platform === platKey) || { status: "not_published" };
        let badgeClass = "badge-draft";
        let statusText = "Belum Terbit";

        if (listing.status === "published") {
          badgeClass = "badge-active";
          statusText = "✓ Terbit";
        } else if (listing.status === "manual_action_required") {
          badgeClass = "badge-sold";
          statusText = "Tindakan Manual";
        }

        const externalLinkHtml = listing.external_url
          ? `<a href="${listing.external_url}" target="_blank" rel="noopener noreferrer" style="font-size:11px; color:var(--accent); text-decoration:none;">Tautan Listing ↗</a>`
          : "";

        return `
          <div class="platform-cell-box">
            <span class="badge ${badgeClass}">${statusText}</span>
            <button class="btn outline btn-sm" onclick="openPublishModal(${p.id}, '${platKey}')">Paket Posting</button>
            ${externalLinkHtml}
          </div>
        `;
      };

      return `
        <tr>
          <td>
            <div class="prod-table-cell">
              ${thumbHtml}
              <div>
                <b>${escapeHtml(p.name)}</b>
                <small class="muted" style="display:block;">${escapeHtml(p.condition)}</small>
              </div>
            </div>
          </td>
          <td>
            <b>${formatRupiah(p.price)}</b>
            <small class="muted" style="display:block;">Stok: ${p.stock}</small>
          </td>
          <td>${renderPlatformCell("shopee")}</td>
          <td>${renderPlatformCell("facebook")}</td>
          <td>${renderPlatformCell("preloved")}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(err.message, true);
  }
}

window.openPublishModal = async function(productId, platform) {
  currentPublishProductId = productId;
  currentPublishPlatform = platform;

  try {
    const pkg = await api(`/api/products/${productId}/publish-package/${platform}`);
    pubModalTitle.textContent = `Paket Posting: ${pkg.product_name}`;
    pubPlatformBadge.textContent = pkg.platform_name;

    pubInstructionsList.innerHTML = pkg.instructions.map(inst => `<li>${escapeHtml(inst)}</li>`).join("");
    pubDestinationBtn.href = pkg.destination_url;
    pubDestinationBtn.textContent = `Buka ${pkg.platform_name} ↗`;

    pubPreviewTitle.value = pkg.draft_title || "";
    pubPreviewDescription.value = pkg.draft_description || "";
    pubPreviewHashtags.value = pkg.draft_hashtags || "";

    pubConfirmUrl.value = pkg.external_url || "";
    pubConfirmNotes.value = "";

    // Photos
    if (pkg.photos && pkg.photos.length > 0) {
      pubPhotosContainer.innerHTML = pkg.photos.map(photo => `
        <a href="${photo.file_path}" target="_blank" title="Klik untuk membuka ukuran penuh">
          <img class="pub-photo-thumb" src="${photo.file_path}" alt="${escapeHtml(photo.file_name)}">
        </a>
      `).join("");
    } else {
      pubPhotosContainer.innerHTML = `<p class="muted" style="font-size:11px;">Belum ada foto yang diunggah untuk produk ini.</p>`;
    }

    publishModal.classList.remove("hidden");
  } catch (err) {
    showToast(err.message, true);
  }
};

// Copy full copywriting from publish modal
document.getElementById("btnCopyPubContent").addEventListener("click", () => {
  const title = pubPreviewTitle.value.trim();
  const desc = pubPreviewDescription.value.trim();
  const tags = pubPreviewHashtags.value.trim();

  const fullText = `${title}\n\n${desc}${tags ? `\n\n${tags}` : ""}`;
  navigator.clipboard.writeText(fullText).then(() => {
    showToast("Teks copywriting berhasil disalin ke clipboard!");
  }).catch(() => {
    showToast("Gagal menyalin secara otomatis.", true);
  });
});

// Confirm publication
document.getElementById("btnConfirmPublishSubmit").addEventListener("click", async () => {
  if (!currentPublishProductId || !currentPublishPlatform) return;

  const payload = {
    external_url: pubConfirmUrl.value.trim() || null,
    notes: pubConfirmNotes.value.trim() || null
  };

  try {
    await api(`/api/products/${currentPublishProductId}/publish/${currentPublishPlatform}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    showToast(`Status publikasi di ${currentPublishPlatform.toUpperCase()} berhasil dikonfirmasi!`);
    publishModal.classList.add("hidden");
    loadPublications();
  } catch (err) {
    showToast(err.message, true);
  }
});

// Reset publication status
document.getElementById("btnResetPublishStatus").addEventListener("click", async () => {
  if (!currentPublishProductId || !currentPublishPlatform) return;
  if (!confirm("Reset status publikasi produk ini?")) return;

  try {
    await api(`/api/products/${currentPublishProductId}/publish/${currentPublishPlatform}/reset`, {
      method: "POST"
    });
    showToast("Status publikasi berhasil di-reset.");
    publishModal.classList.add("hidden");
    loadPublications();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ==================== INVENTORY SYNC & SALES HISTORY ====================
let currentSoldProductId = null;

const soldModal = document.getElementById("soldModal");
const soldForm = document.getElementById("soldForm");
const unpublishChecklistModal = document.getElementById("unpublishChecklistModal");
const unpublishTableBody = document.getElementById("unpublishTableBody");

document.getElementById("btnCloseSoldModal").addEventListener("click", () => soldModal.classList.add("hidden"));
document.getElementById("btnCancelSoldModal").addEventListener("click", () => soldModal.classList.add("hidden"));
document.getElementById("btnCloseUnpublishModal").addEventListener("click", () => unpublishChecklistModal.classList.add("hidden"));
document.getElementById("btnDoneUnpublish").addEventListener("click", () => unpublishChecklistModal.classList.add("hidden"));

window.openSoldModal = async function(productId) {
  currentSoldProductId = productId;
  soldForm.reset();
  try {
    const prod = await api(`/api/products/${productId}`);
    document.getElementById("soldModalTitle").textContent = `Tandai Terjual: ${prod.name}`;
    document.getElementById("soldProductId").value = prod.id;
    document.getElementById("soldPriceInput").value = prod.price || 0;
    soldModal.classList.remove("hidden");
  } catch (err) {
    showToast(err.message, true);
  }
};

soldForm.addEventListener("submit", async e => {
  e.preventDefault();
  if (!currentSoldProductId) return;

  const payload = {
    channel: document.getElementById("soldChannelSelect").value,
    sold_price: parseFloat(document.getElementById("soldPriceInput").value) || 0,
    buyer_note: document.getElementById("soldBuyerNote").value.trim() || null
  };

  try {
    const result = await api(`/api/products/${currentSoldProductId}/mark-sold`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    soldModal.classList.add("hidden");
    showToast("Barang berhasil ditandai terjual!");
    loadProducts();
    loadDashboard();

    // Jika ada kanal lain yang perlu ditarik, buka modal pengingat penarikan
    if (result.channels_to_unpublish && result.channels_to_unpublish.length > 0) {
      document.getElementById("unpublishModalSubtitle").textContent =
        `Barang '${result.product_name}' laku di kanal ${result.sold_channel.toUpperCase()}.`;

      unpublishTableBody.innerHTML = result.channels_to_unpublish.map(item => {
        const linkHtml = item.external_url
          ? `<a href="${item.external_url}" target="_blank" rel="noopener noreferrer" style="font-size:11px; color:var(--accent); display:block; margin-top:4px;">Buka Listing ↗</a>`
          : "";

        return `
          <tr id="unpubRow_${item.platform}">
            <td><b>${escapeHtml(item.platform_name)}</b></td>
            <td>
              <span style="font-size:12px;">${escapeHtml(item.instruction)}</span>
              ${linkHtml}
            </td>
            <td>
              <button class="btn btn-danger btn-sm" onclick="handleUnpublishChannel(${result.product_id}, '${item.platform}')">Tandai Ditarik</button>
            </td>
          </tr>
        `;
      }).join("");

      unpublishChecklistModal.classList.remove("hidden");
    }
  } catch (err) {
    showToast(err.message, true);
  }
});

window.handleUnpublishChannel = async function(productId, platform) {
  try {
    await api(`/api/products/${productId}/unpublish-channel/${platform}`, { method: "POST" });
    const row = document.getElementById(`unpubRow_${platform}`);
    if (row) {
      const btnCell = row.querySelector("td:last-child");
      if (btnCell) {
        btnCell.innerHTML = `<span class="badge badge-active">✓ Ditarik</span>`;
      }
    }
    showToast(`Listing di ${platform.toUpperCase()} berhasil ditandai ditarik.`);
  } catch (err) {
    showToast(err.message, true);
  }
};

async function loadHistory() {
  const tbody = document.getElementById("historyTableBody");
  tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align:center; padding:30px;">Memuat riwayat penjualan...</td></tr>`;

  try {
    const data = await api("/api/history");
    document.getElementById("historyTotalSold").textContent = data.total_sold_items;
    document.getElementById("historyTotalRevenue").textContent = formatRupiah(data.total_revenue);

    const breakdown = data.channel_breakdown || {};
    let topChan = "—";
    let topCount = 0;
    for (const [ch, count] of Object.entries(breakdown)) {
      if (count > topCount) {
        topCount = count;
        topChan = `${ch.toUpperCase()} (${count} item)`;
      }
    }
    document.getElementById("historyTopChannel").textContent = topChan;

    if (!data.recent_sales || data.recent_sales.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align:center; padding:30px;">Belum ada catatan transaksi penjualan.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.recent_sales.map(s => {
      const dateStr = s.created_at ? new Date(s.created_at).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" }) : "—";
      const chanBadge = s.channel ? `<span class="badge badge-brand">${escapeHtml(s.channel.toUpperCase())}</span>` : "—";

      return `
        <tr>
          <td><small class="muted">${dateStr}</small></td>
          <td><b>${escapeHtml(s.product_name)}</b></td>
          <td>${chanBadge}</td>
          <td><b>${formatRupiah(s.sold_price)}</b></td>
          <td><span style="font-size:12px; color:#475467;">${escapeHtml(s.buyer_note || "—")}</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(err.message, true);
  }
}

// ==================== AUTH & BOOTSTRAP ====================
document.getElementById("loginForm").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.currentTarget);
  const body = new URLSearchParams(fd);
  try {
    await api("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });
    showApp();
    await loadDashboard();
  } catch (err) {
    document.getElementById("loginError").textContent = err.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  try {
    await api("/api/logout", { method: "POST" });
  } finally {
    showLogin();
  }
});

// Auto login check on page load
(async () => {
  try {
    const s = await api("/api/session");
    if (s.authenticated) {
      if (s.username) {
        document.getElementById("userNameDisplay").textContent = s.username;
        document.getElementById("userAvatar").textContent = s.username.charAt(0).toUpperCase();
      }
      showApp();
      await loadDashboard();
    } else {
      showLogin();
    }
  } catch {
    showLogin();
  }
})();
