// create-questions.js
let room = null;
let questions = [];
let MAX_QUESTIONS = 0;

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const roomCode = params.get("room");
    if (!roomCode) return;

    room = await eel.get_room_data(roomCode)();
    if (!room) return alert("Room tidak ditemukan");

    const backBtn = document.getElementById("btnBackDashboard");
    if (backBtn) {
        backBtn.href = `dashboard.html?room=${room.roomCode}`;
        backBtn.addEventListener("click", (e) => {
            e.preventDefault();
            location.href = `dashboard.html?room=${room.roomCode}`;
        });
    }

    MAX_QUESTIONS = room.totalQuestions;

    document.querySelector(".room-info h2").textContent = room.roomName;
    document.querySelector(".badge-code").textContent = room.roomCode;
    document.querySelector(".room-meta span:nth-child(2)").innerHTML =
        room.mode === "random"
            ? '<i class="fa-solid fa-shuffle"></i> Mode: Acak'
            : '<i class="fa-solid fa-list-ol"></i> Mode: Berurutan';

    questions = await eel.get_questions(room.roomCode)();
    document.getElementById("listCountBadge").textContent = `${questions.length} Soal`;

    renderAnswers();
    renderList();

    document.getElementById("questionForm").addEventListener("submit", handleSubmit);
});

function renderAnswers() {
    const type = document.getElementById("qType").value;
    const container = document.getElementById("answerSection");
    let html = "";

    if (type === "pg") {
        ["A", "B", "C", "D"].forEach((opt, idx) => {
            html += `
                <label class="answer-row">
                    <input type="radio" name="correct_pg" class="correct-check" value="${opt}" ${idx === 0 ? "checked" : ""}>
                    <div class="option-marker">${opt}</div>
                    <input type="text" class="option-input" id="opt_pg_${opt}" placeholder="Jawaban ${opt}" required>
                </label>
            `;
        });
    }

    if (type === "cb") {
        for (let i = 1; i <= 4; i++) {
            html += `
                <label class="answer-row">
                    <input type="checkbox" name="correct_cb" class="correct-check" value="${i}">
                    <div class="option-marker"><i class="fa-solid fa-check"></i></div>
                    <input type="text" class="option-input" id="opt_cb_${i}" placeholder="Opsi ${i}">
                </label>
            `;
        }
    }

    if (type === "tf") {
        html = `
        <div class="tf-container">
            <label class="tf-option">
                <input type="radio" name="correct_tf" class="tf-radio" value="true" checked>
                BENAR
            </label>
            <label class="tf-option">
                <input type="radio" name="correct_tf" class="tf-radio" value="false">
                SALAH
            </label>
        </div>`;
    }

    container.innerHTML = html;
}


async function handleSubmit(e) {
    e.preventDefault();

    if (questions.length >= MAX_QUESTIONS) {
        return alert("Jumlah soal sudah maksimal!");
    }

    const text = document.getElementById("qText").value.trim();
    const score = parseInt(document.getElementById("qScore").value);
    const type = document.getElementById("qType").value;

    let options = [];
    let correct = [];

    if (type === "pg") {
        ["A", "B", "C", "D"].forEach(opt => {
            const val = document.getElementById(`opt_pg_${opt}`).value.trim();
            options.push({ id: opt, text: val });
        });
        correct.push(document.querySelector('input[name="correct_pg"]:checked').value);
    }

    if (type === "cb") {
        for (let i = 1; i <= 4; i++) {
            const val = document.getElementById(`opt_cb_${i}`).value.trim();
            if (val) options.push({ id: i, text: val });
        }
        document.querySelectorAll('input[name="correct_cb"]:checked')
            .forEach(c => correct.push(c.value));
    }

    if (type === "tf") {
        options = [
            { id: "true", text: "Benar" },
            { id: "false", text: "Salah" }
        ];
        correct.push(document.querySelector('input[name="correct_tf"]:checked').value);
    }

    const saved = await eel.add_question(
        room.roomCode,
        text,
        type,
        score,
        JSON.stringify(options),
        JSON.stringify(correct)
    )();

    if (!saved.success) return alert(saved.message);

    alert("Soal berhasil ditambahkan!");
    location.reload();
}


async function renderList() {
    const list = document.getElementById("questionsList");
    const badge = document.getElementById("listCountBadge");
    const empty = document.getElementById("emptyState");

    questions = await eel.get_questions(room.roomCode)();

    if (!questions.length) {
        empty.style.display = "block";
        list.innerHTML = "";
        list.appendChild(empty);
        badge.textContent = "0 Soal";
        return;
    }

    empty.style.display = "none";
    list.innerHTML = "";
    questions.forEach((q, i) => {
        const label = q.qType === "pg" ? "MCQ" : q.qType === "cb" ? "Checkbox" : "T/F";
        const el = document.createElement("div");
        el.className = "q-item";
        el.innerHTML = `
            <div class="q-number">${i + 1}</div>
            <div class="q-content">
                <div class="q-text">${q.qText}</div>
                <div class="q-badges">
                    <span class="badge badge-type">${label}</span>
                    <span class="badge badge-score">${q.qScore} Poin</span>
                </div>
            </div>
            <div class="q-actions">
                <button class="btn-icon delete" onclick="del(${q.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>`;
        list.appendChild(el);
    });


    badge.textContent = `${questions.length} Soal`;
}

async function del(id) {
    if (!confirm("Hapus soal ini?")) return;
    await eel.delete_question(id)();
    alert("Soal dihapus");
    location.reload();
}



