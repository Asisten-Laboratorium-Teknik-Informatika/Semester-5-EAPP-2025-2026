document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);

    const score = Number(params.get("score")) || 0;
    const total = Number(params.get("total")) || 0;
    const roomCode = params.get("room");

    const participant = JSON.parse(localStorage.getItem("kilas_participant"));
    if (!participant) return (window.location.href = "join.html");

    const room = await eel.get_room_data(roomCode)();
    if (!room) return alert("Room tidak ditemukan!");


    let correct = 0;
    let accuracy = 0;

    
    const maxTotalScore = Number(room.maxTotalScore) || null;

    if (maxTotalScore && maxTotalScore > 0) {
        
        accuracy = Math.round((score / maxTotalScore) * 100);
        if (accuracy < 0) accuracy = 0;
        if (accuracy > 100) accuracy = 100;

      
        correct = Math.round((accuracy / 100) * total);
    } else {
        
        accuracy = total > 0 ? Math.round((score / (total * 100)) * 100) : 0; 
        if (accuracy < 0 || isNaN(accuracy)) accuracy = 0;

        correct = Math.round((accuracy / 100) * total);
    }

    if (correct < 0) correct = 0;
    if (correct > total) correct = total;

    document.querySelector(".result-title").innerText = `Selamat, ${participant.name}!`;
    document.querySelector(".result-subtitle").innerText = `Kuis "${room.roomName}" telah selesai.`;

    document.querySelectorAll(".stat-val")[0].innerText = `${correct}/${total}`;  
    document.querySelectorAll(".stat-val")[1].innerText = score;                
    document.querySelectorAll(".stat-val")[2].innerText = `${accuracy}%`;      
});
