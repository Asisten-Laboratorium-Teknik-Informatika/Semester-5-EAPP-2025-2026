// ============================================
// USER UTILITIES - Fungsi untuk load user info
// ============================================

// Variabel global untuk menyimpan user info
let currentUserInfo = null;

/**
 * Load dan update user info dari sessionStorage
 * Bisa digunakan di semua halaman (dashboard, attendance, reports, dll)
 */
function loadUserInfo() {
  try {
    // Ambil user info dari sessionStorage
    const userStr = sessionStorage.getItem('currentUser');
    if (userStr) {
      currentUserInfo = JSON.parse(userStr);
      
      // Update sidebar user profile
      const avatar = document.querySelector('.user-profile .avatar');
      const userName = document.querySelector('.user-profile .user-name');
      const userRole = document.querySelector('.user-profile .user-role');
      
      if (avatar) {
        // Ambil inisial dari nama (2 huruf pertama)
        const name = currentUserInfo.name || currentUserInfo.username || 'U';
        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        avatar.textContent = initials;
      }
      
      if (userName) {
        userName.textContent = currentUserInfo.name || currentUserInfo.username || 'Unknown';
      }
      
      if (userRole) {
        // Tampilkan role dan department
        const role = currentUserInfo.role || 'employee';
        const department = currentUserInfo.department || 'Unknown';
        const roleText = role.charAt(0).toUpperCase() + role.slice(1);
        userRole.textContent = `${roleText.toUpperCase()} - ${department}`;
      }
      
      // Update header welcome message (jika ada)
      const headerTitle = document.querySelector('.header-title');
      if (headerTitle && currentUserInfo.name) {
        const firstName = currentUserInfo.name.split(' ')[0];
        // Hanya update jika header title mengandung "Welcome" atau "Welcome back"
        if (headerTitle.textContent.includes('Welcome')) {
          headerTitle.textContent = `Welcome back, ${firstName}!`;
        }
      }
      
      return currentUserInfo;
    } else {
      // Auto-set login status dan user data jika belum ada
      if (!sessionStorage.getItem('isLoggedIn')) {
        sessionStorage.setItem('isLoggedIn', 'true');
        sessionStorage.setItem('currentUser', JSON.stringify({
          employee_id: 'USER001',
          username: 'user',
          name: 'User',
          role: 'employee',
          department: 'IT'
        }));
        // Reload user info setelah set
        return loadUserInfo();
      }
      return null;
    }
  } catch (error) {
    console.error('Error loading user info:', error);
    return null;
  }
}

/**
 * Get current user info
 */
function getCurrentUserInfo() {
  if (!currentUserInfo) {
    loadUserInfo();
  }
  return currentUserInfo;
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
  return sessionStorage.getItem('isLoggedIn') === 'true';
}

/**
 * Logout user
 */
function logout() {
  // Tampilkan konfirmasi
  if (confirm('Apakah Anda yakin ingin logout?')) {
    // Hapus semua data session
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('currentUser');
    sessionStorage.removeItem('reset_work_stats_dashboard');
    sessionStorage.removeItem('reset_work_stats_attendance');
    
    // Reset variabel global
    currentUserInfo = null;
    
    // Redirect ke halaman login
    window.location.href = 'login.html';
  }
}

/**
 * Toggle profile dropdown
 */
function toggleProfileDropdown() {
  const dropdown = document.getElementById('profileDropdown');
  const profile = document.getElementById('userProfile');
  
  if (dropdown && profile) {
    dropdown.classList.toggle('show');
    profile.classList.toggle('active');
  }
}

/**
 * Close profile dropdown when clicking outside
 */
function closeProfileDropdown(event) {
  const dropdown = document.getElementById('profileDropdown');
  const profile = document.getElementById('userProfile');
  
  if (dropdown && profile && !profile.contains(event.target) && !dropdown.contains(event.target)) {
    dropdown.classList.remove('show');
    profile.classList.remove('active');
  }
}

// Setup profile dropdown
function setupProfileDropdown() {
  const profile = document.getElementById('userProfile');
  const dropdown = document.getElementById('profileDropdown');
  
  if (profile && dropdown) {
    // Toggle dropdown saat profile diklik
    profile.addEventListener('click', function(e) {
      e.stopPropagation();
      toggleProfileDropdown();
    });
    
    // Close dropdown saat klik di luar
    document.addEventListener('click', closeProfileDropdown);
  }
}

// Auto load user info saat page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    setupProfileDropdown();
  });
} else {
  loadUserInfo();
  setupProfileDropdown();
}

