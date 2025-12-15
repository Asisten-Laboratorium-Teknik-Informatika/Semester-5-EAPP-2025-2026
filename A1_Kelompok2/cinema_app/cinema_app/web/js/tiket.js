document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const bookingCode = params.get("code");

  if (!bookingCode) {
    document.body.innerHTML = "<h2>Kode tiket tidak ditemukan!</h2>";
    return;
  }

  eel.get_ticket_details(bookingCode)((ticket) => {
    console.log("Ticket detail data:", ticket);

    if (ticket.error) {
      document.getElementById("ticketContainer").innerHTML = `<p>${ticket.error}</p>`;
      return;
    }

    // DATA DARI PYTHON (main.py)
    document.getElementById("judulFilm").textContent = ticket.title || "-";
    document.getElementById("hariTayang").textContent = ticket.day || "-";

    // Waktu = show_time
    document.getElementById("jamTayang").textContent = ticket.show_time || "-";

    // seats_list sudah diproses di Python
    document.getElementById("kursi").textContent = ticket.seats_list.join(", ") || "-";

    // TOTAL HARGA — gunakan 'total' yang dikirim Python
    const total = Number(ticket.total || 0);
    document.getElementById("totalHarga").textContent = "Rp " + total.toLocaleString("id-ID");

    document.getElementById("bookingCode").textContent = bookingCode;

    // ======================================
    // ✅ KODE BARU UNTUK MENGAKTIFKAN DOWNLOAD PDF
    // ======================================

    // 1. Definisikan path file PDF yang dibuat oleh main.py
    const pdfFileName = `${bookingCode}.pdf`;
    const pdfPath = `reports/${pdfFileName}`;

    // 2. Dapatkan elemen link dari HTML
    const downloadLink = document.getElementById("downloadLink");

    if (downloadLink) {
      // 3. Set atribut href ke path file PDF
      downloadLink.href = pdfPath;

      // 4. Tampilkan link (mengganti display: none)
      downloadLink.style.display = "block";
    } else {
      console.error("Elemen downloadLink tidak ditemukan di HTML. Pastikan ID-nya benar.");
    }
  });
});
