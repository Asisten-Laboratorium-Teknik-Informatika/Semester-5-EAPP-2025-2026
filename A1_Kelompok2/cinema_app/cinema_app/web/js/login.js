async function login() {
  const user = document.getElementById("username").value.trim();
  const pass = document.getElementById("password").value;
  if (!user || !pass) {
    alert("Username dan password wajib diisi!");
    return;
  }
  try {
    const result = await eel.login(user, pass)();
    if (result === "admin") {
      window.location.href = "admin.html";
    } else if (result === "user") {
      window.location.href = "home.html";
    } else {
      alert("Login gagal! Username atau password salah.");
    }
  } catch (error) {
    alert("Error koneksi login: " + error.message);
    console.error("Login error:", error);
  }
}
