async function handleJoin(e) {
    e.preventDefault();

    const btn = document.querySelector(".btn-join");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Menghubungkan...';

    const code = document.getElementById("roomCode").value.trim();
    const name = document.getElementById("userName").value.trim();

    if (!code || !name) {
        alert("Semua field wajib diisi");
        btn.disabled = false;
        btn.innerHTML = `Gabung Sekarang <i class="fa-solid fa-arrow-right"></i>`;
        return;
    }

    // ambil data room
    const room = await eel.get_room_data(code)();
    console.log("ROOM:", room);
    if (!room) {
        alert("Kode room tidak ditemukan");
        btn.disabled = false;
        btn.innerHTML = `Gabung Sekarang <i class="fa-solid fa-arrow-right"></i>`;
        return;
    }

    // tambah peserta
    const status = await eel.add_participant(code, name)();
    console.log("STATUS PYTHON:", status);

    // 🔥 ini fix utama — tidak akan pernah alert undefined lagi
    if (!status || status.success !== true) {
        const msg = status?.message || "Gagal bergabung ke room";
        alert(msg);
        btn.disabled = false;
        btn.innerHTML = `Gabung Sekarang <i class="fa-solid fa-arrow-right"></i>`;
        return;
    }

    // simpan participant
    const participant = {
        name,
        roomCode: code,
        joinedAt: Date.now()
    };
    localStorage.setItem("kilas_participant", JSON.stringify(participant));

    alert("Berhasil bergabung!");
    window.location.href = `lobby.html?room=${code}`;
}
