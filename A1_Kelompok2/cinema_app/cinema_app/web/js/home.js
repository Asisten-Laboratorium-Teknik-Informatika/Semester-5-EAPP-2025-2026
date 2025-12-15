// home.js — render daftar film ke #filmList
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("filmList");
  if (!container) {
    console.error("Container #filmList tidak ditemukan di DOM");
    return;
  }
  // fallback kecil kalau eel tidak tersedia (mis. buka file langsung)
  if (typeof eel === "undefined") {
    console.warn("eel tidak ditemukan — jalankan aplikasi lewat python main.py");
    // optional: tampilin placeholder statis
    container.innerHTML = '<p class="notice">Jalankan aplikasi lewat python main.py untuk melihat daftar film.</p>';
    return;
  }
  // ambil data film dari Python
  eel.get_movies()(function (movies) {
    console.log("movies from eel:", movies);
    if (!Array.isArray(movies) || movies.length === 0) {
      container.innerHTML = '<p class="notice">Belum ada film tersedia.</p>';
      return;
    }
    // bersihkan container
    container.innerHTML = "";
    movies.forEach((movie) => {
      const card = document.createElement("div");
      card.className = "film-card";
      // gunakan movie.id untuk navigasi (lebih aman daripada title)
      const posterPath = movie.poster ? `images/${movie.poster}` : "images/placeholder.jpg";
      card.innerHTML = `
        <a class="film-link" href="booking.html?id=${encodeURIComponent(movie.id)}" title="${escapeHtml(movie.title || "")}">
          <div class="film-poster"><img src="${posterPath}" alt="${escapeHtml(movie.title || "Poster")}" /></div>
          <div class="film-info">
            <h3 class="film-title">${escapeHtml(movie.title || "")}</h3>
            <p class="film-meta">${escapeHtml(movie.genre || "")} • ${escapeHtml(movie.duration || "")}</p>
          </div>
        </a>
      `;
      container.appendChild(card);
    });
  });
});
// small helper to avoid injection/invalid HTML from DB content
function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
