document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const roomCode = String(urlParams.get("room")).trim();

    if (!roomCode) {
        alert("Room code hilang!");
        return (window.location.href = "host.html");
    }

    const room = await eel.get_room_data(roomCode)();
    if (!room) {
        alert("Room tidak ditemukan di database!");
        return (window.location.href = "host.html");
    }

    const questions = await eel.get_questions(roomCode)() || [];
    const totalCreated = questions.length;

    const roomNameEl = document.querySelector(".room-name-large");
    const hostNameEl = document.querySelector(".host-label");
    const roomCodeEl = document.getElementById("roomCode");
    const modeLabel = document.querySelector(".mode-value");
    const questionStatus = document.querySelector(".question-progress");
    const progressBar = document.querySelector(".progress-bar");
    const timeCreatedEl = document.querySelector(".time-created");
    const createQuestionLink = document.querySelector(".btn-create-q");
    const statusText = document.querySelector(".status-text");
    const statusDot = document.querySelector(".status-dot");
    const startButton = document.querySelector(".btn-start-quiz");

    roomNameEl.textContent = room.roomName;
    hostNameEl.textContent = `Host: ${room.hostName}`;
    roomCodeEl.textContent = room.roomCode;

    modeLabel.innerHTML =
        room.mode === "random"
            ? `<i class="fa-solid fa-shuffle" style="color:var(--secondary)"></i> Acak`
            : `<i class="fa-solid fa-list-ol" style="color:var(--secondary)"></i> Berurutan`;

    questionStatus.textContent = `${totalCreated} dari ${room.totalQuestions}`;
    progressBar.style.width = `${(totalCreated / room.totalQuestions) * 100}%`;

    const createdTime = new Date(room.createdAt);
    const now = new Date();
    const diff = Math.floor((now - createdTime) / 1000);
    timeCreatedEl.textContent = diff < 60 ? "Baru saja" : createdTime.toLocaleString();

    createQuestionLink.href = `create-questions.html?room=${room.roomCode}`;

    function setWaiting() {
        statusText.textContent = "Menunggu Soal";
        statusText.style.color = "var(--warning)";
        statusDot.style.background = "var(--warning)";
        startButton.disabled = true;
        startButton.classList.remove("ready");
    }

    function setReady() {
        statusText.textContent = "Siap Dimulai";
        statusText.style.color = "var(--success)";
        statusDot.style.background = "var(--success)";
        startButton.disabled = false;
        startButton.classList.add("ready");
    }

    if (totalCreated > 0) {
        setReady();
        await eel.update_room_status(room.roomCode, "ready")();
        room.status = "ready";
    } else {
        setWaiting();
        await eel.update_room_status(room.roomCode, "waiting")();
        room.status = "waiting";
    }

    startButton.addEventListener("click", async () => {
        await eel.start_quiz(roomCode)();
        window.location.href = `host-play.html?room=${roomCode}`;
    });

    async function realtime() {
        const questions = await eel.get_questions(room.roomCode)() || [];
        const totalCreated = questions.length;

        questionStatus.textContent = `${totalCreated} dari ${room.totalQuestions}`;
        progressBar.style.width = `${(totalCreated / room.totalQuestions) * 100}%`;

        if (totalCreated > 0 && room.status !== "ready") {
            await eel.update_room_status(room.roomCode, "ready")();
            room.status = "ready";
            setReady();
        } else if (totalCreated === 0 && room.status !== "waiting") {
            await eel.update_room_status(room.roomCode, "waiting")();
            room.status = "waiting";
            setWaiting();
        }

        const status = await eel.get_room_status(room.roomCode)();
        if (status === "started") {
            window.location.href = `host-play.html?room=${room.roomCode}`;
        }
    }

    realtime();
    setInterval(realtime, 2000);
});

function copyCode() {
    const code = document.getElementById("roomCode").innerText;
    navigator.clipboard.writeText(code);
    const btn = document.querySelector(".btn-icon-only");
    const before = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check" style="color:#10b981"></i>';
    btn.style.borderColor = "#10b981";
    setTimeout(() => {
        btn.innerHTML = before;
        btn.style.borderColor = "";
    }, 2000);
}
