// Chart instances
let chartTransaksiHari = null;
let chartPendapatanHari = null;
let chartPerJenis = null;
let chartPerJam = null;
let chartHariMinggu = null;
let chartPendapatanHariMinggu = null;

// Chart configuration
const chartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 15,
                font: {
                    size: 12,
                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: {
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                size: 13
            },
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        if (label.includes('Pendapatan') || label.includes('Rp')) {
                            label += 'Rp ' + context.parsed.y.toLocaleString('id-ID');
                        } else {
                            label += context.parsed.y;
                        }
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            grid: {
                display: false
            },
            ticks: {
                font: {
                    size: 11
                },
                color: '#666'
            }
        },
        y: {
            grid: {
                color: '#f0f0f0'
            },
            ticks: {
                font: {
                    size: 11
                },
                color: '#666',
                callback: function(value) {
                    if (value >= 1000000) {
                        return 'Rp ' + (value / 1000000).toFixed(1) + 'M';
                    } else if (value >= 1000) {
                        return 'Rp ' + (value / 1000).toFixed(0) + 'K';
                    }
                    return 'Rp ' + value;
                }
            }
        }
    }
};

// Load all chart data
async function loadChartData() {
    const days = parseInt(document.getElementById('chartDaysRange').value) || 7;
    
    try {
        // Load data per hari
        const dataPerHari = await eel.get_chart_data_per_hari(days)();
        updateChartTransaksiHari(dataPerHari);
        updateChartPendapatanHari(dataPerHari);
        
        // Load data per jenis
        const dataPerJenis = await eel.get_chart_data_per_jenis()();
        updateChartPerJenis(dataPerJenis);
        
        // Load data per jam
        const dataPerJam = await eel.get_chart_data_per_jam()();
        updateChartPerJam(dataPerJam);
        
        // Load data per hari dalam minggu
        const dataHariMinggu = await eel.get_chart_data_per_hari_minggu()();
        updateChartHariMinggu(dataHariMinggu);
        updateChartPendapatanHariMinggu(dataHariMinggu);
        
        lucide.createIcons();
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Update Chart Transaksi Per Hari
function updateChartTransaksiHari(data) {
    const ctx = document.getElementById('chartTransaksiHari');
    if (!ctx) return;
    
    const labels = data.map(item => {
        const date = new Date(item.tanggal);
        return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
    });
    const transaksi = data.map(item => item.transaksi);
    
    if (chartTransaksiHari) {
        chartTransaksiHari.destroy();
    }
    
    chartTransaksiHari = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Transaksi',
                data: transaksi,
                backgroundColor: 'rgba(26, 26, 26, 0.8)',
                borderColor: 'rgba(26, 26, 26, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartConfig,
            scales: {
                ...chartConfig.scales,
                y: {
                    ...chartConfig.scales.y,
                    ticks: {
                        ...chartConfig.scales.y.ticks,
                        callback: function(value) {
                            return value;
                        }
                    }
                }
            }
        }
    });
}

// Update Chart Pendapatan Per Hari
function updateChartPendapatanHari(data) {
    const ctx = document.getElementById('chartPendapatanHari');
    if (!ctx) return;
    
    const labels = data.map(item => {
        const date = new Date(item.tanggal);
        return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
    });
    const pendapatan = data.map(item => item.pendapatan);
    
    if (chartPendapatanHari) {
        chartPendapatanHari.destroy();
    }
    
    chartPendapatanHari = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pendapatan (Rp)',
                data: pendapatan,
                borderColor: 'rgba(26, 26, 26, 1)',
                backgroundColor: 'rgba(26, 26, 26, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: chartConfig
    });
}

// Update Chart Per Jenis
function updateChartPerJenis(data) {
    const ctx = document.getElementById('chartPerJenis');
    if (!ctx) return;
    
    const labels = data.map(item => item.jenis);
    const jumlah = data.map(item => item.jumlah);
    
    // Generate colors
    const colors = [
        'rgba(26, 26, 26, 0.8)',
        'rgba(74, 74, 74, 0.8)',
        'rgba(42, 42, 42, 0.8)',
        'rgba(100, 100, 100, 0.8)',
        'rgba(120, 120, 120, 0.8)',
        'rgba(140, 140, 140, 0.8)'
    ];
    
    if (chartPerJenis) {
        chartPerJenis.destroy();
    }
    
    chartPerJenis = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: jumlah,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig,
            plugins: {
                ...chartConfig.plugins,
                tooltip: {
                    ...chartConfig.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Update Chart Per Jam
function updateChartPerJam(data) {
    const ctx = document.getElementById('chartPerJam');
    if (!ctx) return;
    
    // Create array for all 24 hours
    const hours = Array.from({ length: 24 }, (_, i) => i);
    const transaksiByHour = new Array(24).fill(0);
    
    data.forEach(item => {
        transaksiByHour[item.jam] = item.transaksi;
    });
    
    const labels = hours.map(h => h + ':00');
    
    if (chartPerJam) {
        chartPerJam.destroy();
    }
    
    chartPerJam = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Transaksi',
                data: transaksiByHour,
                backgroundColor: 'rgba(26, 26, 26, 0.6)',
                borderColor: 'rgba(26, 26, 26, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartConfig,
            scales: {
                ...chartConfig.scales,
                x: {
                    ...chartConfig.scales.x,
                    ticks: {
                        ...chartConfig.scales.x.ticks,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    ...chartConfig.scales.y,
                    ticks: {
                        ...chartConfig.scales.y.ticks,
                        callback: function(value) {
                            return value;
                        }
                    }
                }
            }
        }
    });
}

// Update Chart Hari dalam Minggu (Transaksi)
function updateChartHariMinggu(data) {
    const ctx = document.getElementById('chartHariMinggu');
    if (!ctx) return;
    
    const labels = data.map(item => item.hari);
    const transaksi = data.map(item => item.transaksi);
    
    if (chartHariMinggu) {
        chartHariMinggu.destroy();
    }
    
    chartHariMinggu = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Transaksi',
                data: transaksi,
                backgroundColor: 'rgba(26, 26, 26, 0.8)',
                borderColor: 'rgba(26, 26, 26, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartConfig,
            scales: {
                ...chartConfig.scales,
                y: {
                    ...chartConfig.scales.y,
                    ticks: {
                        ...chartConfig.scales.y.ticks,
                        callback: function(value) {
                            return value;
                        }
                    }
                }
            }
        }
    });
}

// Update Chart Pendapatan Hari dalam Minggu
function updateChartPendapatanHariMinggu(data) {
    const ctx = document.getElementById('chartPendapatanHariMinggu');
    if (!ctx) return;
    
    const labels = data.map(item => item.hari);
    const pendapatan = data.map(item => item.pendapatan);
    
    if (chartPendapatanHariMinggu) {
        chartPendapatanHariMinggu.destroy();
    }
    
    chartPendapatanHariMinggu = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pendapatan (Rp)',
                data: pendapatan,
                backgroundColor: 'rgba(26, 26, 26, 0.8)',
                borderColor: 'rgba(26, 26, 26, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: chartConfig
    });
}

