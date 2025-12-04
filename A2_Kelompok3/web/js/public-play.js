let room = null;
let participant = null;
let questions = [];
let currentIndex = 0;
let scoreTotal = 0;
let timeLeft = 30;
let timerInterval = null;
let isAnswered = false;

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const roomCode = params.get("room");

    participant = JSON.parse(localStorage.getItem("kilas_participant"));
    if (!participant) return (window.location.href = "join.html");

    room = await eel.get_room_data(roomCode)();
    if (!room) return (window.location.href = "join.html");

    questions = await eel.get_questions(roomCode)() || [];
    if (!questions.length) return alert("Belum ada soal!");

    loadQuestion();
    startTimer();
});

function loadQuestion() {
    if (!questions[currentIndex]) return endQuiz();

    const q = questions[currentIndex];
    const options = JSON.parse(q.options);
    const correctList = JSON.parse(q.correct);

    document.querySelector(".badge").innerText = `Soal ${currentIndex + 1} dari ${questions.length}`;
    document.querySelectorAll(".badge")[1].innerText = `Poin: ${q.qScore}`;
    document.querySelector(".q-text").innerText = q.qText;

    const grid = document.getElementById("answersGrid");
    grid.innerHTML = "";
    isAnswered = false;
    timeLeft = 30;
    document.getElementById("timer").classList.remove("danger");
    document.getElementById("footerStatus").classList.remove("visible");

    options.forEach((opt, i) => {
        const btn = document.createElement("button");
        btn.className = "answer-card opt-" + ["a", "b", "c", "d"][i];
        btn.innerText = opt.text;
        btn.onclick = () => submitAnswer(opt.id, correctList, btn);
        grid.appendChild(btn);
    });
}

function submitAnswer(selectedId, correctList, btn) {
    if (isAnswered) return;
    isAnswered = true;

    btn.classList.add("selected");

    const score = parseInt(questions[currentIndex].qScore) || 0;
    scoreTotal = Number(scoreTotal) || 0;

    if (correctList.includes(selectedId)) {
        scoreTotal += score;
    }

    document.getElementById("footerStatus").classList.add("visible");
}

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        document.getElementById("timer").innerText = timeLeft;

        if (timeLeft <= 10) document.getElementById("timer").classList.add("danger");
        if (timeLeft <= 0) nextQuestion();
    }, 1000);
}

function nextQuestion() {
    clearInterval(timerInterval);
    currentIndex++;

    if (currentIndex < questions.length) {
        loadQuestion();
        startTimer();
    } else endQuiz();
}

function endQuiz() {
    clearInterval(timerInterval);

   
    const finalScore = Number(scoreTotal) || 0;
    const totalQuestions = Number(questions.length) || 0;

    window.location.href = `result-user.html?score=${finalScore}&total=${totalQuestions}&room=${room.roomCode}`;
}
