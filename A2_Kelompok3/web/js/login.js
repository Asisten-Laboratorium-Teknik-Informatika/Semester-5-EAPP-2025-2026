// login.js
document.querySelector(".login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    const res = await eel.login_user(SESSION_ID, email, password)();
    if (!res.success) {
        alert(res.message);
        return;
    }

    localStorage.setItem("eel_user", JSON.stringify(res.user));
    alert("Login berhasil");
    window.location.href = "../../pages/index.html";
});

document.getElementById("togglePassword").addEventListener("click", () => {
    const input = document.getElementById("password");
    input.type = input.type === "password" ? "text" : "password";
});
