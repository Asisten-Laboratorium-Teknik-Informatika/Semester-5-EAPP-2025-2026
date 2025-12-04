// signup.js
document.querySelector(".signup-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    const res = await eel.register_user(SESSION_ID, username, email, password)();
    if (!res.success) {
        alert(res.message);
        return;
    }

    localStorage.setItem("eel_user", JSON.stringify(res.user));
    alert("Pendaftaran berhasil");
    window.location.href = "../../pages/index.html";
});

