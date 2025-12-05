let foodsData = [];
let currentPage = 1;
const itemsPerPage = 5;

async function loginUser(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const result = await eel.login_user(email, password)();

  if (result === "success") {
    alert("Login berhasil!");
    window.location.href = "index.html";
  } else if (result === "wrong_password") {
    alert("Password salah!");
  } else {
    alert("Email tidak ditemukan!");
  }
}

async function registerUser(event) {
  event.preventDefault();
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const result = await eel.register_user(name, email, password)();
  if (result === "success") {
    alert("Registrasi berhasil!");
    window.location.href = "login.html";
  }
}

async function updateProfile(event) {
  event.preventDefault();

  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;

  const result = await eel.update_profile(email, name)();
  const message = document.querySelector(".success-message");

  if (result === "success") {
    message.style.display = "inline";
    message.textContent = "Saved.";
    setTimeout(() => (message.style.display = "none"), 2000);
  } else {
    alert("Gagal memperbarui profil!");
  }
}

/* ============================================
   FIXED DATE PARSER — agar tidak kembali ke 1970
   ============================================ */
function fixDate(str) {
  if (!str) return null;

  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    str += "T00:00:00";
  }

  return new Date(str);
}

/* ============================================
   FORMAT TANGGAL
   ============================================ */
function formatDate(dateString) {
  const d = fixDate(dateString);
  if (!d || isNaN(d)) return "-";

  return d.toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

/* ============================================
   KATEGORI EXPIRED
   ============================================ */
function getExpiredCategory(expiredDate) {
  const exp = fixDate(expiredDate);
  if (!exp) return "safe";

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const expDate = new Date(exp.getFullYear(), exp.getMonth(), exp.getDate());

  const diffDays = Math.floor((expDate - today) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return "expired"; // sudah lewat
  if (diffDays <= 3) return "soon"; // ≤ 3 hari lagi
  return "safe";
}

/* ============================================
   STATUS BADGE
   ============================================ */
function getStatusBadge(expiredDate) {
  const exp = fixDate(expiredDate);
  if (!exp || isNaN(exp)) return `<span class="badge bg-secondary">Tidak diketahui</span>`;

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const expDate = new Date(exp.getFullYear(), exp.getMonth(), exp.getDate());

  const diffDays = Math.floor((expDate - today) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return `<span class="badge bg-danger">Sudah Expired</span>`;
  }

  if (diffDays <= 3) {
    return `<span class="badge bg-warning text-dark">Segera Expired</span>`;
  }

  return `<span class="badge bg-success">Masih Aman</span>`;
}

/* ============================================
   LOAD DATA MAKANAN
   ============================================ */
async function loadFoods() {
  const params = new URLSearchParams(window.location.search);

  const keyword = params.get("keyword")?.toLowerCase() || "";
  const filter = params.get("filter") || "";
  const sortBy = params.get("sort_by") || "";
  const sortOrder = params.get("sort_order") || "asc";
  const expiredFrom = params.get("expired_from") || "";
  const expiredTo = params.get("expired_to") || "";

  // Ambil data dari backend
  foodsData = await eel.get_foods_by_user()();

  // 1. FILTER — berdasarkan keyword
  if (keyword) {
    foodsData = foodsData.filter((food) => food.nama_makanan.toLowerCase().includes(keyword));
  }

  // 2. FILTER — expired category
  if (filter) {
    foodsData = foodsData.filter((food) => getExpiredCategory(food.tanggal_expired) === filter);
  }

  // 3. FILTER — expired date range
  if (expiredFrom) {
    foodsData = foodsData.filter((food) => fixDate(food.tanggal_expired) >= fixDate(expiredFrom));
  }

  if (expiredTo) {
    foodsData = foodsData.filter((food) => fixDate(food.tanggal_expired) <= fixDate(expiredTo));
  }

  // 4. SORTING
  if (sortBy === "tanggal_expired") {
    foodsData.sort((a, b) => {
      const d1 = fixDate(a.tanggal_expired);
      const d2 = fixDate(b.tanggal_expired);
      return sortOrder === "asc" ? d1 - d2 : d2 - d1;
    });
  }

  if (sortBy === "created") {
    foodsData.sort((a, b) => {
      const d1 = fixDate(a.tanggal_dibuat);
      const d2 = fixDate(b.tanggal_dibuat);
      return sortOrder === "asc" ? d1 - d2 : d2 - d1;
    });
  }

  // RESET PAGE
  currentPage = 1;

  // RENDER
  renderFoods();
  renderPagination(foodsData.length);
}

/* ============================================
   TAMBAH MAKANAN
   ============================================ */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("foodForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const nama = document.getElementById("nama_makanan").value;
      const jumlah = document.getElementById("jumlah").value;
      const expired = document.getElementById("tanggal_expired").value;

      const result = await eel.add_food(nama, jumlah, expired)();

      if (result === "success") {
        alert("Makanan berhasil ditambahkan!");
        window.location.href = "index.html";
      } else if (result === "not_logged_in") {
        alert("Harap login terlebih dahulu!");
        window.location.href = "login.html";
      } else {
        alert("Gagal menambahkan makanan.");
      }
    });
  }
});

/* ============================================
   LOAD DATA EDIT
   ============================================ */
async function loadEditFood() {
  const id = new URLSearchParams(window.location.search).get("id");
  if (!id) return;

  const food = await eel.get_food_by_id(parseInt(id))();

  if (!food) {
    alert("Data makanan tidak ditemukan!");
    window.location.href = "index.html";
    return;
  }

  document.getElementById("nama_makanan").value = food.nama_makanan;
  document.getElementById("jumlah").value = food.jumlah;
  document.getElementById("tanggal_expired").value = food.tanggal_expired;
}

/* ============================================
   UPDATE MAKANAN
   ============================================ */
async function updateFood(event) {
  event.preventDefault();

  const id = new URLSearchParams(window.location.search).get("id");
  const nama = document.getElementById("nama_makanan").value;
  const jumlah = document.getElementById("jumlah").value;
  const expired = document.getElementById("tanggal_expired").value;

  const result = await eel.update_food(parseInt(id), nama, jumlah, expired)();

  if (result === "success") {
    alert("Data makanan berhasil diperbarui!");
    window.location.href = "index.html";
  } else {
    alert("Gagal memperbarui makanan.");
  }
}

/* ============================================
   HAPUS MAKANAN
   ============================================ */
async function deleteFood(id) {
  if (!confirm("Yakin ingin menghapus makanan ini?")) return;

  const result = await eel.delete_food(id)();

  if (result === "success") {
    alert("Makanan berhasil dihapus!");
    loadFoods();
  } else {
    alert("Gagal menghapus makanan.");
  }
}

/* ============================================
   JALANKAN EDIT MODE
   ============================================ */
if (window.location.pathname.includes("edit.html")) {
  document.addEventListener("DOMContentLoaded", () => {
    loadEditFood();

    const form = document.getElementById("foodFormEdit");
    if (form) form.addEventListener("submit", updateFood);
  });
}

/* ============================================
   RUN AUTO LOAD DATA DI HALAMAN INDEX
   ============================================ */
if (window.location.pathname.includes("index.html")) {
  document.addEventListener("DOMContentLoaded", loadFoods);
}

async function updatePassword(event) {
  event.preventDefault();

  const current = document.getElementById("current_password").value;
  const password = document.getElementById("password").value;
  const confirm = document.getElementById("password_confirmation").value;

  if (password !== confirm) {
    alert("Password baru tidak sama!");
    return;
  }

  const result = await eel.update_password(current, password)();

  if (result === "success") {
    document.getElementById("saved2").classList.remove("d-none");
    setTimeout(() => document.getElementById("saved2").classList.add("d-none"), 2000);

    document.getElementById("current_password").value = "";
    document.getElementById("password").value = "";
    document.getElementById("password_confirmation").value = "";
  } else if (result === "wrong_password") {
    alert("Password lama salah!");
  } else {
    alert("Gagal memperbarui password!");
  }
}

async function deleteAccount(event) {
  event.preventDefault();

  const password = document.getElementById("delete_password").value;
  if (!password) return;

  const result = await eel.delete_account(password)();

  if (result === "success") {
    alert("Akun berhasil dihapus.");
    window.location.href = "register.html";
  } else if (result === "wrong_password") {
    alert("Password salah!");
  } else {
    alert("Gagal menghapus akun.");
  }
}

function renderPagination(totalItems) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  if (totalPages <= 1) return; // Tidak tampil kalau cuma 1 halaman

  let html = `<nav><ul class="pagination">`;

  // Prev
  html += `
    <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
      <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">«</a>
    </li>
  `;

  // Number buttons
  for (let i = 1; i <= totalPages; i++) {
    html += `
      <li class="page-item ${i === currentPage ? "active" : ""}">
        <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
      </li>
    `;
  }

  // Next
  html += `
    <li class="page-item ${currentPage === totalPages ? "disabled" : ""}">
      <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">»</a>
    </li>
  `;

  html += `</ul></nav>`;
  pagination.innerHTML = html;
}

function renderFoods() {
  const tbody = document.querySelector("tbody");
  tbody.innerHTML = "";

  if (foodsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center">Belum ada data makanan.</td></tr>`;
    return;
  }

  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;

  const pageItems = foodsData.slice(start, end);

  pageItems.forEach((food, index) => {
    const category = getExpiredCategory(food.tanggal_expired);
    const statusBadge = getStatusBadge(food.tanggal_expired);

    tbody.innerHTML += `
      <tr>
        <td>${start + index + 1}</td>
        <td>${food.nama_makanan}</td>
        <td>${food.jumlah}</td>
        <td>${formatDate(food.tanggal_dibuat)}</td>
        <td>${food.tanggal_edit ? formatDate(food.tanggal_edit) : "-"}</td>
        <td>${statusBadge}<br><small>${formatDate(food.tanggal_expired)}</small></td>
        <td>
          <a href="edit.html?id=${food.id}" class="btn btn-sm btn-warning">Edit</a>
          <button class="btn btn-sm btn-danger" onclick="deleteFood(${food.id})">Hapus</button>
        </td>
      </tr>
    `;
  });
}

async function logoutUser() {
  const result = await eel.logout()();

  if (result === "success") {
    window.location.href = "login.html"; // balik ke login
  }
}

function changePage(page) {
  currentPage = page;
  renderFoods(); // tampilkan hanya data halaman ini
  renderPagination(foodsData.length);
}
