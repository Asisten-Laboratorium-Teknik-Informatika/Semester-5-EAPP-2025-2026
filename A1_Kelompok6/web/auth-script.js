// ============================================
// AUTH SCRIPT (Login & Register)
// ============================================

// Toggle password visibility
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const eyeIcon = document.getElementById(inputId + '-eye');
  
  if (input.type === 'password') {
    input.type = 'text';
    eyeIcon.classList.remove('fa-eye');
    eyeIcon.classList.add('fa-eye-slash');
  } else {
    input.type = 'password';
    eyeIcon.classList.remove('fa-eye-slash');
    eyeIcon.classList.add('fa-eye');
  }
}

// Show error message
function showError(message) {
  const errorDiv = document.getElementById('errorMessage');
  if (errorDiv) {
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    errorDiv.style.display = 'flex';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, 5000);
  }
}

// Show success message
function showSuccess(message) {
  const successDiv = document.getElementById('successMessage');
  if (successDiv) {
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    successDiv.style.display = 'flex';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
      successDiv.style.display = 'none';
    }, 5000);
  }
}

// Hide messages
function hideMessages() {
  const errorDiv = document.getElementById('errorMessage');
  const successDiv = document.getElementById('successMessage');
  if (errorDiv) errorDiv.style.display = 'none';
  if (successDiv) successDiv.style.display = 'none';
}

// ============================================
// LOGIN FORM HANDLER
// ============================================
const loginForm = document.getElementById('loginForm');

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    // Validation
    if (!username || !password) {
      showError('Username dan password harus diisi!');
      return;
    }

    // Disable button
    const submitButton = loginForm.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

    try {
      // Check if eel is available
      if (typeof eel === 'undefined') {
        showError('Backend belum siap. Silakan refresh halaman.');
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
        return;
      }

      console.log('[LOGIN] Attempting login for:', username);
      
      // Call backend login function with timeout (diperpanjang menjadi 20 detik)
      const loginPromise = eel.login_user(username, password)();
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Login timeout - Silakan coba lagi!')), 20000)
      );
      
      let result;
      try {
        result = await Promise.race([loginPromise, timeoutPromise]);
      } catch (raceError) {
        // Jika timeout, coba cancel promise dan berikan error yang lebih informatif
        console.error('[LOGIN] Promise race error:', raceError);
        if (raceError.message && raceError.message.includes('timeout')) {
          throw new Error('Waktu tunggu habis. Pastikan XAMPP MySQL sudah berjalan dan database tersedia.');
        }
        throw raceError;
      }
      
      console.log('[LOGIN] Response:', result);
      
      if (result && result.success) {
        // Store user info if remember me is checked
        if (rememberMe) {
          localStorage.setItem('rememberUsername', username);
        } else {
          localStorage.removeItem('rememberUsername');
        }

        // Store current user session
        sessionStorage.setItem('currentUser', JSON.stringify(result.user));
        sessionStorage.setItem('isLoggedIn', 'true');
        sessionStorage.setItem('reset_work_stats_dashboard', 'true');
        sessionStorage.setItem('reset_work_stats_attendance', 'true');

        // Show success message
        showSuccess('Login berhasil! Mengalihkan...');

        // Redirect to dashboard after 1 second
        setTimeout(() => {
          window.location.href = 'index.html';
        }, 1000);
      } else {
        const errorMsg = result?.message || 'Login gagal! Username atau password salah.';
        console.error('[LOGIN ERROR]', errorMsg);
        showError(errorMsg);
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
      }
    } catch (error) {
      console.error('[LOGIN ERROR]', error);
      let errorMsg = 'Terjadi kesalahan saat login. ';
      
      if (error.message && error.message.includes('timeout')) {
        errorMsg += 'Waktu tunggu habis. Silakan coba lagi.';
      } else if (error.message) {
        errorMsg += error.message;
      } else {
        errorMsg += 'Silakan coba lagi atau periksa console untuk detail error.';
      }
      
      showError(errorMsg);
      submitButton.disabled = false;
      submitButton.innerHTML = originalText;
    }
  });

  // Load remembered username
  window.addEventListener('DOMContentLoaded', () => {
    const rememberedUsername = localStorage.getItem('rememberUsername');
    if (rememberedUsername) {
      document.getElementById('username').value = rememberedUsername;
      document.getElementById('rememberMe').checked = true;
    }
  });
}

// ============================================
// REGISTER FORM HANDLER
// ============================================
const registerForm = document.getElementById('registerForm');

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const fullName = document.getElementById('fullName').value.trim();
    const employeeId = document.getElementById('employeeId').value.trim();
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const role = document.getElementById('role').value;
    const department = document.getElementById('department').value.trim();
    const agreeTerms = document.getElementById('agreeTerms').checked;

    // Validation
    if (!fullName || !username || !password || !confirmPassword || !role) {
      showError('Nama lengkap, username, password, dan role harus diisi!');
      return;
    }

    if (password.length < 6) {
      showError('Password harus minimal 6 karakter!');
      return;
    }

    if (password !== confirmPassword) {
      showError('Password dan konfirmasi password tidak cocok!');
      return;
    }

    if (!agreeTerms) {
      showError('Anda harus menyetujui syarat dan ketentuan!');
      return;
    }

    // Disable button
    const submitButton = registerForm.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

    try {
      // Check if eel is available
      if (typeof eel === 'undefined') {
        showError('Backend belum siap. Silakan refresh halaman.');
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
        return;
      }

      // Call backend register function
      // Employee ID bisa kosong (akan di-generate otomatis)
      const result = await eel.register_user(
        employeeId || '',  // Bisa kosong, akan di-generate otomatis
        username, 
        password, 
        role,
        fullName,  // Nama lengkap
        department || ''  // Department (opsional)
      )();
      
      if (result.success) {
        showSuccess('Registrasi berhasil! Mengalihkan ke halaman login...');

        // Redirect to login page after 2 seconds
        setTimeout(() => {
          window.location.href = 'login.html';
        }, 2000);
      } else {
        // Check if error is about username already exists
        const errorMsg = result.message || 'Registrasi gagal! Silakan coba lagi.';
        
        if (errorMsg.includes('sudah digunakan') || errorMsg.includes('sudah terdaftar')) {
          // Show special message with link to login
          const loginLink = '<a href="login.html" style="color: #3b82f6; text-decoration: underline; font-weight: bold;">Login di sini</a>';
          showError(`Akun dengan username tersebut sudah terdaftar! ${loginLink}`);
        } else {
          showError(errorMsg);
        }
        
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
      }
    } catch (error) {
      console.error('Register error:', error);
      showError('Terjadi kesalahan saat registrasi. Silakan coba lagi.');
      submitButton.disabled = false;
      submitButton.innerHTML = originalText;
    }
  });

  // Real-time password confirmation validation
  const confirmPasswordInput = document.getElementById('confirmPassword');
  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', function() {
      const password = document.getElementById('regPassword').value;
      const confirmPassword = this.value;

      if (confirmPassword && password !== confirmPassword) {
        this.setCustomValidity('Password tidak cocok');
        this.style.borderColor = '#ef4444';
      } else {
        this.setCustomValidity('');
        this.style.borderColor = '';
      }
    });
  }

  // Real-time username availability check
  const usernameInput = document.getElementById('regUsername');
  const usernameStatus = document.getElementById('usernameStatus');
  const usernameHint = document.getElementById('usernameHint');
  let usernameCheckTimeout = null;

  if (usernameInput && usernameStatus) {
    usernameInput.addEventListener('input', function() {
      const username = this.value.trim();
      
      // Clear previous timeout
      if (usernameCheckTimeout) {
        clearTimeout(usernameCheckTimeout);
      }

      // Hide status if username is empty or too short
      if (username.length < 3) {
        usernameStatus.style.display = 'none';
        usernameHint.style.display = 'block';
        this.style.borderColor = '';
        return;
      }

      // Debounce: wait 500ms after user stops typing
      usernameCheckTimeout = setTimeout(async () => {
        try {
          if (typeof eel !== 'undefined') {
            const result = await eel.check_username_available(username)();
            
            if (result.available === false) {
              // Username sudah terdaftar
              usernameStatus.innerHTML = `
                <div style="color: #ef4444; display: flex; align-items: center; gap: 6px;">
                  <i class="fas fa-exclamation-circle"></i>
                  <span>Username sudah terdaftar! <a href="login.html" style="color: #3b82f6; text-decoration: underline; font-weight: bold;">Login di sini</a></span>
                </div>
              `;
              usernameStatus.style.display = 'block';
              usernameHint.style.display = 'none';
              this.style.borderColor = '#ef4444';
            } else {
              // Username tersedia
              usernameStatus.innerHTML = `
                <div style="color: #10b981; display: flex; align-items: center; gap: 6px;">
                  <i class="fas fa-check-circle"></i>
                  <span>Username tersedia</span>
                </div>
              `;
              usernameStatus.style.display = 'block';
              usernameHint.style.display = 'none';
              this.style.borderColor = '#10b981';
            }
          }
        } catch (error) {
          console.error('Error checking username:', error);
          usernameStatus.style.display = 'none';
          usernameHint.style.display = 'block';
        }
      }, 500); // Wait 500ms after user stops typing
    });

    // Clear status when user focuses out
    usernameInput.addEventListener('blur', function() {
      // Keep status visible if there's an error
      const username = this.value.trim();
      if (username.length >= 3 && usernameStatus.innerHTML.includes('sudah terdaftar')) {
        // Keep error message visible
        return;
      }
    });
  }
}

// ============================================
// CHECK AUTHENTICATION STATUS
// ============================================
function checkAuthStatus() {
  const isLoggedIn = sessionStorage.getItem('isLoggedIn');
  const currentPath = window.location.pathname;
  const currentPage = currentPath.split('/').pop();

  // If user is on login/register page and already logged in, redirect to dashboard
  if ((currentPage === 'login.html' || currentPage === 'register.html') && isLoggedIn === 'true') {
    window.location.href = 'index.html';
  }

  // If user is on protected pages and not logged in, redirect to login
  if (currentPage !== 'login.html' && currentPage !== 'register.html' && isLoggedIn !== 'true') {
    window.location.href = 'login.html';
  }
}

// Check auth status on page load
window.addEventListener('DOMContentLoaded', checkAuthStatus);

