// Menu link active state and navigation
const menuLinks = document.querySelectorAll(".menu-link")
menuLinks.forEach((link) => {
  // Set active class based on current page
  const href = link.getAttribute("href")
  const currentPage = window.location.pathname.split("/").pop() || "index.html"
  if (href === currentPage) {
    link.classList.add("active")
  }

  // Handle click events
  link.addEventListener("click", function (e) {
    if (href === "#" || href === "#settings") {
      e.preventDefault()
      menuLinks.forEach((l) => l.classList.remove("active"))
      this.classList.add("active")
    }
  })
})

// Day card selection (legacy - akan diganti dengan updateWeekOverview)
// Event listener untuk day card akan ditambahkan di updateWeekOverview

// Variabel global untuk menyimpan clock in time
let currentClockInTime = null
let isClockedIn = false

function resetDashboardStatsIfNeeded() {
  const shouldReset = sessionStorage.getItem('reset_work_stats_dashboard') === 'true'
  if (!shouldReset) return
  sessionStorage.removeItem('reset_work_stats_dashboard')

  isClockedIn = false
  currentClockInTime = null

  const statusBadge = document.getElementById("statusBadge")
  if (statusBadge) {
    statusBadge.textContent = "Belum Active"
    statusBadge.style.backgroundColor = "#ef4444"
    statusBadge.style.color = "white"
  }

  const clockInTimeEl = document.getElementById("clockInTime")
  if (clockInTimeEl) {
    clockInTimeEl.textContent = "--:-- --"
  }

  const timeElapsedEl = document.getElementById("timeElapsed")
  if (timeElapsedEl) {
    timeElapsedEl.textContent = "00:00:00"
  }

  const progressFillEl = document.getElementById("progressFill")
  if (progressFillEl) {
    progressFillEl.style.width = "0%"
  }

  const progressPercentEl = document.getElementById("progressPercent")
  if (progressPercentEl) {
    progressPercentEl.textContent = "0%"
  }

  const hoursTodayEl = document.getElementById("hoursToday")
  if (hoursTodayEl) {
    hoursTodayEl.innerHTML = `0.0 <span class="stat-unit">hrs</span>`
  }

  const activityList = document.getElementById("recentActivityList")
  if (activityList) {
    activityList.innerHTML = `
      <li style="text-align:center;padding:20px;color:var(--text-secondary);">
        Belum ada aktivitas
      </li>`
  }
}

// Fungsi untuk convert waktu 24 jam ke 12 jam format
function formatTime(time24) {
  if (!time24) return "--:-- --"
  
  const [hours, minutes, seconds] = time24.split(":")
  const hour = parseInt(hours)
  const ampm = hour >= 12 ? "PM" : "AM"
  const hour12 = hour % 12 || 12
  
  if (seconds) {
    return `${String(hour12).padStart(2, "0")}:${minutes}:${seconds} ${ampm}`
  }
  return `${String(hour12).padStart(2, "0")}:${minutes} ${ampm}`
}

// Fungsi untuk update status dashboard dari backend
async function updateDashboardStatus() {
  try {
    if (typeof eel === 'undefined') {
      console.warn('Eel belum tersedia, menunggu...');
      return;
    }
    
    const userStr = sessionStorage.getItem('currentUser');
    let employeeId = 'USER001';
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        employeeId = user.employee_id || 'USER001';
      } catch (err) {
        console.warn('[DASHBOARD] Gagal parse user data, fallback USER001', err);
        employeeId = 'USER001';
      }
    }
    
    let status = null;
    try {
      status = await eel.get_current_status(employeeId)();
    } catch (err) {
      console.error('[DASHBOARD] Error memanggil get_current_status:', err);
      return;
    }
    
    if (!status) {
      console.warn('[DASHBOARD] Status kosong dari backend');
      return;
    }
    
    isClockedIn = (status.is_clocked_in === true) || (status.is_clocked_in === 1);
    currentClockInTime = status.clock_in || null;
    
    const statusBadge = document.getElementById("statusBadge");
    if (statusBadge) {
      if (isClockedIn) {
        statusBadge.textContent = "Active";
        statusBadge.style.backgroundColor = "#10b981";
        statusBadge.style.color = "white";
      } else {
        statusBadge.textContent = "Belum Active";
        statusBadge.style.backgroundColor = "#ef4444";
        statusBadge.style.color = "white";
      }
    }
    
    const clockInTimeEl = document.getElementById("clockInTime");
    if (clockInTimeEl) {
      if (status.clock_in) {
        clockInTimeEl.textContent = formatTime(status.clock_in);
      } else {
        clockInTimeEl.textContent = "Belum masuk";
      }
    }
    
    const hoursTodayEl = document.getElementById("hoursToday");
    if (hoursTodayEl) {
      const totalToday = typeof status.today_total_hours === 'number'
        ? status.today_total_hours
        : (typeof status.total_hours === 'number' ? status.total_hours : 0);
      hoursTodayEl.innerHTML = `${totalToday.toFixed(1)} <span class="stat-unit">hrs</span>`;
    }
  } catch (error) {
    console.error("Error updating dashboard status:", error);
  }
}

// Real-time clock update untuk time elapsed
function updateElapsedTime() {
  const timeElapsedEl = document.getElementById("timeElapsed")
  const progressFillEl = document.getElementById("progressFill")
  const progressPercentEl = document.getElementById("progressPercent")
  
  if (!isClockedIn || !currentClockInTime) {
    // Belum clock in, reset time elapsed
    if (timeElapsedEl) timeElapsedEl.textContent = "00:00:00"
    if (progressFillEl) progressFillEl.style.width = "0%"
    if (progressPercentEl) progressPercentEl.textContent = "0%"
    return
  }
  
  // Parse clock in time dan buat datetime lengkap untuk hari ini
  const [hours, minutes, seconds] = currentClockInTime.split(":")
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const clockInDate = new Date(today)
  clockInDate.setHours(parseInt(hours), parseInt(minutes), parseInt(seconds || 0), 0)
  
  // Jika clock in time lebih dari waktu sekarang, berarti clock in kemarin
  // (tidak mungkin, tapi untuk safety check)
  if (clockInDate > now) {
    // Kurangi 1 hari
    clockInDate.setDate(clockInDate.getDate() - 1)
  }
  
  const elapsedMs = now - clockInDate
  
  // Pastikan elapsed time tidak negatif
  if (elapsedMs < 0) {
    if (timeElapsedEl) timeElapsedEl.textContent = "00:00:00"
    if (progressFillEl) progressFillEl.style.width = "0%"
    if (progressPercentEl) progressPercentEl.textContent = "0%"
    return
  }
  
  const elapsedHours = elapsedMs / (1000 * 60 * 60)
  
  const hours_elapsed = Math.floor(elapsedMs / (1000 * 60 * 60))
  const minutes_elapsed = Math.floor((elapsedMs % (1000 * 60 * 60)) / (1000 * 60))
  const seconds_elapsed = Math.floor((elapsedMs % (1000 * 60)) / 1000)
  
  const timeDisplay = `${String(hours_elapsed).padStart(2, "0")}:${String(minutes_elapsed).padStart(2, "0")}:${String(seconds_elapsed).padStart(2, "0")}`
  
  if (timeElapsedEl) {
    timeElapsedEl.textContent = timeDisplay
  }
  
  // Update Daily Progress (target 8 jam = 100%)
  const targetHours = 8
  const progressPercent = Math.min((elapsedHours / targetHours) * 100, 100)
  
  if (progressFillEl) {
    progressFillEl.style.width = `${progressPercent}%`
  }
  
  if (progressPercentEl) {
    progressPercentEl.textContent = `${Math.round(progressPercent)}%`
  }
}

// Fungsi untuk mendapatkan tanggal minggu ini (Senin - Minggu)
function getWeekDates() {
  const now = new Date()
  const day = now.getDay()
  
  // Hitung Senin (1) dari minggu ini
  // day = 0 (Minggu), 1 (Senin), ..., 6 (Sabtu)
  // Jika hari ini Minggu (0), mundur ke Senin minggu lalu
  // Jika hari ini bukan Minggu, mundur ke Senin minggu ini
  const diff = day === 0 ? -6 : 1 - day
  const monday = new Date(now)
  monday.setDate(now.getDate() + diff)
  
  // Generate array tanggal untuk semua hari dalam minggu (Senin - Minggu)
  const weekDates = []
  const dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    
    weekDates.push({
      date: date,
      dayName: dayNames[i],
      dateString: date.toISOString().split('T')[0], // Format: YYYY-MM-DD
      dayNumber: date.getDate(),
      monthName: date.toLocaleDateString('id-ID', { month: 'short' }),
      isToday: date.toDateString() === now.toDateString(),
      isWeekend: i >= 5 // Sabtu dan Minggu
    })
  }
  
  return weekDates
}

function getWeekDateRange() {
  const weekDates = getWeekDates()
  const monday = weekDates[0].date
  const sunday = weekDates[6].date
  
  // Format tanggal pendek untuk header
  const formatShortDate = (date) => {
    const day = date.getDate()
    const month = date.toLocaleDateString('id-ID', { month: 'short' })
    return `${day} ${month}`
  }
  
  // Jika dalam bulan yang sama, tampilkan format pendek
  if (monday.getMonth() === sunday.getMonth() && monday.getFullYear() === sunday.getFullYear()) {
    return `${formatShortDate(monday)} - ${formatShortDate(sunday)} ${monday.getFullYear()}`
  } else {
    // Jika beda bulan, tampilkan format lengkap
    const formatFullDate = (date) => {
      const day = date.getDate()
      const month = date.toLocaleDateString('id-ID', { month: 'long' })
      const year = date.getFullYear()
      return `${day} ${month} ${year}`
    }
    return `${formatFullDate(monday)} - ${formatFullDate(sunday)}`
  }
}

// Fungsi untuk load data jam kerja per hari dalam minggu
async function loadWeekHours(weekDates) {
  try {
    // Ambil employee_id dari sessionStorage
    const userStr = sessionStorage.getItem('currentUser');
    let employeeId = null;
    if (userStr) {
      const user = JSON.parse(userStr);
      employeeId = user.employee_id;
    }
    
    // Ambil data attendance untuk minggu ini dari backend
    // Menggunakan load_data() langsung dari utils karena lebih efisien
    const weekHours = {}
    
    // Initialize semua hari dengan 0 jam
    weekDates.forEach(dayData => {
      weekHours[dayData.dateString] = 0
    })
    
    // Ambil semua data attendance dari backend
    try {
      // Check if eel is available
    if (typeof eel === 'undefined') {
      console.warn('Eel belum tersedia saat loadWeekHours');
      return weekHours;
    }
    
    // Load semua data attendance untuk minggu ini menggunakan get_attendance_report
      const startDate = weekDates[0].dateString
      const endDate = weekDates[6].dateString
      
      const reportData = await eel.get_attendance_report(startDate, endDate, employeeId)()
      
      let allAttendanceData = []
      
      if (reportData && reportData.success && reportData.data) {
        // Ambil data dari report
        allAttendanceData = reportData.data
      } else if (reportData && reportData.error) {
        console.log("Error from report:", reportData.error)
        // Jika error, ambil data kosong
        allAttendanceData = []
      } else {
        // Jika tidak ada data, tetap gunakan array kosong
        allAttendanceData = []
      }
      
      // Hitung total jam kerja untuk setiap hari
      weekDates.forEach(dayData => {
        const dateStr = dayData.dateString
        const dayAttendance = allAttendanceData.filter(record => record.date === dateStr)
        
        let totalHours = 0
        if (dayAttendance && dayAttendance.length > 0) {
          totalHours = dayAttendance.reduce((sum, record) => {
            const hours = parseFloat(record.total_hours) || 0
            return sum + hours
          }, 0)
        }
        
        weekHours[dateStr] = Math.round(totalHours * 10) / 10 // Round to 1 decimal
      })
      
    } catch (error) {
      console.error("Error loading week hours from backend:", error)
      // Tetap return weekHours dengan nilai 0 untuk semua hari
    }
    
    return weekHours
  } catch (error) {
    console.error("Error loading week hours:", error)
    // Return empty hours untuk semua hari jika error
    const weekHours = {}
    weekDates.forEach(dayData => {
      weekHours[dayData.dateString] = 0
    })
    return weekHours
  }
}

// Update week overview cards dengan tanggal asli
async function updateWeekOverview() {
  const gridEl = document.getElementById('weekOverviewGrid')
  if (!gridEl) return
  
  // Dapatkan tanggal minggu ini
  const weekDates = getWeekDates()
  
  // Update judul dengan range tanggal
  const titleEl = document.getElementById('weekOverviewTitle')
  if (titleEl) {
    const weekRange = getWeekDateRange()
    titleEl.textContent = `Ringkasan Minggu Ini (${weekRange})`
  }
  
  // Load data jam kerja untuk minggu ini
  const weekHours = await loadWeekHours(weekDates)
  
  // Clear grid
  gridEl.innerHTML = ''
  
  // Generate card untuk setiap hari
  weekDates.forEach(dayData => {
    const card = document.createElement('div')
    card.className = 'day-card'
    
    // Mark hari ini sebagai active
    if (dayData.isToday) {
      card.classList.add('active')
    }
    
    // Mark weekend sebagai inactive
    if (dayData.isWeekend) {
      card.classList.add('inactive')
    }
    
    // Ambil jam kerja untuk hari ini
    const hours = weekHours[dayData.dateString] || 0
    const hoursDisplay = hours > 0 ? `${hours.toFixed(1)}h` : '--'
    
    // Format tanggal untuk ditampilkan
    const dateDisplay = `${dayData.dayNumber} ${dayData.monthName}`
    
    // Add data attribute untuk tanggal
    card.setAttribute('data-date', dayData.dateString)
    
    card.innerHTML = `
      <div class="day-name">${dayData.dayName}</div>
      <div class="day-date">${dateDisplay}</div>
      <div class="day-hours">${hoursDisplay}</div>
      <div class="day-indicator"></div>
    `
    
    // Add click event listener untuk select
    card.addEventListener('click', function() {
      // Jangan select jika weekend (inactive)
      if (!dayData.isWeekend) {
        // Remove selected dari semua card
        document.querySelectorAll('.day-card').forEach(c => {
          c.classList.remove('selected')
        })
        // Add selected ke card yang diklik
        this.classList.add('selected')
        
        // Optional: Log atau action lain saat card di-select
        console.log(`Selected date: ${dayData.dateString} (${dateDisplay})`)
      }
    })
    
    gridEl.appendChild(card)
  })
}

// Muat recent activity realtime
async function loadRecentActivity(limit = 10) {
  try {
    const listEl = document.getElementById('recentActivityList')
    if (!listEl) {
      console.warn('[DASHBOARD] recentActivityList element tidak ditemukan')
      return
    }

    if (typeof eel === 'undefined') {
      listEl.innerHTML = `
        <li style="text-align:center;padding:20px;color:var(--text-secondary);">
          Backend belum siap
        </li>`
      return
    }

    const userStr = sessionStorage.getItem('currentUser')
    let employeeId = 'USER001'
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        employeeId = user.employee_id || 'USER001'
      } catch (err) {
        console.warn('[DASHBOARD] Gagal parse user data untuk recent activity', err)
      }
    }

    const activities = await eel.get_recent_activity(employeeId, limit)()
    listEl.innerHTML = ''

    if (!activities || activities.length === 0) {
      listEl.innerHTML = `
        <li style="text-align:center;padding:20px;color:var(--text-secondary);">
          Belum ada aktivitas
        </li>`
      return
    }

    activities.forEach(activity => {
      const li = document.createElement('li')
      li.className = 'activity-item'

      const dot = document.createElement('span')
      const isClockIn = activity.type === 'clock_in'
      const isLate = Boolean(activity.is_late)
      dot.className = `activity-dot ${isClockIn ? (isLate ? 'dot-orange' : 'dot-blue') : 'dot-green'}`

      const content = document.createElement('div')
      content.className = 'activity-content'

      const title = document.createElement('div')
      title.className = 'activity-title'
      title.textContent = activity.title || (isClockIn ? 'Clock In' : 'Clock Out')

      const meta = document.createElement('div')
      meta.className = 'activity-time'
      const timeText = activity.time ? formatTime(activity.time) : '--:--'
      const dateText = activity.date_display || activity.date || ''
      const extra =
        !isClockIn && typeof activity.total_hours === 'number'
          ? ` • ${parseFloat(activity.total_hours).toFixed(1)} jam`
          : isClockIn && isLate
            ? ' • Terlambat'
            : ''
      meta.textContent = `${dateText} • ${timeText}${extra}`

      content.appendChild(title)
      content.appendChild(meta)

      li.appendChild(dot)
      li.appendChild(content)

      listEl.appendChild(li)
    })
  } catch (error) {
    console.error('[DASHBOARD] Error loading recent activity:', error)
    const listEl = document.getElementById('recentActivityList')
    if (listEl) {
      listEl.innerHTML = `
        <li style="text-align:center;padding:20px;color:#ef4444;">
          Gagal memuat aktivitas
        </li>`
    }
  }
}


// Event listener untuk refresh saat ada update attendance
window.addEventListener('storage', function(e) {
  if (e.key === 'attendance_updated') {
    console.log('[DASHBOARD] Storage event: Attendance updated, refreshing...');
    setTimeout(() => {
      updateDashboardStatus();
      updateWeekOverview();
      loadAttendanceEmployees();
      loadRecentActivity();
    }, 500);
  }
});

// Event listener untuk postMessage (cross-tab communication)
window.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'attendance_updated') {
    console.log('[DASHBOARD] PostMessage event: Attendance updated, refreshing...');
    setTimeout(() => {
      updateDashboardStatus();
      updateWeekOverview();
      loadAttendanceEmployees();
      loadRecentActivity();
    }, 500);
  }
});

// Refresh saat window focus (jika user kembali ke tab)
window.addEventListener('focus', function() {
  console.log('[DASHBOARD] Window focused, refreshing...');
  updateDashboardStatus();
  updateWeekOverview();
  loadAttendanceEmployees();
  loadRecentActivity();
});

// Tambahkan juga polling untuk memastikan dashboard selalu ter-update
// (backup jika event listener tidak bekerja)

// Load dashboard data
resetDashboardStatsIfNeeded()

setTimeout(() => {
  updateDashboardStatus();
  updateWeekOverview();
  loadAttendanceEmployees();
  loadRecentActivity();
  
  // Update setiap 5 detik
  setInterval(() => {
    updateDashboardStatus();
    updateWeekOverview();
    loadAttendanceEmployees();
    loadRecentActivity();
  }, 5000);
}, 500);

// Update time elapsed setiap detik
setInterval(updateElapsedTime, 1000)
updateElapsedTime()

// Fungsi untuk load dan display data karyawan yang hadir
async function loadAttendanceEmployees() {
  try {
    if (typeof eel === 'undefined') {
      console.warn('[DASHBOARD] Eel belum tersedia saat loadAttendanceEmployees');
      return;
    }
    
    console.log('[DASHBOARD] Loading attendance employees...');
    const employees = await eel.get_attendance_employees()();
    console.log('[DASHBOARD] Received employees:', employees);
    console.log('[DASHBOARD] Number of employees:', employees ? employees.length : 0);
    
    const tableBody = document.getElementById("attendanceTableBody");
    
    if (!tableBody) {
      console.warn('[DASHBOARD] attendanceTableBody element tidak ditemukan');
      return;
    }

    tableBody.innerHTML = "";

    if (!employees || employees.length === 0) {
      console.log('[DASHBOARD] No employees present today');
      const row = document.createElement("tr");
      row.innerHTML = `
        <td colspan="5" style="text-align: center; padding: 20px; color: var(--text-secondary);">
          Belum ada karyawan yang hadir hari ini
        </td>
      `;
      tableBody.appendChild(row);
      return;
    }

    console.log('[DASHBOARD] Rendering', employees.length, 'employees');
    employees.forEach((employee, index) => {
      console.log(`[DASHBOARD] Employee ${index + 1}:`, employee);
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${employee.employee_id || "N/A"}</td>
        <td>${employee.employee_name || "Unknown"}</td>
        <td>${employee.department || "Unknown"}</td>
        <td>
          <span class="status-badge-present">${employee.status || "Hadir"}</span>
        </td>
        <td>
          <button class="btn-detail" onclick="showEmployeeDetail('${employee.employee_id || ""}', '${(employee.employee_name || "Unknown").replace(/'/g, "\\'")}')">
            Detail
          </button>
        </td>
      `;
      tableBody.appendChild(row);
    });
    
    console.log('[DASHBOARD] Attendance employees loaded successfully');
  } catch (error) {
    console.error("[DASHBOARD] Error loading attendance employees:", error);
    console.error("[DASHBOARD] Error stack:", error.stack);
  }
}

// Fungsi untuk menampilkan detail karyawan
function showEmployeeDetail(employeeId, employeeName) {
  // TODO: Implementasi halaman detail atau modal untuk menampilkan detail karyawan
  // Untuk sementara, tampilkan alert dengan informasi dasar
  alert(`Detail Karyawan:\n\nID: ${employeeId}\nNama: ${employeeName}\n\nFitur detail lengkap akan segera tersedia.`)
  
  // Contoh implementasi yang bisa dikembangkan:
  // - Buka modal dengan detail lengkap
  // - Redirect ke halaman detail karyawan
  // - Tampilkan informasi seperti: jam masuk, jam keluar, total jam kerja, dll
}
