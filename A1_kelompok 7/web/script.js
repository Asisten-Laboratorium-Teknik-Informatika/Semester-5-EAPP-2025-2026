// Di awal script.js, tambahkan:
document.addEventListener("DOMContentLoaded", function () {
  console.log("Page loaded:", currentPage());
});

// Tambahkan error handling untuk semua eel calls
async function safeEelCall(eelFunction, ...args) {
  try {
    return await eelFunction(...args)();
  } catch (error) {
    console.error("Eel call failed:", error);
    alert("Terjadi kesalahan sistem");
    return { ok: false };
  }
}
// -----------------------------------------
// FIXED UNIVERSAL NAVIGATION
// -----------------------------------------
function goHome() {
  window.location.href = "index.html";
}
function goToDonor() {
  window.location.href = "donatur.html";
}
function backToLogin() {
  window.location.href = "index.html";
}

// -----------------------------------------
// HELPER — DETECT FILE NAME
// -----------------------------------------
function currentPage() {
  return window.location.pathname.split("/").pop();
}

// -----------------------------------------
// LOGIN PAGE (index.html)
// -----------------------------------------
if (currentPage() === "index.html") {
  const btn = document.getElementById("btnLogin");

  btn?.addEventListener("click", async () => {
    const u = document.getElementById("username").value.trim();
    const p = document.getElementById("password").value.trim();

    const res = await eel.api_login(u, p)();
    if (res.ok) {
      sessionStorage.setItem("user", JSON.stringify(res.user));
      window.location.href = "donatur.html";
    } else {
      alert(res.message || "Login gagal");
    }
  });
}

// -----------------------------------------
// DONATUR PAGE (donatur.html)
// -----------------------------------------
if (currentPage() === "donatur.html") {
  document.getElementById("btnSaveDonatur")?.addEventListener("click", async () => {
    const name = document.getElementById("donor_name").value.trim();
    const contact = document.getElementById("donor_contact").value.trim();
    const amount = document.getElementById("donor_amount").value.trim() || "0";

    if (!name) {
      alert("Nama donor wajib");
      return;
    }

    const r = await eel.api_add_donatur(name, contact)();
    if (r.ok) {
      sessionStorage.setItem("last_donatur_id", r.donatur_id);
      sessionStorage.setItem("last_donatur_amount", amount);

      window.location.href = "penerima.html";
    } else {
      alert("Gagal menyimpan donatur");
    }
  });
}

// -----------------------------------------
// DAFTAR PANTI PAGE (daftar_panti.html)
// -----------------------------------------
// Update bagian daftar panti di script.js
if (currentPage() === "daftar_panti.html") {
  const form = document.getElementById("formPanti");

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const nama = document.getElementById("namaPanti").value.trim();
    const alamat = document.getElementById("alamatPanti").value.trim();
    const kontak = document.getElementById("kontakPanti").value.trim();

    if (!nama) {
      alert("Nama panti wajib diisi");
      return;
    }

    const res = await eel.api_add_panti(nama, alamat, kontak)();
    if (res.ok) {
      alert("Panti berhasil disimpan!");
      form.reset();
      loadPantiList();
    } else {
      alert("Gagal menyimpan panti");
    }
  });

  async function loadPantiList() {
    try {
      const data = await eel.api_get_all_panti()();
      const tbody = document.querySelector("#tabelPanti");
      const pantiCount = document.getElementById("pantiCount");
      const totalPanti = document.getElementById("totalPanti");

      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="3" class="text-center" style="color: #6c757d; font-style: italic;">
              Belum ada panti terdaftar. Tambahkan panti pertama.
            </td>
          </tr>`;
      } else {
        data.forEach((p) => {
          tbody.innerHTML += `
            <tr>
              <td><strong>${p.nama}</strong></td>
              <td>${p.alamat || "-"}</td>
              <td>${p.kontak || "-"}</td>
            </tr>`;
        });
      }

      pantiCount.textContent = data.length + " Panti";
      totalPanti.textContent = data.length;
    } catch (error) {
      console.error("Error loading panti list:", error);
    }
  }

  // Load data when page loads
  document.addEventListener("DOMContentLoaded", function () {
    loadPantiList();
  });
}

// -----------------------------------------
// PENERIMA PAGE (penerima.html)
// -----------------------------------------
if (currentPage() === "penerima.html") {
  const select = document.getElementById("pantiSelect");

  async function loadPantiSelect() {
    const data = await eel.api_get_all_panti()();
    select.innerHTML = `<option value="">-- Pilih Panti Terdaftar --</option>`;
    data.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.nama;
      select.appendChild(opt);
    });
  }

  document.getElementById("btnSaveReceiver")?.addEventListener("click", async () => {
    const nama = document.getElementById("receiver_name").value.trim();
    const need = document.getElementById("receiver_need").value.trim();
    const panti_id = select.value;

    if (!nama || !need || !panti_id) {
      alert("Lengkapi semua data");
      return;
    }

    const r = await eel.api_add_penerima(nama, need, Number(panti_id))();
    if (!r.ok) {
      alert("Gagal menambah penerima");
      return;
    }

    const donatur_id = sessionStorage.getItem("last_donatur_id");
    const jumlah = sessionStorage.getItem("last_donatur_amount") || 0;

    if (donatur_id) {
      await eel.api_record_donation(Number(donatur_id), r.penerima_id, jumlah, "")();

      sessionStorage.removeItem("last_donatur_id");
      sessionStorage.removeItem("last_donatur_amount");
    }

    alert("Penerima & donasi tersimpan!");
    window.location.href = "donasi.html";
  });

  loadPantiSelect();
}

// -----------------------------------------
// DONASI PAGE (donasi.html)
// -----------------------------------------
// Update bagian donasi di script.js
if (currentPage() === "donasi.html") {
  async function loadDonations() {
    try {
      const rows = await eel.api_get_donations()();
      const tbody = document.querySelector("#donasiTable tbody");

      tbody.innerHTML = "";

      if (rows.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center" style="color: #6c757d; font-style: italic;">
              Belum ada data donasi. Mulai dengan menambahkan donatur pertama.
            </td>
          </tr>`;
        return;
      }

      let total = 0;
      rows.forEach((r, idx) => {
        total += parseFloat(r[3] || 0);
        const date = new Date(r[4]);
        const formattedDate = date.toLocaleDateString("id-ID", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
        });

        tbody.innerHTML += `
          <tr>
            <td>${idx + 1}</td>
            <td><strong>${r[1]}</strong></td>
            <td>${r[2]}</td>
            <td style="color: #28a745; font-weight: 600;">Rp ${Number(r[3]).toLocaleString()}</td>
            <td>${formattedDate}</td>
            <td><span class="status-badge status-completed">Selesai</span></td>
          </tr>`;
      });

      // Update stats
      const summary = await eel.api_get_summary()();
      document.getElementById("totalDonasi").innerText = "Rp " + Number(summary.total).toLocaleString();
      document.getElementById("totalDonatur").innerText = summary.donors;
      document.getElementById("totalPenerima").innerText = summary.recipients;
      document.getElementById("totalTransaksi").innerText = rows.length;
    } catch (error) {
      console.error("Error loading donations:", error);
      const tbody = document.querySelector("#donasiTable tbody");
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center" style="color: #dc3545;">
            Error memuat data. Silakan refresh halaman.
          </td>
        </tr>`;
    }
  }

  // Load data when page loads
  document.addEventListener("DOMContentLoaded", function () {
    loadDonations();
  });
}
