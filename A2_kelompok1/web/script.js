// Fungsi notifikasi
function showNotification(message, type = 'success') {
    const notif = document.getElementById('notification');
    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.style.display = 'block';
    
    setTimeout(() => {
        notif.style.display = 'none';
    }, 3000);
}

// Fungsi kendaraan masuk
async function kendaraanMasuk() {
    const plat = document.getElementById('plat').value.trim();
    const jenis = document.getElementById('jenis').value;

    if (!plat) {
        showNotification('Nomor plat harus diisi!', 'error');
        return;
    }

    try {
        console.log('🚗 Mencoba menyimpan kendaraan:', plat, jenis);
        const result = await eel.kendaraan_masuk(plat, jenis)();
        console.log('✅ Result masuk:', result);
        
        if (result.success) {
            showNotification(result.message);
            document.getElementById('formMasuk').reset();
            // Verifikasi data tersimpan dengan memuat ulang
            await loadData();
            console.log('✅ Data berhasil dimuat ulang');
        } else {
            console.error('❌ Gagal menyimpan:', result.message);
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('❌ Error kendaraan masuk:', error);
        showNotification('Terjadi kesalahan!', 'error');
    }
}

// Fungsi kendaraan keluar
async function kendaraanKeluar(id) {
    if (!confirm('Yakin kendaraan ini akan keluar?')) return;

    try {
        const result = await eel.kendaraan_keluar(id)();
        
        if (result.success) {
            showNotification(
                `${result.message}\nDurasi: ${result.jam} jam (${result.durasi} menit)\nBiaya: Rp ${result.biaya.toLocaleString('id-ID')}`
            );
            await loadData();
            // Reapply filters after data reload
            applyParkirFilters();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error kendaraan keluar:', error);
        showNotification('Terjadi kesalahan!', 'error');
    }
}

// Load semua data
async function loadData() {
    await loadKendaraanParkir();
    await loadRiwayat();
    await updateStats();
}

// Store original parkir data for search filtering
let originalParkirData = [];

// Load kendaraan yang sedang parkir
async function loadKendaraanParkir() {
    try {
        console.log('Memuat data kendaraan parkir dari database...');
        const dataParkir = await eel.get_kendaraan_parkir_data()();
        console.log('Data parkir dari database:', dataParkir);
        console.log('Jumlah kendaraan parkir:', dataParkir.length);
        
        // Store original data
        originalParkirData = dataParkir;
        
        // Apply filters if any
        applyParkirFilters();
    } catch (error) {
        console.error('Error loading parkir:', error);
    }
}

// Display parkir data
function displayParkir(dataParkir) {
    const tableParkir = document.getElementById('tableParkir');
    
    if (dataParkir.length === 0) {
        console.log('Tidak ada kendaraan parkir');
        tableParkir.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <div class="empty-icon"><i data-lucide="car"></i></div>
                    <p>Tidak ada kendaraan parkir</p>
                </td>
            </tr>`;
    } else {
        console.log('Menampilkan', dataParkir.length, 'kendaraan parkir');
        tableParkir.innerHTML = dataParkir.map((item, index) => `
            <tr class="table-row-hover">
                <td>${index + 1}</td>
                <td><strong class="plat-number">${item.plat}</strong></td>
                <td><span class="badge badge-${item.jenis.toLowerCase()}">${getVehicleIcon(item.jenis)} ${item.jenis}</span></td>
                <td>${formatDateTime(item.time_in)}</td>
                <td class="text-center">
                    <button class="btn btn-danger btn-sm" onclick="kendaraanKeluar(${item.id})">
                        <i data-lucide="arrow-left" class="btn-icon"></i> Keluar
                    </button>
                </td>
            </tr>
        `).join('');
    }
    lucide.createIcons();
}

// Search parkir by plat
function searchParkirByPlat() {
    const searchValue = document.getElementById('searchPlatParkir').value.trim().toUpperCase();
    const clearBtn = document.getElementById('clearSearchParkir');
    
    if (searchValue === '') {
        clearBtn.style.display = 'none';
    } else {
        clearBtn.style.display = 'flex';
    }
    
    // Apply all filters
    applyParkirFilters();
}

// Clear search parkir
function clearSearchParkir() {
    document.getElementById('searchPlatParkir').value = '';
    document.getElementById('clearSearchParkir').style.display = 'none';
    applyParkirFilters();
}

// Filter parkir by jenis
function filterParkirByJenis() {
    applyParkirFilters();
}

// Apply all filters (search + jenis)
function applyParkirFilters() {
    const searchValue = document.getElementById('searchPlatParkir')?.value.trim().toUpperCase() || '';
    const filterJenis = document.getElementById('filterJenisParkir')?.value || 'all';
    
    let filteredData = originalParkirData.length > 0 ? [...originalParkirData] : [];
    
    // Apply search filter
    if (searchValue) {
        filteredData = filteredData.filter(item => 
            item.plat && item.plat.toUpperCase().includes(searchValue)
        );
    }
    
    // Apply jenis filter
    if (filterJenis !== 'all') {
        filteredData = filteredData.filter(item => 
            item.jenis === filterJenis
        );
    }
    
    displayParkir(filteredData);
}

// Store original riwayat data for search filtering
let originalRiwayatData = [];

// Load riwayat parkir
async function loadRiwayat() {
    try {
        // Otomatis terapkan filter yang dipilih
        const filterRange = document.getElementById('filterRange');
        if (filterRange && filterRange.value) {
            await filterRiwayatWaktu();
        } else {
            console.log('Memuat riwayat parkir dari database...');
            const dataRiwayat = await eel.get_riwayat()();
            console.log('Data riwayat dari database:', dataRiwayat);
            console.log('Jumlah riwayat:', dataRiwayat.length);
            originalRiwayatData = dataRiwayat;
            displayRiwayat(dataRiwayat);
        }
        // Initialize icons after loading
        lucide.createIcons();
    } catch (error) {
        console.error('Error loading riwayat:', error);
    }
}

// Search riwayat by plat
async function searchRiwayatByPlat() {
    const searchValue = document.getElementById('searchPlat').value.trim().toUpperCase();
    const clearBtn = document.getElementById('clearSearch');
    
    if (searchValue === '') {
        clearBtn.style.display = 'none';
        // If no search value, apply time filter if exists
        const filterRange = document.getElementById('filterRange');
        if (filterRange && filterRange.value && filterRange.value !== 'all') {
            await filterRiwayatWaktu();
        } else if (originalRiwayatData.length > 0) {
            displayRiwayat(originalRiwayatData);
        } else {
            // Reload all data
            const dataRiwayat = await eel.get_riwayat()();
            originalRiwayatData = dataRiwayat;
            displayRiwayat(dataRiwayat);
        }
        lucide.createIcons();
        return;
    }
    
    clearBtn.style.display = 'flex';
    
    // Get data to search from - use filtered data if available, otherwise load all
    let dataToSearch = originalRiwayatData.length > 0 ? originalRiwayatData : [];
    
    if (dataToSearch.length === 0) {
        // Load all data if we don't have any
        try {
            dataToSearch = await eel.get_riwayat()();
            originalRiwayatData = dataToSearch;
        } catch (error) {
            console.error('Error loading data for search:', error);
            return;
        }
    }
    
    // Apply search filter
    const filteredData = dataToSearch.filter(item => 
        item.plat && item.plat.toUpperCase().includes(searchValue)
    );
    
    displayRiwayat(filteredData);
    lucide.createIcons();
}

// Clear search
function clearSearch() {
    document.getElementById('searchPlat').value = '';
    document.getElementById('clearSearch').style.display = 'none';
    searchRiwayatByPlat();
}

// FUNGSI BARU: Filter riwayat berdasarkan range waktu
async function filterRiwayatWaktu() {
    const rangeType = document.getElementById('filterRange').value;
    const searchValue = document.getElementById('searchPlat').value.trim().toUpperCase();

    if (!rangeType) {
        showNotification('Pilih filter waktu terlebih dahulu!', 'error');
        return;
    }

    try {
        let dataRiwayat;
        
        if (rangeType === 'all') {
            // Load semua data tanpa filter
            console.log('Memuat semua riwayat...');
            dataRiwayat = await eel.get_riwayat()();
        } else {
            console.log('Memfilter riwayat dengan range:', rangeType);
            dataRiwayat = await eel.get_riwayat_by_time_range(rangeType)();
        }
        
        // Store original data
        originalRiwayatData = dataRiwayat;
        
        // Apply search filter if exists
        if (searchValue) {
            dataRiwayat = dataRiwayat.filter(item => 
                item.plat && item.plat.toUpperCase().includes(searchValue)
            );
        }
        
        console.log('Data riwayat setelah filter:', dataRiwayat);
        console.log('Jumlah riwayat:', dataRiwayat.length);
        displayRiwayat(dataRiwayat);
        lucide.createIcons();
        
        const rangeLabels = {
            'all': 'Semua',
            'today': 'Hari Ini',
            'yesterday': 'Kemarin',
            'week': 'Minggu Ini',
            'month': 'Bulan Ini',
            'year': 'Tahun Ini'
        };
        
        showNotification(`Menampilkan data: ${rangeLabels[rangeType]} (${dataRiwayat.length} transaksi)`);
    } catch (error) {
        console.error('Error filter riwayat:', error);
        showNotification('Terjadi kesalahan saat memfilter data!', 'error');
    }
}

// Reset filter
async function resetFilter() {
    document.getElementById('filterRange').value = 'all';
    await filterRiwayatWaktu();
    showNotification('Filter direset ke "Semua"');
}

// Display riwayat
function displayRiwayat(dataRiwayat) {
    const tableRiwayat = document.getElementById('tableRiwayat');
    
    if (dataRiwayat.length === 0) {
        tableRiwayat.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <div class="empty-icon"><i data-lucide="file-text"></i></div>
                    <p>Belum ada riwayat</p>
                </td>
            </tr>`;
    } else {
        tableRiwayat.innerHTML = dataRiwayat.map(item => `
            <tr class="table-row-hover">
                <td><strong class="plat-number">${item.plat}</strong></td>
                <td><span class="badge badge-${item.jenis.toLowerCase()}">${getVehicleIcon(item.jenis)} ${item.jenis}</span></td>
                <td>${formatDateTime(item.time_in)}</td>
                <td>${formatDateTime(item.time_out)}</td>
                <td class="text-center"><span class="duration-badge">${Math.ceil(item.durasi_menit / 60)} jam</span></td>
                <td class="text-right"><strong class="price-text">Rp ${item.biaya.toLocaleString('id-ID')}</strong></td>
            </tr>
        `).join('');
    }
    lucide.createIcons();
}

// Update statistik
async function updateStats() {
    try {
        const stats = await eel.get_stats()();
        
        document.getElementById('statParkir').textContent = stats.total_parkir;
        document.getElementById('statHariIni').textContent = stats.transaksi_hari_ini;
        document.getElementById('statPendapatan').textContent = 
            'Rp ' + stats.pendapatan_hari_ini.toLocaleString('id-ID');
    } catch (error) {
        console.error('Error update stats:', error);
    }
}

// Format tanggal dan waktu
function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format tanggal saja
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
}

// Get vehicle icon
function getVehicleIcon(jenis) {
    const icons = {
        'Motor': '<i data-lucide="bike"></i>',
        'Mobil': '<i data-lucide="car"></i>',
        'Truk': '<i data-lucide="truck"></i>',
        'Bus': '<i data-lucide="truck"></i>',
        'Pickup': '<i data-lucide="truck"></i>',
        'Sepeda': '<i data-lucide="bike"></i>'
    };
    return icons[jenis] || '<i data-lucide="car"></i>';
}

// Set default filter
function setDefaultFilter() {
    const filterRange = document.getElementById('filterRange');
    if (filterRange) {
        filterRange.value = 'all';
        // Tambahkan event listener untuk auto-filter saat dropdown berubah
        filterRange.addEventListener('change', function() {
            filterRiwayatWaktu();
        });
    }
}

// Load data saat halaman dimuat
window.onload = () => {
    setDefaultFilter();
    loadData();
    // Initialize icons
    lucide.createIcons();
    // Auto refresh setiap 30 detik
    setInterval(updateStats, 30000);
};