let activeCategory = 'All';
let stockChart = null;

window.onload = () => {
    console.log("Aplikasi siap. Menunggu user login...");
};

// --- DATA HANDLING ---
async function loadData() {
    const btn = document.querySelector('.refresh-btn');
    if(btn) { btn.disabled = true; btn.style.opacity = "0.5"; }

    try {
        let rawData = await eel.get_products_frontend()();
        let products = (typeof rawData === 'string') ? JSON.parse(rawData) : rawData;

        // 1. UPDATE STATISTIK (Tetap menghitung SEMUA data, tidak terpengaruh filter)
        let totalStock = 0, totalSales = 0, totalAsset = 0;
        products.forEach(p => {
            totalStock += parseInt(p.stock);
            totalSales += parseInt(p.sales);
            totalAsset += (parseInt(p.stock) * parseFloat(p.price));
        });
        document.getElementById('stat-stock').innerText = totalStock;
        document.getElementById('stat-sales').innerText = totalSales;
        document.getElementById('stat-asset').innerText = "Rp " + totalAsset.toLocaleString();
        
        // Update Chart
        updateChart(products);


        // 2. GENERATE FILTER BUTTONS (DINAMIS)
        // Ambil kategori unik dari data produk
        const categories = ['All', ...new Set(products.map(p => p.category))];
        const filterContainer = document.getElementById('filter-container');
        
        // Simpan tombol yang ada sekarang agar tidak flicker (kedip) parah
        // Kita hanya render ulang tombol jika jumlah kategori berubah
        if (filterContainer.childElementCount !== categories.length) {
            filterContainer.innerHTML = '';
            categories.forEach(cat => {
                const button = document.createElement('button');
                button.className = `filter-btn ${cat === activeCategory ? 'active' : ''}`;
                button.innerText = cat;
                button.onclick = () => {
                    activeCategory = cat; // Set kategori aktif
                    loadData(); // Reload data untuk memfilter grid
                };
                filterContainer.appendChild(button);
            });
        } else {
            // Update status active saja tanpa hapus elemen
            Array.from(filterContainer.children).forEach(btn => {
                if (btn.innerText === activeCategory) btn.classList.add('active');
                else btn.classList.remove('active');
            });
        }
        const grid = document.getElementById('product-grid');
        grid.innerHTML = '';

        const filteredProducts = (activeCategory === 'All') 
            ? products 
            : products.filter(p => p.category === activeCategory);

        if (filteredProducts.length > 0) {
            filteredProducts.forEach(p => {
                let imgUrl = p.image_url ? p.image_url : 'https://placehold.co/400x300?text=No+Img';
                
                grid.innerHTML += `
                    <div class="product-card">
                        <img src="${imgUrl}" class="card-img-top" onerror="this.src='https://placehold.co/400x300?text=Err'">
                        <div class="card-body">
                            <div class="card-title" title="${p.name}">${p.name}</div>
                            <span class="card-category">${p.category}</span>
                            <div class="card-details">
                                <span class="stock-tag"><i class="fas fa-box"></i> ${p.stock}</span>
                                <span class="price-tag">Rp ${parseFloat(p.price).toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            grid.innerHTML = '<p style="grid-column:1/-1; text-align:center; padding:40px; color:#888;">Tidak ada produk di kategori ini.</p>';
        }
    } catch (e) {
        console.error(e);
    } finally {
        if(btn) { btn.disabled = false; btn.style.opacity = "1"; }
    }
}

// Switch Form
function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('auth-msg').innerText = '';
}

function showLogin() {
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('auth-msg').innerText = '';
}

// Handle Login Submit
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    const btn = e.target.querySelector('button');
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    const res = await eel.login_user(user, pass)();
    
    if (res.status === 'success') {
        enterDashboard();
    } else {
        document.getElementById('auth-msg').innerText = res.msg;
        btn.innerHTML = 'MASUK';
    }
});

// Handle Register Submit
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('reg-user').value;
    const pass = document.getElementById('reg-pass').value;
    
    if(!user || !pass) return;

    const res = await eel.register_user(user, pass)();
    
    if (res.status === 'success') {
        alert(res.msg);
        showLogin();
    } else {
        document.getElementById('auth-msg').innerText = res.msg;
    }
});

function enterDashboard() {
    // Sembunyikan Login, Tampilkan Dashboard
    document.getElementById('auth-view').style.display = 'none';
    document.getElementById('dashboard-view').style.display = 'flex'; // Flex agar layout sidebar pas
    
    // Mulai load data
    loadData();
    setInterval(loadData, 5000); // Mulai auto refresh
}

function logout() {
    // Reload halaman untuk reset semua state
    location.reload();
}

function updateChart(products) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    const labels = products.map(p => p.name);
    const data = products.map(p => p.stock);

    if (stockChart) {
        stockChart.data.labels = labels;
        stockChart.data.datasets[0].data = data;
        stockChart.update('none');
    } else {
        stockChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stok',
                    data: data,
                    backgroundColor: '#1976d2',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }
}

// --- CHAT & UPLOAD ---
let selectedFileBase64 = null;
let selectedFileName = null;

function handleFileSelect() {
    const file = document.getElementById('file-input').files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            selectedFileBase64 = e.target.result;
            selectedFileName = file.name;
            document.getElementById('upload-preview').style.display = 'block';
            document.getElementById('filename-display').innerText = file.name;
        };
        reader.readAsDataURL(file);
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    let text = input.value;
    if (!text && !selectedFileBase64) return;

    // UI User Bubble
    let msgUI = text;
    if (selectedFileName) msgUI = `[Upload: ${selectedFileName}]<br>` + text;
    addBubble(msgUI, 'user');
    
    input.value = '';
    const loadingId = addBubble("Memproses...", 'ai');

    // Logic Upload
    let prompt = text;
    if (selectedFileBase64) {
        const path = await eel.save_image_from_ui(selectedFileName, selectedFileBase64)();
        if (!path.startsWith("Error")) {
            prompt += ` (GAMBAR_PATH: ${path})`;
        }
        // Reset
        selectedFileBase64 = null;
        selectedFileName = null;
        document.getElementById('file-input').value = "";
        document.getElementById('upload-preview').style.display = "none";
    }

    // Kirim ke AI
    const reply = await eel.send_message_to_agent(prompt)();
    
    document.getElementById(loadingId).remove();
    addBubble(reply, 'ai');
    loadData(); // Auto refresh setelah chat
}

function addBubble(html, type) {
    const chat = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = `msg ${type}`;
    div.innerHTML = html;
    div.id = "msg-" + Date.now();
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div.id;
}

// --- MODAL ---
function toggleGuide() {
    const m = document.getElementById('guide-modal');
    m.style.display = (m.style.display === 'block') ? 'none' : 'block';
}
window.onclick = (e) => {
    const m = document.getElementById('guide-modal');
    if (e.target == m) m.style.display = 'none';
}
// Enter to send
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if(e.key === 'Enter') sendMessage();
});

function triggerAnalysis() {
    // Otomatis isi chat dan kirim
    document.getElementById('user-input').value = "Berikan analisis lengkap stok dan penjualan saya saat ini";
    sendMessage();
}