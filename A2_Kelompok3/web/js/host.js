// host.js
async function handleCreateRoom(e) {
    e.preventDefault();
    const btn = document.querySelector('.btn-submit');
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Memproses...';
    btn.disabled = true;

    const roomName = document.getElementById("roomName").value.trim();
    const mode = document.getElementById("mode").value;
    const totalQuestions = Number(document.getElementById("totalQuestions").value);

    const user = await eel.get_current_user(SESSION_ID)();
    if (!user) {
        alert("Session habis, silakan login ulang.");
        window.location.href = "../pages/auth/login.html";
        return;
    }

    const hostName = user.username;
    const roomCode = Math.floor(100000 + Math.random() * 900000);

    const saved = await eel.create_room(roomCode, roomName, hostName, mode, totalQuestions)();
    if (!saved.success) {
        alert(saved.message);
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-rocket"></i> Buat Room Sekarang';
        return;
    }

    alert("Room berhasil dibuat!");

    localStorage.setItem("last_room", roomCode);

  
    window.location.href = "dashboard.html?room=" + roomCode;

}
