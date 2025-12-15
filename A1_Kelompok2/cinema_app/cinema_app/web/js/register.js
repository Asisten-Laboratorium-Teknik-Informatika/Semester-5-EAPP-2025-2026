document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Ganti fetch ke Eel call
    const result = await eel.register(username, password)();
    alert(result.message);
    if (result.success) {
      window.location.href = "login.html"; // Redirect ke login setelah sukses
    }
  });
});
