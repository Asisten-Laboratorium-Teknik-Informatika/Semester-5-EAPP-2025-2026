let room = null;

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const roomCode = params.get("room");
    if (!roomCode) return (window.location.href = "host.html");

    room = await eel.get_room_data(roomCode)();
    if (!room) return (window.location.href = "host.html");

    document.getElementById("roomNameDisplay").innerText = room.roomName;
    document.getElementById("roomCodeDisplay").innerText = room.roomCode;
    document.getElementById("hostNameDisplay").innerText = `Host: ${room.hostName}`;

    loadParticipants();
    setInterval(loadParticipants, 2000);
    setInterval(checkRoomStatus, 2000);
});

async function loadParticipants() {
    const users = await eel.get_participants(room.roomCode)() || [];
    const listEl = document.getElementById("participantsList");
    const countEl = document.getElementById("participantCount");

    countEl.innerText = users.length;
    listEl.innerHTML = "";

    if (users.length === 0) {
        listEl.innerHTML = `
            <div style="padding:20px; text-align:center; color:var(--text-muted);">
                Belum ada peserta bergabung.
            </div>`;
        return;
    }

    users.forEach(p => {
        const initial = p.participantName.charAt(0).toUpperCase();
        listEl.innerHTML += `
            <div class="p-item">
                <div class="p-name">
                    <div class="p-avatar">${initial}</div>
                    ${p.participantName}
                </div>
            </div>`;
    });
}

async function checkRoomStatus() {
    const status = await eel.get_room_status(room.roomCode)();
    if (status === "finished") {
        window.location.href = `index.html`;
    }
}

async function endSession() {
    if (!confirm("Akhiri sesi kuis untuk semua peserta?")) return;
    await eel.finish_quiz(room.roomCode)();
    window.location.href = `index.html`;
}
