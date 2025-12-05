//----------------------------------------------------
// GLOBAL VARIABLES
//----------------------------------------------------
let user_id = sessionStorage.getItem("user_id");
let foodDB = [];        // data mentah dari Python: [ [nama, kalori_per100], ... ]
let calorieDB = {};     // mapping: nama(lowercase) -> kalori_per100
let foodData = [];      // list makanan yg user input (untuk tabel)
let editIndex = -1;     // index data yang sedang diedit

// konversi unit ke gram
const unitGram = {
    "piring": 150,
    "buah": 100,
    "potong": 80,
    "porsi": 50,
};

// helper: qty + unit -> gram total
function toGram(qty, unit) {
    const u = (unit || "").toLowerCase().trim();
    const perUnit = unitGram[u] || 100;
    return qty * perUnit;
}


//----------------------------------------------------
// ON LOAD
//----------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    // refresh user_id setiap load halaman
    user_id = sessionStorage.getItem("user_id");

    setupLogin();
    setupRegister();
    setupBMIPage();
    setupBmiHistoryPage();
    loadFoodDatabase();
    setupCaloriePage();
});


//----------------------------------------------------
// NAVIGASI
//----------------------------------------------------
function go(page) {
    window.location.href = page;
}


//----------------------------------------------------
// LOAD FOOD DATABASE (food_database)
//----------------------------------------------------
function loadFoodDatabase() {
    if (!window.eel || !eel.get_all_food) return;

    eel.get_all_food()(function(data) {
        // data: [ ["Nasi Putih", 175], ["Ayam Goreng", 260], ...]
        foodDB = data;
        calorieDB = {};

        data.forEach(row => {
            const nama = String(row[0]).toLowerCase();
            const kal = Number(row[1]);
            calorieDB[nama] = kal;
        });

        console.log("✓ Food Database Loaded:", calorieDB);
    });
}


//----------------------------------------------------
// REGISTER
//----------------------------------------------------
function setupRegister() {
    const btn = document.getElementById("reg-btn");
    if (!btn) return;

    btn.addEventListener("click", () => {
        let name = document.getElementById("reg-name").value.trim();
        let email = document.getElementById("reg-email").value.trim();
        let pass  = document.getElementById("reg-password").value.trim();

        eel.register(name, email, pass)(function(res) {
            if (res === "success") {
                alert("Registrasi berhasil!");
                go("signin.html");
            } else if (res === "exists") {
                alert("Email sudah digunakan!");
            } else if (res === "empty") {
                alert("Lengkapi semua data!");
            } else {
                alert("Terjadi kesalahan saat registrasi.");
            }
        });
    });
}


//----------------------------------------------------
// LOGIN
//----------------------------------------------------
function setupLogin() {
    const btn = document.getElementById("login-btn");
    if (!btn) return;

    btn.addEventListener("click", () => {
        let email = document.getElementById("login-email").value.trim();
        let pass  = document.getElementById("login-password").value.trim();

        eel.login(email, pass)(function(response) {
            console.log("Login response:", response);

            if (response.status === "success") {
                sessionStorage.setItem("user_id", response.user_id);
                go("home.html");
            } else if (response.status === "invalid") {
                alert("Email atau password salah!");
            } else if (response.status === "empty") {
                alert("Isi email & password!");
            } else {
                alert("Gagal login. Cek koneksi database.");
            }
        });
    });
}


//----------------------------------------------------
// BMI PAGE (hitung + simpan ke DB)
//----------------------------------------------------
function setupBMIPage() {
    const btn = document.querySelector(".bmi-btn");
    if (!btn) return; // bukan di halaman BMI

    btn.addEventListener("click", () => {
        const inputs = document.querySelectorAll(".bmi-input");

        let usia   = Number(inputs[0].value);   // tidak disimpan ke DB, cuma dipakai di UI
        let tinggi = Number(inputs[1].value);
        let berat  = Number(inputs[2].value);

        if (!usia || !tinggi || !berat) {
            alert("Isi semua data BMI!");
            return;
        }

        let tinggiM = tinggi / 100;
        let bmi = berat / (tinggiM * tinggiM);

        let kategori = "";
        if (bmi < 18.5) kategori = "Kurus";
        else if (bmi < 25) kategori = "Normal";
        else if (bmi < 30) kategori = "Overweight";
        else kategori = "Obesitas";

        alert(`BMI: ${bmi.toFixed(1)} (${kategori})`);

        if (!user_id) {
            console.warn("User belum login, BMI tidak disimpan.");
            return;
        }

        // SIMPAN BMI KE DATABASE 💾
        eel.save_bmi(user_id, berat, tinggi)(function(res) {
            console.log("SAVE BMI RESULT:", res);
            if (res.status === "bmi_saved") {
                alert("BMI kamu berhasil disimpan!");
            } else {
                alert("BMI tidak tersimpan. Cek koneksi / server.");
            }
        });
    });
}


//----------------------------------------------------
// BMI HISTORY PAGE (Chart.js)
//----------------------------------------------------
function setupBmiHistoryPage() {
    const canvas = document.getElementById("bmiChart");
    if (!canvas) return; // bukan di halaman BMI history

    if (!user_id) {
        console.warn("User belum login, tidak bisa load bmi history.");
        return;
    }

    loadBmiHistory(canvas);
}

function loadBmiHistory(canvasElem) {
    eel.get_bmi_history(user_id)(function(data){
        console.log("BMI HISTORY:", data);

        if (!Array.isArray(data) || data.length === 0) {
            console.log("Belum ada data BMI.");
            return;
        }

        const tanggal = data.map(x => x.tanggal);
        const bmiValue = data.map(x => x.bmi);

        const ctx = canvasElem.getContext("2d");

        // pastikan Chart.js sudah di-include di HTML:
        // <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        new Chart(ctx, {
            type: "line",
            data: {
                labels: tanggal,
                datasets: [{
                    label: "BMI History",
                    data: bmiValue,
                    borderColor: "blue",
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    });
}


//----------------------------------------------------
// CALORIE PAGE
//----------------------------------------------------
function setupCaloriePage() {
    const addBtn   = document.querySelector(".add-btn");
    const saveBtn  = document.querySelector(".save-btn");
    const editBtn  = document.querySelector(".edit-btn");
    const exitBtn  = document.querySelector(".exit-btn");

    const analysisTable = document.querySelector(".analysis-table");
    const circleInner   = document.querySelector(".circle-inner");
    const resultValue   = document.querySelector(".result-value");

    const kategoriInput   = document.querySelector(".food-kategori");
    const namaInput       = document.getElementById("food-input");
    const qtyInput        = document.querySelector(".food-qty");
    const unitInput       = document.querySelector(".food-unit");
    const autocompleteBox = document.getElementById("food-list");

    // kalau bukan di halaman calorie, stop
    if (!addBtn || !analysisTable || !namaInput) return;


    //----------------------------------------------------
    // AUTOCOMPLETE NAMA MAKANAN
    //----------------------------------------------------
    namaInput.addEventListener("input", () => {
        const key = namaInput.value.toLowerCase();
        autocompleteBox.innerHTML = "";

        if (key.length < 1) {
            autocompleteBox.style.display = "none";
            return;
        }

        const hasil = Object.keys(calorieDB).filter(nama => nama.includes(key));

        if (hasil.length === 0) {
            autocompleteBox.style.display = "none";
            return;
        }

        hasil.forEach(nama => {
            const div = document.createElement("div");
            const kalPer100 = calorieDB[nama] ?? 0;

            div.textContent = `${nama} (${kalPer100} kcal/100g)`;
            div.onclick = () => {
                let found = foodDB.find(f => f[0].toLowerCase() === nama);
                namaInput.value = found ? found[0] : nama;
                autocompleteBox.innerHTML = "";
                autocompleteBox.style.display = "none";
            };

            autocompleteBox.appendChild(div);
        });

        autocompleteBox.style.display = "block";
    });

    // klik di luar -> tutup box autocomplete
    document.addEventListener("click", (e) => {
        if (e.target !== namaInput && e.target.parentNode !== autocompleteBox) {
            autocompleteBox.style.display = "none";
        }
    });


    //----------------------------------------------------
    // RESET INPUT FORM
    //----------------------------------------------------
    function resetForm() {
        kategoriInput.value = "";
        namaInput.value     = "";
        qtyInput.value      = "";
        unitInput.value     = "";
        editIndex = -1;
    }


    //----------------------------------------------------
    // RENDER TABEL
    //----------------------------------------------------
    function updateTable() {
        let html = `
            <tr>
                <th>Kategori</th>
                <th>Nama</th>
                <th>Quantity</th>
                <th>Unit</th>
            </tr>`;

        foodData.forEach((item) => {
            html += `
                <tr onclick="fillForm('${item.nama}')">
                    <td>${item.kategori}</td>
                    <td>${item.nama}</td>
                    <td>${item.qty}</td>
                    <td>${item.unit}</td>
                </tr>`;
        });

        analysisTable.innerHTML = html;
    }


    //----------------------------------------------------
    // ISI FORM SAAT KLIK BARIS
    //----------------------------------------------------
    window.fillForm = function(nama) {
        nama = nama.toLowerCase();
        const item = foodData.find(x => x.nama === nama);
        if (item) {
            kategoriInput.value = item.kategori;
            namaInput.value     = item.nama;
            qtyInput.value      = item.qty;
            unitInput.value     = item.unit;
        }
    };


    //----------------------------------------------------
    // TOMBOL "TAMBAH"
    //----------------------------------------------------
    addBtn.addEventListener("click", (e) => {
        e.preventDefault();

        let kategori = kategoriInput.value.trim();
        let namaRaw  = namaInput.value.trim();
        let qty      = Number(qtyInput.value);
        let unit     = unitInput.value.trim();

        if (!kategori || !namaRaw || !qty || !unit) {
            alert("Isi semua data makanan!");
            return;
        }

        if (!user_id) {
            alert("Silakan login terlebih dahulu.");
            return;
        }

        console.log("➡ Menyimpan data makanan...");

        const nama = namaRaw.toLowerCase();
        const qtyGram = toGram(qty, unit);
        const baseKalori = calorieDB[nama] || 0;
        const totalKalori = (qtyGram / 100) * baseKalori;

        // SIMPAN KE food_log
        eel.save_food_log(user_id, kategori, namaRaw, qtyGram, unit, totalKalori)(function(res) {
            console.log("✓ save_food_log (Tambah):", res);
        });

        foodData.push({ kategori, nama, qty, unit });
        updateTable();
        resetForm();
    });


    //----------------------------------------------------
    // TOMBOL "EDIT"
    //----------------------------------------------------
    editBtn.addEventListener("click", () => {
        const namaDicari = namaInput.value.trim().toLowerCase();
        const index = foodData.findIndex(x => x.nama === namaDicari);

        if (index === -1) {
            alert("Klik baris di tabel dulu!");
            return;
        }

        editIndex = index;
        const item = foodData[index];

        kategoriInput.value = item.kategori;
        namaInput.value     = item.nama;
        qtyInput.value      = item.qty;
        unitInput.value     = item.unit;
    });


    //----------------------------------------------------
    // TOMBOL "SIMPAN"
    //----------------------------------------------------
    saveBtn.addEventListener("click", () => {
        let kategori = kategoriInput.value.trim();
        let namaRaw  = namaInput.value.trim();
        let qty      = Number(qtyInput.value);
        let unit     = unitInput.value.trim();

        if (!kategori || !namaRaw || !qty || !unit) {
            alert("Isi semua data!");
            return;
        }

        if (!user_id) {
            alert("Silakan login terlebih dahulu.");
            return;
        }

        const nama = namaRaw.toLowerCase();
        const qtyGram = toGram(qty, unit);
        const baseKalori = calorieDB[nama] || 0;
        const totalKalori = (qtyGram / 100) * baseKalori;

        // jika editIndex aktif, update data lokal
        if (editIndex !== -1) {
            foodData[editIndex] = { kategori, nama, qty, unit };
            editIndex = -1;
        } else {
            foodData.push({ kategori, nama, qty, unit });
        }

        // SIMPAN KE DATABASE
        eel.save_food_log(user_id, kategori, namaRaw, qtyGram, unit, totalKalori)(function(res) {
            console.log("✓ save_food_log (Simpan):", res);
        });

        updateTable();
        resetForm();
    });


    //----------------------------------------------------
    // TOMBOL "KELUAR" / RESET
    //----------------------------------------------------
    exitBtn.addEventListener("click", resetForm);


    //----------------------------------------------------
    // TOMBOL "ANALYZE"
    //----------------------------------------------------
    const analyzeBtn = document.querySelector(".analyze-btn");
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", () => {
            if (foodData.length === 0) {
                alert("Tidak ada data!");
                return;
            }

            let totalKalori = 0;
            let totalGram = 0;

            foodData.forEach(item => {
                const base = calorieDB[item.nama] || 0;
                const qtyGram = toGram(item.qty, item.unit);

                totalKalori += (qtyGram / 100) * base;
                totalGram   += qtyGram;
            });

            if (circleInner) {
                circleInner.textContent = `${Math.round(totalKalori)} KCAL`;
            }
            if (resultValue) {
                resultValue.textContent = `${totalGram} Gram`;
            }
        });
    }
}
