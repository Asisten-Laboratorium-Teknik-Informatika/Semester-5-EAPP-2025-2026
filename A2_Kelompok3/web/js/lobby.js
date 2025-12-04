let room = null;
let participants = [];
let participant = null;
let quizStartedAlertShown = false;

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const roomCode = params.get("room");

    participant = JSON.parse(localStorage.getItem("kilas_participant"));
    if (!participant) {
        alert("Data peserta hilang, silakan join ulang");
        return window.location.href = "join.html";
    }

    room = await eel.get_room_data(roomCode)();
    if (!room) return alert("Room tidak ditemukan!");

    document.getElementById("roomCode").innerText = room.roomCode;
    document.querySelector(".info-row:nth-child(2) .info-value").innerText = room.roomName;
    document.querySelector(".info-row:nth-child(3) .info-value").innerText = room.hostName;

    const soalEl = document.querySelector(".info-row:nth-child(4)");
    soalEl.innerHTML =
        `<span class="info-label"><i class="fa-solid fa-layer-group"></i> ${room.totalQuestions} Soal</span>
         <span class="info-label"><i class="fa-solid fa-shuffle"></i> ${room.mode === "random" ? "Acak" : "Berurutan"}</span>`;

    loadParticipants();
    setInterval(loadParticipants, 2000);
    setInterval(checkStart, 1500);
});

async function loadParticipants() {
    participants = await eel.get_participants(room.roomCode)();
    const list = document.getElementById("pList");
    const count = document.getElementById("pCount");

    list.innerHTML = "";
    participants.forEach(p => {
        const avatar = p.participantName.charAt(0).toUpperCase();
        list.innerHTML += `
            <div class="p-item">
                <div class="p-avatar" style="background:#4f46e5;">${avatar}</div>
                <span class="p-name">${p.participantName}${p.participantName === participant.name ? " (Anda)" : ""}</span>
                <span class="p-status"><i class="fa-solid fa-circle-check"></i></span>
            </div>
        `;
    });

    count.textContent = participants.length;
}

async function checkStart() {
    const status = await eel.get_room_status(room.roomCode)();

    if (status === "started" && quizStartedAlertShown === false) {
        quizStartedAlertShown = true;
        document.getElementById("statusText").innerText = "Kuis Dimulai!";

        alert("Kuis dimulai! Siap-siap menjawab pertanyaan!");
        setTimeout(() => {
            window.location.href = `public-play.html?room=${room.roomCode}`;
        }, 900);
    }
}


function confirmExit() {
    if (!confirm("Yakin mau keluar dari room?")) return;
    localStorage.removeItem("kilas_participant");
    window.location.href = "join.html";
}
