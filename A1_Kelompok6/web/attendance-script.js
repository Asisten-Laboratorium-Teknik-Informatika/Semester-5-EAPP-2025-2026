// Variabel untuk menyimpan event IDs yang sudah ada di timeline
const timelineEventIds = new Set();

// Flag untuk mencegah loadAttendanceStatus meng-override button setelah clock in
let justClockedIn = false;
let clockInTimestamp = 0;
let attendanceStatusInterval = null; // Simpan interval ID untuk bisa di-clear

function resetAttendanceStatsIfNeeded() {
  const shouldReset = sessionStorage.getItem('reset_work_stats_attendance') === 'true';
  if (!shouldReset) return;
  sessionStorage.removeItem('reset_work_stats_attendance');

  const totalHoursEl = document.getElementById("totalHoursValue");
  if (totalHoursEl) {
    totalHoursEl.textContent = "0.00";
    totalHoursEl.title = "";
  }

  const statusEl = document.getElementById("clockStatus");
  if (statusEl) {
    statusEl.textContent = "Keluar";
  }

  const btn = document.getElementById("clockInBtn");
  if (btn) {
    btn.innerHTML = "<span>▶</span> Masuk";
    btn.classList.remove("clocked-in");
  }
}

// Fungsi untuk format waktu 24 jam (tetap 24 jam, tidak diubah ke 12 jam)
function formatTime12(time24) {
  if (!time24) return "--:--";
  
  // Pastikan time24 adalah string
  const timeStr = String(time24).trim();
  if (!timeStr) return "--:--";
  
  // Split waktu dengan error handling
  try {
    const timeParts = timeStr.split(":");
    if (timeParts.length < 2) {
      console.warn(`[FORMAT TIME] Invalid time format: ${time24}`);
      return "--:--";
    }
    
    const hours = timeParts[0] || "00";
    const minutes = timeParts[1] || "00";
    const seconds = timeParts[2] || null;
    
    // Validasi bahwa hours dan minutes adalah angka
    if (isNaN(parseInt(hours)) || isNaN(parseInt(minutes))) {
      console.warn(`[FORMAT TIME] Invalid time values: ${time24}`);
      return "--:--";
    }
    
    // Tetap tampilkan format 24 jam tanpa AM/PM
    if (seconds && !isNaN(parseInt(seconds))) {
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    }
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  } catch (error) {
    console.error(`[FORMAT TIME] Error formatting time ${time24}:`, error);
    return "--:--";
  }
}

// Fungsi untuk generate unique ID dari event
function getEventId(type, time) {
  return `${type}-${time}`;
}

// Fungsi untuk load status saat page load
async function loadAttendanceStatus() {
  try {
    if (typeof eel === 'undefined') {
      console.warn('[ATTENDANCE] Eel belum tersedia');
      return;
    }
    
    const userStr = sessionStorage.getItem('currentUser');
    if (!userStr) {
      alert('Anda harus login terlebih dahulu.');
      if (typeof redirectToLogin === 'function') {
        redirectToLogin();
      } else {
        window.location.href = 'login.html';
      }
      return;
    }
    let employeeId;
    try {
      const user = JSON.parse(userStr);
      employeeId = user.employee_id;
    } catch (e) {
      console.warn('[ATTENDANCE] Error parsing user data:', e);
      if (typeof redirectToLogin === 'function') {
        redirectToLogin();
      } else {
        window.location.href = 'login.html';
      }
      return;
    }
    if (!employeeId) {
      if (typeof redirectToLogin === 'function') {
        redirectToLogin();
      } else {
        window.location.href = 'login.html';
      }
      return;
    }
    
    const status = await eel.get_current_status(employeeId)();
    const btn = document.getElementById("clockInBtn");
    const statusEl = document.getElementById("clockStatus");

    if (!btn || !statusEl) {
      console.warn('[ATTENDANCE] Button or status element not found');
      return;
    }

    // Jika baru saja clock in, beri jeda sebelum mengizinkan override dari DB
    const now = Date.now();
    if (justClockedIn && now - clockInTimestamp < 4000) {
      console.log('[ATTENDANCE] Baru clock in, skip override agar UI stabil');
      if (status) {
        updateStats(status);
      }
      return;
    } else if (justClockedIn && now - clockInTimestamp >= 4000) {
      justClockedIn = false;
    }

    const isDbClockedIn = !!(status && (status.is_clocked_in === true || status.is_clocked_in === 1));
    const isLate = !!(status && (status.is_late === true || Number(status.late_minutes || 0) > 0));
    
    const desiredStatusText = isDbClockedIn ? (isLate ? "Masuk (Terlambat)" : "Masuk") : "Keluar";
    if (statusEl.textContent !== desiredStatusText) {
      statusEl.textContent = desiredStatusText;
    }
    
    const btnShowsClockedIn = btn.classList.contains("clocked-in");
    if (btnShowsClockedIn !== isDbClockedIn) {
      if (isDbClockedIn) {
        btn.innerHTML = "⏹ Keluar";
        btn.classList.add("clocked-in");
      } else {
        btn.innerHTML = "<span>▶</span> Masuk";
        btn.classList.remove("clocked-in");
      }
    }

    if (status) {
      updateStats(status);
    }
  } catch (error) {
    console.error("Error loading attendance status:", error);
  }
}

// Fungsi untuk load timeline dari backend
async function loadTimeline() {
  try {
    if (typeof eel === 'undefined') return;
    
    const timelineList = document.getElementById("timelineList");
    if (!timelineList) return;

    timelineList.innerHTML = "";
    timelineEventIds.clear();

    const userStr = sessionStorage.getItem('currentUser');
    if (!userStr) return;
    
    const user = JSON.parse(userStr);
    const employeeId = user.employee_id;
    if (!employeeId) return;

    const todayData = await eel.get_today_attendance(employeeId)();
    
    // Jika tidak ada data, tampilkan pesan kosong
    if (!todayData || todayData.length === 0) {
      const emptyMsg = document.createElement("li");
      emptyMsg.className = "timeline-item";
      emptyMsg.style.textAlign = "center";
      emptyMsg.style.padding = "20px";
      emptyMsg.style.color = "#999";
      emptyMsg.textContent = "Belum ada aktivitas hari ini";
      timelineList.appendChild(emptyMsg);
      return;
    }

    // Buat array untuk menyimpan semua event dengan timestamp
    const allEvents = [];

    // Kumpulkan semua event dari data hari ini
    todayData.forEach(record => {
      if (!record) return; // Skip jika record null/undefined
      
      // Validasi dan parse clock_in
      if (record.clock_in) {
        try {
          // Cek apakah terlambat
          const isLate = record.is_late === true || record.is_late === 1 || record.is_late === '1';
          const lateMinutes = parseFloat(record.late_minutes) || 0;
          const label = isLate && lateMinutes > 0 ? `Masuk (Terlambat ${Math.round(lateMinutes)} menit)` : "Masuk";
          
          // Parse timestamp dengan benar (format: YYYY-MM-DD HH:MM:SS)
          let dateStr = null;
          try {
            if (record.date) {
              // Jika date sudah dalam format YYYY-MM-DD
              if (typeof record.date === 'string' && record.date.match(/^\d{4}-\d{2}-\d{2}/)) {
                dateStr = record.date.split('T')[0]; // Handle jika ada waktu juga
              } else {
                dateStr = new Date(record.date).toISOString().split('T')[0];
              }
            } else {
              dateStr = new Date().toISOString().split('T')[0];
            }
          } catch (dateError) {
            console.warn('[TIMELINE] Error parsing date:', dateError);
            dateStr = new Date().toISOString().split('T')[0];
          }
          
          const timeStr = String(record.clock_in || '').trim();
          if (!timeStr || !timeStr.includes(':')) {
            console.warn('[TIMELINE] Invalid clock_in time:', record.clock_in);
            return; // Skip event ini jika waktu tidak valid
          }
          
          let timestamp = Date.now(); // Default ke waktu sekarang
          
          try {
            // Format: "YYYY-MM-DD HH:MM:SS" atau "HH:MM:SS"
            if (timeStr && timeStr.includes(':') && dateStr) {
              const fullDateTime = `${dateStr} ${timeStr}`;
              timestamp = new Date(fullDateTime.replace(/-/g, '/')).getTime();
              if (isNaN(timestamp)) {
                // Fallback jika parsing gagal
                console.warn('[TIMELINE] Failed to parse timestamp, using current time');
                timestamp = Date.now();
              }
            }
          } catch (e) {
            console.warn('[TIMELINE] Error parsing clock_in timestamp:', e);
            timestamp = Date.now();
          }
          
          allEvents.push({
            id: getEventId("Masuk", timeStr),
            type: "Masuk",
            time: timeStr,
            label: label,
            dotClass: isLate ? "dot-orange" : "dot-blue",
            timestamp: timestamp
          });
        } catch (error) {
          console.error('[TIMELINE] Error processing clock_in event:', error, record);
        }
      }
      
      // Validasi dan parse clock_out
      if (record.clock_out) {
        try {
          // Parse timestamp untuk clock out
          let dateStr = null;
          try {
            if (record.date) {
              if (typeof record.date === 'string' && record.date.match(/^\d{4}-\d{2}-\d{2}/)) {
                dateStr = record.date.split('T')[0];
              } else {
                dateStr = new Date(record.date).toISOString().split('T')[0];
              }
            } else {
              dateStr = new Date().toISOString().split('T')[0];
            }
          } catch (dateError) {
            console.warn('[TIMELINE] Error parsing date for clock_out:', dateError);
            dateStr = new Date().toISOString().split('T')[0];
          }
          
          const timeStr = String(record.clock_out || '').trim();
          if (!timeStr || !timeStr.includes(':')) {
            console.warn('[TIMELINE] Invalid clock_out time:', record.clock_out);
            return; // Skip event ini jika waktu tidak valid
          }
          
          let timestamp = Date.now();
          
          try {
            if (timeStr && timeStr.includes(':') && dateStr) {
              const fullDateTime = `${dateStr} ${timeStr}`;
              timestamp = new Date(fullDateTime.replace(/-/g, '/')).getTime();
              if (isNaN(timestamp)) {
                console.warn('[TIMELINE] Failed to parse clock_out timestamp, using current time');
                timestamp = Date.now();
              }
            }
          } catch (e) {
            console.warn('[TIMELINE] Error parsing clock_out timestamp:', e);
            timestamp = Date.now();
          }
          
          allEvents.push({
            id: getEventId("Keluar", timeStr),
            type: "Keluar",
            time: timeStr,
            label: "Keluar",
            dotClass: "dot-orange",
            timestamp: timestamp
          });
        } catch (error) {
          console.error('[TIMELINE] Error processing clock_out event:', error, record);
        }
      }
    });

    // Sort events berdasarkan timestamp (terbaru di atas)
    allEvents.sort((a, b) => b.timestamp - a.timestamp);

    // Tambahkan semua events ke timeline (dalam urutan terbaru di atas)
    allEvents.forEach(event => {
      try {
        // Validasi event sebelum menambahkan
        if (!event || !event.time || !event.label) {
          console.warn('[TIMELINE] Skipping invalid event:', event);
          return;
        }
        
        const li = document.createElement("li");
        li.className = "timeline-item";
        if (event.id) {
          li.setAttribute("data-event-id", event.id);
        }

        const dot = document.createElement("span");
        dot.className = `timeline-dot ${event.dotClass || "dot-blue"}`;

        const content = document.createElement("div");
        content.className = "timeline-content";

        const title = document.createElement("div");
        title.className = "timeline-event";
        title.textContent = event.label || "Event";

        const time = document.createElement("div");
        time.className = "timeline-time";
        time.textContent = formatTime12(event.time);

        content.appendChild(title);
        content.appendChild(time);

        li.appendChild(dot);
        li.appendChild(content);

        timelineList.appendChild(li);
        
        if (event.id) {
          timelineEventIds.add(event.id);
        }
      } catch (error) {
        console.error('[TIMELINE] Error adding event to timeline:', error, event);
      }
    });
  } catch (error) {
    console.error("Error loading timeline:", error);
    const timelineList = document.getElementById("timelineList");
    if (timelineList) {
      timelineList.innerHTML = "";
      const errorMsg = document.createElement("li");
      errorMsg.className = "timeline-item";
      errorMsg.style.textAlign = "center";
      errorMsg.style.padding = "20px";
      errorMsg.style.color = "#ef4444";
      errorMsg.textContent = "Error memuat data";
      timelineList.appendChild(errorMsg);
    }
  }
}

// Fungsi untuk update statistik
function updateStats(status) {
  // Update total jam
  const totalHoursEl = document.getElementById("totalHoursValue");
  if (totalHoursEl) {
    const totalHours = status
      ? (status.today_total_hours ?? status.current_session_hours ?? status.total_hours ?? 0)
      : 0
    totalHoursEl.textContent = totalHours.toFixed(2)
    if (status && status.is_clocked_in) {
      totalHoursEl.title = "Sedang berjalan"
    } else {
      totalHoursEl.title = ""
    }
  }
}

async function toggleClockIn() {
  const btn = document.getElementById("clockInBtn");
  const status = document.getElementById("clockStatus");

  if (!btn || !status) {
    alert("Error: Elemen UI tidak ditemukan. Silakan refresh halaman.");
    return;
  }

  if (btn.dataset.processing === 'true') {
    console.log('[CLOCK IN] Proses masih berjalan, abaikan klik ganda.');
    return;
  }

  btn.dataset.processing = 'true';
  btn.disabled = true;

  const resetButtonState = () => {
    btn.disabled = false;
    btn.dataset.processing = 'false';
  };

  // Ambil employee_id dari sessionStorage
  const userStr = sessionStorage.getItem('currentUser');
  if (!userStr) {
    alert('Anda harus login terlebih dahulu.');
    if (typeof redirectToLogin === 'function') {
      redirectToLogin();
    } else {
      window.location.href = 'login.html';
    }
    return;
  }
  let employeeId;
  try {
    const user = JSON.parse(userStr);
    employeeId = user.employee_id;
  } catch (e) {
    console.warn('[CLOCK IN] Error parsing user data:', e);
    if (typeof redirectToLogin === 'function') {
      redirectToLogin();
    } else {
      window.location.href = 'login.html';
    }
    return;
  }
  if (!employeeId) {
    if (typeof redirectToLogin === 'function') {
      redirectToLogin();
    } else {
      window.location.href = 'login.html';
    }
    return;
  }
    
    console.log("[CLOCK IN] Using employee_id:", employeeId);

    // Cek status dari database untuk menentukan apakah Clock In atau Clock Out
    const currentStatus = await eel.get_current_status(employeeId)();
    
    // Cek status real-time dari database
    if (currentStatus && currentStatus.is_clocked_in) {
      // Clock Out - wajib face detection juga
      console.log("[CLOCK OUT] Memulai face detection...");
      try {
        const faceResult = await eel.detect_face(employeeId)();
        if (!faceResult || !faceResult.success) {
          const errorMsg = faceResult?.message || "Gagal mendeteksi wajah. Pastikan kamera tersedia dan wajah terlihat jelas.";
          alert(`❌ Face Detection Clock Out Gagal!\n\n${errorMsg}\n\nSilakan coba lagi.`);
          await loadAttendanceStatus();
          resetButtonState();
          return;
        }
        console.log("[CLOCK OUT] Face detection berhasil:", faceResult.message);
      } catch (error) {
        console.error("[CLOCK OUT] Error saat face detection:", error);
        alert(`❌ Error saat face detection!\n\n${error.message || error}\n\nSilakan coba lagi.`);
        await loadAttendanceStatus();
        resetButtonState();
        return;
      }

      const result = await eel.clock_out(employeeId)();
      if (result.error) {
        alert(result.error);
        setTimeout(() => loadAttendanceStatus(), 500);
        resetButtonState();
        return;
      }
      
      // Update UI
      status.textContent = "Keluar";
      btn.innerHTML = "<span>▶</span> Masuk";
      btn.classList.remove("clocked-in");
      alert(`Keluar: ${formatTime12(result.clock_out)}\nTotal jam: ${result.total_hours} jam`);

      // Reload timeline dan status
      setTimeout(async () => {
        await loadTimeline();
        await loadAttendanceStatus();
      }, 500);
      
      // Trigger refresh dashboard
      localStorage.setItem('attendance_updated', Date.now().toString());
      window.postMessage({ type: 'attendance_updated' }, '*');
      resetButtonState();
      return;
  } else {
    // Clock In - WAJIB face detection dulu SEBELUM cek database
    console.log("[CLOCK IN] Memulai face detection...");
    
    try {
      // Panggil face detection dari Python - HARUS dilakukan dulu
      const faceResult = await eel.detect_face(employeeId)();
      
      if (!faceResult || !faceResult.success) {
        const errorMsg = faceResult?.message || "Gagal mendeteksi wajah. Pastikan kamera tersedia dan wajah terlihat jelas.";
        alert(`❌ Face Detection Gagal!\n\n${errorMsg}\n\nSilakan coba lagi.`);
        // Reload status untuk memastikan UI sync
        await loadAttendanceStatus();
        resetButtonState();
        return;
      }
      
      console.log("[CLOCK IN] Face detection berhasil:", faceResult.message);
    } catch (error) {
      console.error("[CLOCK IN] Error saat face detection:", error);
      alert(`❌ Error saat face detection!\n\n${error.message || error}\n\nSilakan coba lagi.`);
      // Reload status untuk memastikan UI sync
      await loadAttendanceStatus();
      resetButtonState();
      return;
    }
    
    // Setelah face detection berhasil, BARU cek database dan clock in
    console.log("[CLOCK IN] Face detection berhasil, melanjutkan clock in...");
    console.log("[CLOCK IN] Calling eel.clock_in with employeeId:", employeeId);
    
    // Pastikan employee_id dikirim dengan benar
    const record = await eel.clock_in(employeeId)();
    console.log("[CLOCK IN] Clock in response:", record);
    
    console.log("[CLOCK IN] Response from backend:", record);
    
    if (!record) {
      alert("❌ Error: Tidak ada response dari server. Silakan coba lagi.");
      resetButtonState();
      return;
    }
    
    if (record.error) {
      // Jika error "sudah clock in", tetap reload status untuk sync
      if (record.error.includes("sudah clock in")) {
        console.log("[CLOCK IN] User sudah clock in sebelumnya, reloading status...");
        // Reload status untuk update UI
        await loadAttendanceStatus();
        await loadTimeline();
        // Tampilkan info bahwa sudah clock in
        alert("ℹ️ " + record.error + "\n\nStatus akan diperbarui secara real-time.");
      } else {
        // Error lain, tampilkan dan reload
        alert("❌ " + record.error);
        await loadAttendanceStatus();
        await loadTimeline();
      }
      resetButtonState();
      return;
    }
    
    console.log("[CLOCK IN] Clock in berhasil! Record:", record);
    console.log("[CLOCK IN] Employee ID yang digunakan:", employeeId);
    
    // Tandai bahwa UI baru saja melakukan clock in agar polling tidak override
    justClockedIn = true;
    clockInTimestamp = Date.now();
    setTimeout(() => {
      if (Date.now() - clockInTimestamp >= 4000) {
        justClockedIn = false;
      }
    }, 5000);

    // Update UI LANGSUNG setelah clock in berhasil (SYNCHRONOUS, TIDAK MENUNGGU ASYNC)
    console.log("[CLOCK IN] Updating button and status immediately (SYNC)...");
    
    // Update status text
    if (status) {
      status.textContent = "Masuk";
      console.log("[CLOCK IN] Status text updated to 'Masuk'");
    } else {
      console.warn("[CLOCK IN] Status element not found!");
    }
    
    // Update button - PASTIKAN langsung ter-update
    if (btn) {
      // Hapus class lama dulu
      btn.classList.remove("clocked-in");
      // Update innerHTML
      btn.innerHTML = "⏹ Keluar";
      // Tambah class baru
      btn.classList.add("clocked-in");
      console.log("[CLOCK IN] Button updated to 'Keluar' - innerHTML:", btn.innerHTML, "classList:", btn.classList.toString());
      
      // Force reflow untuk memastikan browser render perubahan
      void btn.offsetWidth;
    } else {
      console.warn("[CLOCK IN] Button element not found!");
    }
    
    // Refresh timeline saja (tidak perlu loadAttendanceStatus karena akan di-block)
    console.log("[CLOCK IN] Refreshing timeline from database (async)...");
    loadTimeline().then(() => {
      console.log("[CLOCK IN] loadTimeline completed");
    }).catch(err => {
      console.error("[CLOCK IN] Error in loadTimeline:", err);
    });
    
    // Delay loadAttendanceStatus untuk memastikan database sudah commit
    // Dengan smart update, loadAttendanceStatus tidak akan meng-override button jika sudah benar
    setTimeout(() => {
      console.log("[CLOCK IN] Delayed loadAttendanceStatus after 2 seconds...");
      loadAttendanceStatus().then(() => {
        console.log("[CLOCK IN] loadAttendanceStatus completed");
        // Resume interval setelah 2 detik lagi
        setTimeout(() => {
          if (!attendanceStatusInterval) {
            console.log("[CLOCK IN] Resuming attendance status interval");
            attendanceStatusInterval = setInterval(async () => {
              await loadAttendanceStatus();
              await loadTimeline();
            }, 2000);
          }
        }, 2000);
      }).catch(err => {
        console.error("[CLOCK IN] Error in loadAttendanceStatus:", err);
      });
    }, 2000); // Delay 2 detik untuk memastikan database sudah commit
    
    // Update statistik
    if (record.clock_in) {
      updateStats({
        is_clocked_in: true,
        clock_in_time: record.clock_in,
        total_hours: 0
      });
    }
    
    // Trigger refresh dashboard IMMEDIATELY
    try {
      const timestamp = Date.now();
      console.log("[CLOCK IN] Broadcasting attendance update to dashboard...");
      
      // Broadcast ke semua window bahwa ada update attendance
      window.localStorage.setItem('attendance_updated', timestamp.toString());
      
      // PostMessage untuk cross-tab communication
      window.postMessage({ type: 'attendance_updated', timestamp: timestamp }, '*');
      
      // Jika di halaman dashboard, langsung refresh
      if (window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/')) {
        console.log("[CLOCK IN] On dashboard page, refreshing immediately...");
        // Panggil langsung updateDashboardStatus jika fungsi tersedia
        if (typeof updateDashboardStatus === 'function') {
          setTimeout(() => {
            updateDashboardStatus();
            if (typeof loadAttendanceEmployees === 'function') {
              loadAttendanceEmployees();
            }
          }, 500);
        }
      }
      
      console.log("[CLOCK IN] Broadcast sent successfully");
    } catch (e) {
      console.error('[CLOCK IN] Error broadcasting attendance update:', e);
    }
    
    // Pastikan button tetap ter-update sebelum alert
    // Double-check button state - FORCE UPDATE
    const btnCheck = document.getElementById("clockInBtn");
    const statusCheck = document.getElementById("clockStatus");
    
    if (btnCheck) {
      // FORCE UPDATE button - tidak peduli state sebelumnya
      btnCheck.innerHTML = "⏹ Keluar";
      btnCheck.classList.add("clocked-in");
      console.log("[CLOCK IN] Button FORCE updated to 'Keluar' - innerHTML:", btnCheck.innerHTML);
      // Force reflow
      void btnCheck.offsetWidth;
    } else {
      console.error("[CLOCK IN] Button element not found for double-check!");
    }
    
    if (statusCheck) {
      statusCheck.textContent = "Masuk";
      console.log("[CLOCK IN] Status FORCE updated to 'Masuk'");
    } else {
      console.error("[CLOCK IN] Status element not found for double-check!");
    }
    
    // Tampilkan pesan validasi terlambat (SETELAH refresh status)
    console.log("[CLOCK IN] Record data:", record);
    console.log("[CLOCK IN] is_late:", record.is_late, "late_minutes:", record.late_minutes);
    
    // Pastikan is_late dan late_minutes tersedia
    const isLate = record.is_late === true || record.is_late === 1;
    const lateMinutes = record.late_minutes || 0;
    
    // Tampilkan alert dan redirect ke dashboard setelah ditutup
    if (isLate && lateMinutes > 0) {
      const lateMinutesRounded = Math.round(lateMinutes);
      alert(`⚠️ TERLAMBAT!\n\nWaktu masuk: ${formatTime12(record.clock_in)}\nWaktu yang diharapkan: ${formatTime12(record.expected_clock_in || '08:30:00')}\nTerlambat: ${lateMinutesRounded} menit\n\nJam kerja: 08:30 - 17:00\n\nMengalihkan ke dashboard...`);
    } else {
      alert(`✅ TEPAT WAKTU!\n\nMasuk pada: ${formatTime12(record.clock_in)}\nWaktu yang diharapkan: ${formatTime12(record.expected_clock_in || '08:30:00')}\n\nJam kerja: 08:30 - 17:00\n\nMengalihkan ke dashboard...`);
    }
    
    // Setelah alert ditutup, pastikan button masih ter-update
    const btnAfterAlert = document.getElementById("clockInBtn");
    const statusAfterAlert = document.getElementById("clockStatus");
    if (btnAfterAlert) {
      btnAfterAlert.innerHTML = "⏹ Keluar";
      btnAfterAlert.classList.add("clocked-in");
      console.log("[CLOCK IN] Button updated again after alert - innerHTML:", btnAfterAlert.innerHTML);
    }
    if (statusAfterAlert) {
      statusAfterAlert.textContent = "Masuk";
      console.log("[CLOCK IN] Status updated again after alert");
    }
    
    // Redirect ke dashboard setelah alert ditutup
    console.log("[CLOCK IN] Redirecting to dashboard...");
    setTimeout(() => {
      // Simpan flag bahwa baru saja clock in untuk trigger refresh di dashboard
      localStorage.setItem('just_clocked_in', 'true');
      localStorage.setItem('attendance_updated', Date.now().toString());
      
      // Redirect ke dashboard
      window.location.href = 'index.html';
    }, 500); // Delay 500ms setelah alert ditutup
    
    // Refresh lagi setelah alert untuk memastikan data ter-update dan button tetap benar
    setTimeout(async () => {
      console.log("[CLOCK IN] Final refresh setelah alert...");
      await loadAttendanceStatus();
      await loadTimeline();
      
      // Double-check button state lagi setelah refresh
      const btnFinal = document.getElementById("clockInBtn");
      const statusFinal = document.getElementById("clockStatus");
      if (btnFinal && !btnFinal.classList.contains("clocked-in")) {
        console.log("[CLOCK IN] Button masih belum ter-update setelah refresh, forcing update...");
        btnFinal.innerHTML = "⏹ Keluar";
        btnFinal.classList.add("clocked-in");
      }
      if (statusFinal && statusFinal.textContent !== "Masuk") {
        console.log("[CLOCK IN] Status masih belum ter-update setelah refresh, forcing update...");
        statusFinal.textContent = "Masuk";
      }
      
      console.log("[CLOCK IN] Final refresh completed");
    }, 300);
    
    console.log("[CLOCK IN] Clock in process completed");
    resetButtonState();
  }
}

function addTimelineEvent(label, timeStr, dotColorClass, eventId) {
  const list = document.getElementById("timelineList");
  if (!list) return;

  // Jika eventId diberikan, cek apakah sudah ada
  if (eventId && timelineEventIds.has(eventId)) {
    return; // Jangan tambahkan jika sudah ada
  }

  const li = document.createElement("li");
  li.className = "timeline-item";
  if (eventId) {
    li.setAttribute("data-event-id", eventId);
  }

  const dot = document.createElement("span");
  dot.className = `timeline-dot ${dotColorClass || ""}`.trim();

  const content = document.createElement("div");
  content.className = "timeline-content";

  const title = document.createElement("div");
  title.className = "timeline-event";
  title.textContent = label;

  const time = document.createElement("div");
  time.className = "timeline-time";
  time.textContent = timeStr;

  content.appendChild(title);
  content.appendChild(time);

  li.appendChild(dot);
  li.appendChild(content);

  list.insertBefore(li, list.firstChild);

  // Tambahkan eventId ke Set jika diberikan
  if (eventId) {
    timelineEventIds.add(eventId);
  }
}

function scrollToTimeline() {
  const card = document.getElementById("timelineCard");
  if (!card) return;
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Update jam digital real-time (format 24 jam)
function updateDigitalClock() {
  const now = new Date();
  // Tetap gunakan format 24 jam (tidak dikonversi ke 12 jam)
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  
  const clockEl = document.getElementById("digitalClock");
  if (clockEl) {
    clockEl.textContent = `${hours}:${minutes}:${seconds}`;
  }

  // Update tanggal
  const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateEl = document.getElementById("clockDate");
  if (dateEl) {
    dateEl.textContent = now.toLocaleDateString('id-ID', dateOptions);
  }
}

// Load data saat halaman dimuat
document.addEventListener("DOMContentLoaded", async function() {
  // Update jam digital
  updateDigitalClock();
  setInterval(updateDigitalClock, 1000);

  resetAttendanceStatsIfNeeded();

  // Load status dan timeline saat halaman dimuat
  // Coba beberapa kali jika eel belum siap
  let retries = 0;
  const maxRetries = 10;
  
  async function tryLoadData() {
    if (typeof eel !== 'undefined') {
      // Load status REAL-TIME dari database
      await loadAttendanceStatus();
      await loadTimeline();
      
      // Update setiap 2 detik untuk real-time (lebih cepat)
      // Simpan interval ID untuk bisa di-clear jika perlu
      attendanceStatusInterval = setInterval(async () => {
        await loadAttendanceStatus();
        await loadTimeline();
      }, 2000);
      
      // Event listener untuk refresh saat ada perubahan dari localStorage/postMessage
      window.addEventListener('storage', async (e) => {
        if (e.key === 'attendance_updated') {
          console.log("[ATTENDANCE] Detected attendance update from storage, refreshing...");
          await loadAttendanceStatus();
          await loadTimeline();
        }
      });
      
      // Event listener untuk postMessage
      window.addEventListener('message', async (e) => {
        if (e.data && e.data.type === 'attendance_updated') {
          console.log("[ATTENDANCE] Detected attendance update from postMessage, refreshing...");
          await loadAttendanceStatus();
          await loadTimeline();
        }
      });
    } else if (retries < maxRetries) {
      retries++;
      setTimeout(tryLoadData, 500);
    }
  }
  
  tryLoadData();
});
