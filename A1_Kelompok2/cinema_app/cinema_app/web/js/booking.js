document.addEventListener("DOMContentLoaded", () => {
  console.log("booking.js loaded");

  const params = new URLSearchParams(window.location.search);
  const filmId = parseInt(params.get("id"));
  let movieTitle = params.get("title");

  const dateContainer = document.getElementById("dateContainer");
  const timeContainer = document.getElementById("timeContainer");

  let schedules = [];
  let selectedDate = null;
  let selectedScheduleId = null;

  if (isNaN(filmId)) {
    console.error("Film ID tidak valid! URL harus menyertakan id.");
    dateContainer.innerHTML = "<p style='color:red'>Film ID tidak valid. Periksa URL!</p>";
    return;
  }

  // ----------------------------
  // 1. LOAD FILM INFO
  // ----------------------------
  if (typeof eel !== "undefined") {
    eel.get_movies()(function (movies) {
      const film = movies.find((m) => parseInt(m.id) === filmId);
      if (!film) return;

      movieTitle = film.title;
      document.getElementById("posterImage").src = "images/" + film.poster;
      document.querySelector(".movie-title").textContent = film.title;
      document.querySelector(".duration-text").textContent = film.duration + " menit";
      document.getElementById("metaInfo").innerHTML = `<span>Durasi: ${film.duration} menit</span>`;
    });
  }

  // ----------------------------
  // 2. LOAD JADWAL DARI DATABASE
  // ----------------------------
  if (typeof eel !== "undefined") {
    eel.get_schedule(filmId)(function (data) {
      if (!data || data.length === 0) {
        console.warn("Tidak ada jadwal ditemukan. Gunakan dummy data untuk testing.");
        schedules = [
          { id: 1, movie_id: filmId, show_time: "2025-12-01 17:00:00" },
          { id: 2, movie_id: filmId, show_time: "2025-12-02 19:00:00" },
        ];
      } else {
        schedules = data.map((s) => ({
          ...s,
          show_time: typeof s.show_time === "string" ? s.show_time : formatDateTime(s.show_time),
        }));
      }

      populateDates();
    });
  }

  // ----------------------------
  // FUNGSI MEMBUAT TOMBOL TANGGAL
  // ----------------------------
  function populateDates() {
    dateContainer.innerHTML = "";
    const validSchedules = schedules.filter((s) => s.show_time); // hanya yang ada show_time
    const uniqueDates = [...new Set(validSchedules.map((s) => s.show_time.split(" ")[0]))];

    uniqueDates.forEach((date) => {
      const btn = document.createElement("button");
      btn.className = "date-button";
      btn.dataset.date = date;
      btn.innerHTML = `
        <span class="date-number">${date.split("-")[2]}</span>  
        <span class="date-day">${getHari(date)}</span>
      `;
      btn.addEventListener("click", () => selectDate(date));
      dateContainer.appendChild(btn);
    });
  }

  // ----------------------------
  // pilih tanggal & buat tombol jam
  // ----------------------------
  function selectDate(date) {
    selectedDate = date;
    selectedScheduleId = null;

    document.querySelectorAll(".date-button").forEach((btn) => btn.classList.remove("active"));
    document.querySelector(`.date-button[data-date="${date}"]`).classList.add("active");

    const schedulesForDate = schedules.filter((s) => s.show_time && s.show_time.startsWith(date));

    timeContainer.innerHTML = "";

    schedulesForDate.forEach((s) => {
      const time = s.show_time.split(" ")[1].slice(0, 5);
      const btn = document.createElement("button");
      btn.className = "time-button";
      btn.dataset.time = time;
      btn.dataset.scheduleId = s.id; // <- simpan schedule_id di tombol
      btn.textContent = time;

      btn.addEventListener("click", () => {
        selectedScheduleId = s.id;
        document.querySelectorAll(".time-button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });

      timeContainer.appendChild(btn);
    });
  }

  // ----------------------------
  // tombol lanjut
  // ----------------------------
  document.querySelector(".continue-button").addEventListener("click", () => {
    if (!selectedDate || !selectedScheduleId) {
      alert("Pilih tanggal dan jam terlebih dahulu.");
      return;
    }

    const matched = schedules.find((s) => s.id === selectedScheduleId);

    if (!matched) {
      alert("Jadwal tidak ditemukan di database!");
      return;
    }

    localStorage.setItem("selectedScheduleId", matched.id);
    localStorage.setItem(
      "selectedSchedule",
      JSON.stringify({
        filmId,
        filmTitle: movieTitle,
        tanggal: selectedDate,
        jam: matched.show_time.split(" ")[1].slice(0, 5),
        scheduleId: matched.id,
      })
    );

    window.location.href = "seat.html";
  });

  // ----------------------------
  // UTIL
  // ----------------------------
  function getHari(dateString) {
    const hari = ["MINGGU", "SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"];
    const d = new Date(dateString);
    return hari[d.getDay()];
  }

  function formatDateTime(dt) {
    if (dt instanceof Date) {
      const y = dt.getFullYear();
      const m = String(dt.getMonth() + 1).padStart(2, "0");
      const d = String(dt.getDate()).padStart(2, "0");
      const h = String(dt.getHours()).padStart(2, "0");
      const min = String(dt.getMinutes()).padStart(2, "0");
      const s = String(dt.getSeconds()).padStart(2, "0");
      return `${y}-${m}-${d} ${h}:${min}:${s}`;
    }
    return dt;
  }
});
