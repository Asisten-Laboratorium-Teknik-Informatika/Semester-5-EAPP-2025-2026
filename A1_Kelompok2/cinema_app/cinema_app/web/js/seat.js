console.log("Seat page loaded");

// Seat template (tetap sama)
const seatsData = {
  A: ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10", "A11", "A12", "A13"],
  B: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10", "B11", "B12", "B13"],
  C: ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13"],
  D: ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11", "D12", "D13"],
};

let bookedSeats = [];
let selectedSeats = [];
const pricePerSeat = 42000;

// --------------------------------------------------
// LOAD BOOKED SEATS FROM DATABASE
// --------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
  const scheduleId = parseInt(localStorage.getItem("selectedScheduleId"));
  if (!scheduleId || isNaN(scheduleId)) {
    alert("Pilih jadwal dulu!");
    window.location.href = "booking.html";
    return;
  }

  console.log("Loading seats for schedule:", scheduleId);

  eel.get_seats(scheduleId)((seats) => {
    bookedSeats = seats
      .filter((s) => s.is_booked === 1 || s.is_booked === "1") // mysql bisa kirim string
      .map((s) => s.seat_number);

    console.log("Booked seats:", bookedSeats);

    initSeats();
  });
});

// --------------------------------------------------
// GENERATE SEAT GRID
// --------------------------------------------------
function initSeats() {
  const container = document.getElementById("seatsContainer");
  container.innerHTML = "";

  Object.entries(seatsData).forEach(([row, seats]) => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "seats-row";

    seats.forEach((seatId) => {
      const btn = document.createElement("button");
      btn.className = "seat";
      btn.textContent = seatId;

      if (bookedSeats.includes(seatId)) {
        btn.classList.add("booked");
        btn.disabled = true;
      }

      btn.onclick = () => toggleSeat(seatId, btn);
      rowDiv.appendChild(btn);
    });

    container.appendChild(rowDiv);
  });

  updateSummary();
}

// --------------------------------------------------
function toggleSeat(seatId, btn) {
  if (btn.classList.contains("booked")) return;

  const index = selectedSeats.indexOf(seatId);
  if (index >= 0) {
    selectedSeats.splice(index, 1);
    btn.classList.remove("selected");
  } else {
    selectedSeats.push(seatId);
    btn.classList.add("selected");
  }

  updateSummary();
}

function updateSummary() {
  document.getElementById("selectedSeatsDisplay").textContent = selectedSeats.length ? selectedSeats.join(", ") : "-";

  const total = selectedSeats.length * pricePerSeat;
  document.getElementById("totalPrice").textContent = "RP " + total.toLocaleString("id-ID");
}

// --------------------------------------------------
// SEND TO PYTHON
// --------------------------------------------------
function confirmBooking() {
  if (selectedSeats.length === 0) {
    alert("Pilih kursi dulu!");
    return;
  }

  const scheduleId = parseInt(localStorage.getItem("selectedScheduleId"));

  const bookingData = {
    seats: selectedSeats,
    total: selectedSeats.length * pricePerSeat,
    schedule_id: scheduleId,
  };

  console.log("Send booking:", bookingData);

  eel.save_booking(bookingData)((response) => {
    console.log("Response:", response);

    if (!response.success) {
      alert("Gagal booking: " + response.message);
      return;
    }

    alert("Berhasil! Kode: " + response.booking_code);

    // PERBAIKAN DI SINI
    window.location.href = `tiket.html?code=${response.booking_code}`;
  });
}
