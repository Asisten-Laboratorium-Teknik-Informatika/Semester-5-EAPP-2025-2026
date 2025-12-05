// Fungsi untuk format waktu 24 jam ke 12 jam format
function formatTime12(time24) {
    if (!time24 || time24 === '-') return '-';
    const [hours, minutes, seconds] = time24.split(":");
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? "PM" : "AM";
    const hour12 = hour % 12 || 12;
    if (seconds) {
        return `${String(hour12).padStart(2, "0")}:${minutes}:${seconds} ${ampm}`;
    }
    return `${String(hour12).padStart(2, "0")}:${minutes} ${ampm}`;
}

// Set default dates untuk form
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const lastMonth = new Date(today);
    lastMonth.setMonth(lastMonth.getMonth() - 1);
    
    // Set default untuk export
    document.getElementById('exportStartDate').value = lastMonth.toISOString().split('T')[0];
    document.getElementById('exportEndDate').value = today.toISOString().split('T')[0];
    
    // Set default untuk report
    document.getElementById('reportStartDate').value = lastMonth.toISOString().split('T')[0];
    document.getElementById('reportEndDate').value = today.toISOString().split('T')[0];
    
    // Set default untuk late check (hari ini)
    document.getElementById('lateCheckDate').value = today.toISOString().split('T')[0];
    
    // Set default untuk search
    document.getElementById('searchStartDate').value = lastMonth.toISOString().split('T')[0];
    document.getElementById('searchEndDate').value = today.toISOString().split('T')[0];
});

// FITUR 1: Export to CSV
async function exportToCSV() {
    const startDate = document.getElementById('exportStartDate').value;
    const endDate = document.getElementById('exportEndDate').value;
    const employeeId = document.getElementById('exportEmployeeId').value.trim() || null;
    const resultDiv = document.getElementById('exportResult');
    
    resultDiv.innerHTML = '<div class="loading">Mengekspor data...</div>';
    
    try {
        const result = await eel.export_attendance_to_csv(startDate || null, endDate || null, employeeId)();
        
        if (result.error) {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✓ Berhasil!</strong><br>
                    ${result.message}<br>
                    <small>File: ${result.filename}</small><br>
                    <small>Total record: ${result.records_exported}</small>
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> ${error.message || 'Gagal mengekspor data'}
            </div>
        `;
    }
}

// FITUR 2: Generate Report
async function generateReport() {
    const startDate = document.getElementById('reportStartDate').value;
    const endDate = document.getElementById('reportEndDate').value;
    const employeeId = document.getElementById('reportEmployeeId').value.trim() || null;
    const resultDiv = document.getElementById('reportResult');
    
    if (!startDate || !endDate) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> Tanggal mulai dan tanggal akhir harus diisi
            </div>
        `;
        return;
    }
    
    resultDiv.innerHTML = '<div class="loading">Membuat laporan...</div>';
    
    try {
        const result = await eel.get_attendance_report(startDate, endDate, employeeId)();
        
        if (result.error) {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        } else if (!result.success) {
            resultDiv.innerHTML = `
                <div class="result-box">
                    <strong>Info:</strong> ${result.message}
                </div>
            `;
        } else {
            const stats = result.statistics;
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h3 style="margin-top: 0;">Laporan Periode: ${result.period.start_date} s/d ${result.period.end_date}</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">Total Records</div>
                            <div class="stat-value">${stats.total_records}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Hari Kerja</div>
                            <div class="stat-value">${stats.working_days}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Jam</div>
                            <div class="stat-value">${stats.total_hours} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Rata-rata Jam/Hari</div>
                            <div class="stat-value">${stats.average_hours_per_day} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Clock In</div>
                            <div class="stat-value">${stats.clock_ins}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Clock Out</div>
                            <div class="stat-value">${stats.clock_outs}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Terlambat</div>
                            <div class="stat-value">${stats.late_count}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Tepat Waktu</div>
                            <div class="stat-value">${stats.on_time_count}</div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> ${error.message || 'Gagal membuat laporan'}
            </div>
        `;
    }
}

// FITUR 3: Check Late Arrival
async function checkLate() {
    const date = document.getElementById('lateCheckDate').value;
    const employeeId = document.getElementById('lateCheckEmployeeId').value.trim() || null;
    const resultDiv = document.getElementById('lateResult');
    
    resultDiv.innerHTML = '<div class="loading">Mengecek keterlambatan...</div>';
    
    try {
        const result = await eel.check_late_arrival(employeeId, date || null)();
        
        if (result.error) {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        } else {
            const isLate = result.is_late;
            resultDiv.innerHTML = `
                <div class="result-box ${isLate ? 'error' : 'success'}">
                    <h3 style="margin-top: 0;">Hasil Pengecekan Keterlambatan</h3>
                    <p><strong>Status:</strong> 
                        <span class="badge ${isLate ? 'badge-danger' : 'badge-success'}">
                            ${isLate ? 'Terlambat' : 'Tepat Waktu'}
                        </span>
                    </p>
                    <p><strong>Waktu yang Diharapkan:</strong> ${formatTime12(result.expected_time)}</p>
                    <p><strong>Waktu Aktual:</strong> ${formatTime12(result.actual_time)}</p>
                    <p><strong>Selisih:</strong> ${result.difference_minutes} menit (${result.difference_hours} jam)</p>
                    <p><strong>Pesan:</strong> ${result.message}</p>
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> ${error.message || 'Gagal mengecek keterlambatan'}
            </div>
        `;
    }
}

// FITUR 4: Get Statistics
async function getStatistics() {
    const days = parseInt(document.getElementById('statsDays').value);
    const employeeId = document.getElementById('statsEmployeeId').value.trim() || null;
    const resultDiv = document.getElementById('statsResult');
    
    resultDiv.innerHTML = '<div class="loading">Menghitung statistik...</div>';
    
    try {
        const result = await eel.get_attendance_statistics(employeeId, days)();
        
        if (result.error) {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        } else if (!result.success) {
            resultDiv.innerHTML = `
                <div class="result-box">
                    <strong>Info:</strong> ${result.message}
                </div>
            `;
        } else {
            const stats = result.statistics;
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h3 style="margin-top: 0;">Statistik ${result.period_days} Hari Terakhir</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">Total Records</div>
                            <div class="stat-value">${stats.total_records}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Hari Kerja</div>
                            <div class="stat-value">${stats.working_days}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Jam</div>
                            <div class="stat-value">${stats.total_hours} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Rata-rata Jam/Hari</div>
                            <div class="stat-value">${stats.average_hours_per_day} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Rata-rata Jam/Hari Kerja</div>
                            <div class="stat-value">${stats.average_hours_per_working_day} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Rata-rata Jam/Minggu</div>
                            <div class="stat-value">${stats.average_weekly_hours} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Tingkat Kehadiran</div>
                            <div class="stat-value">${stats.attendance_rate}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Terlambat</div>
                            <div class="stat-value">${stats.late_count}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Tepat Waktu</div>
                            <div class="stat-value">${stats.on_time_count}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Jam Maksimum</div>
                            <div class="stat-value">${stats.max_hours} hrs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Jam Minimum</div>
                            <div class="stat-value">${stats.min_hours} hrs</div>
                        </div>
                    </div>
                    ${Object.keys(result.weekly_breakdown).length > 0 ? `
                        <h4 style="margin-top: 20px;">Breakdown Per Minggu:</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Minggu</th>
                                        <th>Total Jam</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(result.weekly_breakdown).map(([week, hours]) => `
                                        <tr>
                                            <td>${week}</td>
                                            <td>${hours.toFixed(2)} hrs</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : ''}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> ${error.message || 'Gagal menghitung statistik'}
            </div>
        `;
    }
}

// FITUR 5: Search Records
async function searchRecords() {
    const startDate = document.getElementById('searchStartDate').value || null;
    const endDate = document.getElementById('searchEndDate').value || null;
    const employeeId = document.getElementById('searchEmployeeId').value.trim() || null;
    const employeeName = document.getElementById('searchEmployeeName').value.trim() || null;
    const department = document.getElementById('searchDepartment').value.trim() || null;
    const minHours = document.getElementById('searchMinHours').value ? parseFloat(document.getElementById('searchMinHours').value) : null;
    const maxHours = document.getElementById('searchMaxHours').value ? parseFloat(document.getElementById('searchMaxHours').value) : null;
    const lateOnly = document.getElementById('searchLateOnly').checked;
    const resultDiv = document.getElementById('searchResult');
    
    resultDiv.innerHTML = '<div class="loading">Mencari data...</div>';
    
    try {
        const result = await eel.search_attendance_records(
            startDate, endDate, employeeId, employeeName, department, 
            minHours, maxHours, lateOnly
        )();
        
        if (result.error) {
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        } else {
            if (result.total_records === 0) {
                resultDiv.innerHTML = `
                    <div class="result-box">
                        <strong>Info:</strong> Tidak ada data yang ditemukan dengan filter yang diberikan
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="result-box success">
                        <h3 style="margin-top: 0;">Hasil Pencarian (${result.total_records} record ditemukan)</h3>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Tanggal</th>
                                        <th>Employee ID</th>
                                        <th>Nama</th>
                                        <th>Departemen</th>
                                        <th>Clock In</th>
                                        <th>Clock Out</th>
                                        <th>Total Jam</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${result.records.map(record => `
                                        <tr>
                                            <td>${record.date || '-'}</td>
                                            <td>${record.employee_id || '-'}</td>
                                            <td>${record.employee_name || '-'}</td>
                                            <td>${record.department || '-'}</td>
                                            <td>${formatTime12(record.clock_in)}</td>
                                            <td>${formatTime12(record.clock_out)}</td>
                                            <td>${record.total_hours ? record.total_hours.toFixed(2) + ' hrs' : '-'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> ${error.message || 'Gagal mencari data'}
            </div>
        `;
    }
}

