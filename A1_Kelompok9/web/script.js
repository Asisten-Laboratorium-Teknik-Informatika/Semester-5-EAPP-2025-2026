const questions = [
  // Menggabungkan semua kategori secara acak, positif & negatif
  { id: 1, category: "Neuroticism", dimension: "N", text: "Saya merasa gelisah atau khawatir lebih sering daripada orang lain." },
  { id: 2, category: "Openness", dimension: "O", text: "Saya tertarik mempelajari ide atau konsep yang abstrak." },
  { id: 3, category: "Agreeableness", dimension: "A", text: "Saya cenderung memperhatikan kebutuhan orang lain sebelum kebutuhan sendiri." },
  { id: 4, category: "Extraversion", dimension: "E", text: "Saya merasa termotivasi saat berinteraksi dengan banyak orang." },
  { id: 5, category: "Conscientiousness", dimension: "C", text: "Saya jarang menunda tugas yang penting." },
  
  { id: 6, category: "Neuroticism", dimension: "N", text: "Saya mudah merasa tersinggung atau frustrasi." },
  { id: 7, category: "Openness", dimension: "O", text: "Saya sering mencoba hal-hal baru, bahkan yang sedikit menantang." },
  { id: 8, category: "Agreeableness", dimension: "A", text: "Saya jarang merasa perlu bersaing dengan orang lain." },
  { id: 9, category: "Extraversion", dimension: "E", text: "Saya menikmati menjadi pusat perhatian di acara sosial." },
  { id: 10, category: "Conscientiousness", dimension: "C", text: "Saya selalu memastikan pekerjaan saya rapi dan teratur." },
  
  { id: 11, category: "Neuroticism", dimension: "N", text: "Saya sering merasa cemas tanpa alasan yang jelas." },
  { id: 12, category: "Openness", dimension: "O", text: "Saya menikmati seni, musik, atau budaya berbeda." },
  { id: 13, category: "Agreeableness", dimension: "A", text: "Saya mudah memaafkan kesalahan orang lain." },
  { id: 14, category: "Extraversion", dimension: "E", text: "Saya lebih suka bekerja dalam kelompok daripada sendirian." },
  { id: 15, category: "Conscientiousness", dimension: "C", text: "Saya membuat rencana sebelum melakukan sesuatu." },
  
  { id: 16, category: "Neuroticism", dimension: "N", text: "Saya sering meragukan keputusan yang saya buat." },
  { id: 17, category: "Openness", dimension: "O", text: "Saya cepat bosan dengan rutinitas yang monoton." },
  { id: 18, category: "Agreeableness", dimension: "A", text: "Saya senang membantu orang lain tanpa mengharapkan imbalan." },
  { id: 19, category: "Extraversion", dimension: "E", text: "Saya merasa energik saat menghadiri pertemuan sosial." },
  { id: 20, category: "Conscientiousness", dimension: "C", text: "Saya disiplin dalam menjalankan tanggung jawab sehari-hari." },
  
  { id: 21, category: "Neuroticism", dimension: "N", text: "Saya mudah merasa sedih atau kecewa." },
  { id: 22, category: "Openness", dimension: "O", text: "Saya sering memikirkan konsep baru atau ide abstrak." },
  { id: 23, category: "Agreeableness", dimension: "A", text: "Saya biasanya mempercayai niat baik orang lain." },
  { id: 24, category: "Extraversion", dimension: "E", text: "Saya merasa nyaman berbicara dengan orang yang baru saya temui." },
  { id: 25, category: "Conscientiousness", dimension: "C", text: "Saya selalu berusaha menyelesaikan tugas sesuai standar tinggi." },
];


const QUESTIONS_PER_PAGE = 5
let currentPage = 0
let answers = {}

let userData = {}

const traitDescriptions = {
  O: {
    name: "Openness",
    fullName: "Keterbukaan terhadap Pengalaman",
    low: "Anda cenderung lebih praktis dan konvensional, menyukai rutinitas dan hal-hal yang sudah familiar.",
    medium:
      "Anda memiliki keseimbangan antara kreativitas dan praktikalitas, terbuka pada ide baru namun tetap menghargai tradisi.",
    high: "Anda sangat kreatif, imajinatif, dan terbuka pada pengalaman baru. Anda menikmati seni, ide-ide abstrak, dan petualangan.",
  },
  C: {
    name: "Conscientiousness",
    fullName: "Kesadaran/Kedisiplinan",
    low: "Anda cenderung lebih fleksibel dan spontan, namun mungkin perlu meningkatkan fokus dan organisasi.",
    medium: "Anda memiliki keseimbangan antara disiplin dan fleksibilitas, dapat mengatur waktu dengan baik.",
    high: "Anda sangat terorganisir, disiplin, dan bertanggung jawab. Anda adalah perencana yang handal dan dapat diandalkan.",
  },
  E: {
    name: "Extraversion",
    fullName: "Ekstraversi",
    low: "Anda cenderung lebih introvert, menikmati waktu sendiri dan refleksi. Anda selektif dalam bersosialisasi.",
    medium: "Anda memiliki keseimbangan antara waktu sosial dan waktu pribadi, nyaman dalam berbagai situasi.",
    high: "Anda sangat energik dan sosial, menikmati interaksi dengan banyak orang dan situasi sosial yang ramai.",
  },
  A: {
    name: "Agreeableness",
    fullName: "Keramahan",
    low: "Anda cenderung lebih kompetitif dan skeptis, tidak mudah percaya dan lebih mementingkan kepentingan sendiri.",
    medium: "Anda memiliki keseimbangan antara kooperatif dan asertif, dapat bekerja sama namun tetap tegas.",
    high: "Anda sangat kooperatif, empatik, dan mudah percaya. Anda mementingkan harmoni dan kesejahteraan orang lain.",
  },
  N: {
    name: "Neuroticism",
    fullName: "Neurotisisme/Stabilitas Emosi",
    low: "Anda sangat stabil secara emosional, tenang, dan jarang merasa cemas atau tertekan.",
    medium: "Anda memiliki stabilitas emosional yang cukup baik, dapat mengelola stres dengan wajar.",
    high: "Anda cenderung lebih sensitif terhadap stres dan emosi negatif. Pertimbangkan teknik manajemen stres.",
  },
}

function startTest() {
  document.getElementById("home-screen").classList.remove("active")
  document.getElementById("guidelines-screen").classList.add("active")
}

function startActualTest() {
  document.getElementById("guidelines-screen").classList.remove("active")
  document.getElementById("test-screen").classList.add("active")
  currentPage = 0
  answers = {}
  renderPage()
}

function goToLanding() {
  document.getElementById("test-screen").classList.remove("active")
  document.getElementById("guidelines-screen").classList.remove("active")
  document.getElementById("home-screen").classList.add("active")
}

function renderPage() {
  const totalPages = Math.ceil(questions.length / QUESTIONS_PER_PAGE)
  const startIdx = currentPage * QUESTIONS_PER_PAGE
  const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length)
  const pageQuestions = questions.slice(startIdx, endIdx)

  const answeredCount = Object.keys(answers).length
  const percent = Math.round((answeredCount / questions.length) * 100)
  document.getElementById("progress-percent").textContent = `${percent} %`
  document.getElementById("step-indicator").textContent = `Step ${currentPage + 1} of ${totalPages}`

  const container = document.getElementById("questions-list")
  container.innerHTML = pageQuestions
    .map(
      (q, idx) => `
    <div class="question-card" data-question-id="${q.id}">
      <p class="question-card-text">${q.text}</p>
      <div class="radio-options">
        ${[1, 2, 3, 4, 5]
          .map(
            (value) => `
          <label class="radio-option">
            <input type="radio" name="q${q.id}" value="${value}" 
              ${answers[q.id] === value ? "checked" : ""} 
              onchange="selectAnswer(${q.id}, ${value})">
            <div class="radio-circle color-${value}">
              <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20,6 9,17 4,12" />
              </svg>
            </div>
          </label>
        `,
          )
          .join("")}
      </div>
    </div>
  `,
    )
    .join("")

  updateNextButton()
}

function selectAnswer(questionId, value) {
  answers[questionId] = value
  updateNextButton()
}

function updateNextButton() {
  const startIdx = currentPage * QUESTIONS_PER_PAGE
  const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length)
  const pageQuestions = questions.slice(startIdx, endIdx)

  const allAnswered = pageQuestions.every((q) => answers[q.id] !== undefined)
  document.getElementById("btn-next-page").disabled = !allAnswered

  // Update progress percentage
  const answeredCount = Object.keys(answers).length
  const percent = Math.round((answeredCount / questions.length) * 100)
  document.getElementById("progress-percent").textContent = `${percent} %`
}

function nextPage() {
  const totalPages = Math.ceil(questions.length / QUESTIONS_PER_PAGE)

  if (currentPage < totalPages - 1) {
    currentPage++
    renderPage()
    window.scrollTo(0, 0)
  } else {
    showUserForm()
  }
}

function showUserForm() {
  document.getElementById("test-screen").classList.remove("active")
  document.getElementById("user-form-screen").classList.add("active")
  window.scrollTo(0, 0)
}

function submitUserForm(event) {
  event.preventDefault()

  userData = {
    name: document.getElementById("user-name").value,
    dob: document.getElementById("user-dob").value,
    gender: document.getElementById("user-gender").value,
    education: document.getElementById("user-education").value,
    occupation: document.getElementById("user-occupation").value,
    email: document.getElementById("user-email").value,
    testDate: new Date().toLocaleDateString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }),
  }

  if (userData.dob) {
    const birthDate = new Date(userData.dob)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    userData.age = age
  }

  finishTest()
}

function finishTest() {
  const scores = calculateScores()
  const maxScorePerDimension = getMaxScorePerDimension()

  document.getElementById("user-form-screen").classList.remove("active")
  document.getElementById("results-screen").classList.add("active")
  window.scrollTo(0, 0)

  if (userData.name) {
    document.getElementById("results-user-name").innerHTML =
      `Hasil untuk <strong>${userData.name}</strong> - Model Big Five Personality (OCEAN)`
  }

  renderUserSummary()
  renderCharts(scores, maxScorePerDimension)
  renderDetailedResults(scores, maxScorePerDimension)
  renderInterpretations(scores, maxScorePerDimension)
}

function getMaxScorePerDimension() {
  const counts = { O: 0, C: 0, E: 0, A: 0, N: 0 }
  questions.forEach((q) => {
    counts[q.dimension]++
  })
  return {
    O: counts.O * 5,
    C: counts.C * 5,
    E: counts.E * 5,
    A: counts.A * 5,
    N: counts.N * 5,
  }
}

function renderUserSummary() {
  const container = document.getElementById("results-user-summary")

  const genderMap = { male: "Laki-laki", female: "Perempuan", other: "Lainnya" }
  const educationMap = {
    sd: "SD",
    smp: "SMP",
    sma: "SMA/SMK",
    diploma: "Diploma",
    s1: "S1",
    s2: "S2",
    s3: "S3",
  }

  const occupationMap = {
    student: "Pelajar/Mahasiswa",
    employee: "Karyawan",
    entrepreneur: "Wirausaha",
    professional: "Profesional",
    freelancer: "Freelancer",
    unemployed: "Belum Bekerja",
    retired: "Pensiunan",
    other: "Lainnya",
  }

  let summaryHTML = ""

  if (userData.age) {
    summaryHTML += `
      <div class="user-summary-item">
        <span class="user-summary-label">Usia</span>
        <span class="user-summary-value">${userData.age} tahun</span>
      </div>
    `
  }

  if (userData.gender) {
    summaryHTML += `
      <div class="user-summary-item">
        <span class="user-summary-label">Jenis Kelamin</span>
        <span class="user-summary-value">${genderMap[userData.gender] || userData.gender}</span>
      </div>
    `
  }

  if (userData.education) {
    summaryHTML += `
      <div class="user-summary-item">
        <span class="user-summary-label">Pendidikan</span>
        <span class="user-summary-value">${educationMap[userData.education] || userData.education}</span>
      </div>
    `
  }

  if (userData.occupation) {
    summaryHTML += `
      <div class="user-summary-item">
        <span class="user-summary-label">Pekerjaan</span>
        <span class="user-summary-value">${occupationMap[userData.occupation] || userData.occupation}</span>
      </div>
    `
  }

  summaryHTML += `
    <div class="user-summary-item">
      <span class="user-summary-label">Tanggal Tes</span>
      <span class="user-summary-value">${userData.testDate}</span>
    </div>
  `

  container.innerHTML = summaryHTML
}

function renderCharts(scores, maxScores) {
  // Calculate percentages
  const percentages = {
    O: Math.round((scores.O / maxScores.O) * 100),
    C: Math.round((scores.C / maxScores.C) * 100),
    E: Math.round((scores.E / maxScores.E) * 100),
    A: Math.round((scores.A / maxScores.A) * 100),
    N: Math.round((scores.N / maxScores.N) * 100),
  }

  const labels = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
  const data = [percentages.O, percentages.C, percentages.E, percentages.A, percentages.N]
  const colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336"]

  // Radar Chart
  const radarCtx = document.getElementById("radarChart").getContext("2d")
  new window.Chart(radarCtx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Skor Anda",
          data: data,
          backgroundColor: "rgba(0, 133, 88, 0.2)",
          borderColor: "#008558",
          borderWidth: 2,
          pointBackgroundColor: "#008558",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#008558",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            font: { size: 10 },
          },
          pointLabels: {
            font: { size: 11, weight: "600" },
          },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  })

  // Bar Chart
  const barCtx = document.getElementById("barChart").getContext("2d")
  new window.Chart(barCtx, {
    type: "bar",
    data: {
      labels: ["O", "C", "E", "A", "N"],
      datasets: [
        {
          label: "Persentase",
          data: data,
          backgroundColor: colors,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: (value) => value + "%",
          },
        },
        x: {
          grid: { display: false },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `${context.parsed.y}%`,
          },
        },
      },
    },
  })
}

function renderDetailedResults(scores, maxScores) {
  const container = document.getElementById("results-details")
  const dimensions = ["O", "C", "E", "A", "N"]

  container.innerHTML = dimensions
    .map((dim) => {
      const score = scores[dim]
      const maxScore = maxScores[dim]
      const percentage = Math.round((score / maxScore) * 100)
      const trait = traitDescriptions[dim]

      let level, levelClass
      if (percentage < 40) {
        level = "Rendah"
        levelClass = "level-low"
      } else if (percentage < 70) {
        level = "Sedang"
        levelClass = "level-medium"
      } else {
        level = "Tinggi"
        levelClass = "level-high"
      }

      return `
      <div class="result-detail-card">
        <div class="result-detail-header">
          <div class="result-detail-icon">${dim}</div>
          <div class="result-detail-score">${percentage}%</div>
        </div>
        <div class="result-detail-name">${trait.fullName}</div>
        <div class="result-detail-bar">
          <div class="result-detail-bar-fill" style="width: ${percentage}%"></div>
        </div>
        <div class="result-detail-desc">Skor: ${score} dari ${maxScore} poin</div>
        <span class="result-detail-level ${levelClass}">${level}</span>
      </div>
    `
    })
    .join("")
}

function renderInterpretations(scores, maxScores) {
  const container = document.getElementById("results-interpretations")
  const dimensions = ["O", "C", "E", "A", "N"]

  let html = '<h3 class="interpretations-title">Interpretasi Hasil Anda</h3>'

  html += dimensions
    .map((dim) => {
      const score = scores[dim]
      const maxScore = maxScores[dim]
      const percentage = Math.round((score / maxScore) * 100)
      const trait = traitDescriptions[dim]

      let interpretation
      if (percentage < 40) {
        interpretation = trait.low
      } else if (percentage < 70) {
        interpretation = trait.medium
      } else {
        interpretation = trait.high
      }

      return `
      <div class="interpretation-card">
        <div class="interpretation-header">
          <div class="interpretation-icon">${dim}</div>
          <div class="interpretation-name">${trait.name} (${percentage}%)</div>
        </div>
        <p class="interpretation-text">${interpretation}</p>
      </div>
    `
    })
    .join("")

  container.innerHTML = html
}

function retakeTest() {
  currentPage = 0
  answers = {}
  userData = {}

  // Reset form
  document.getElementById("user-info-form").reset()

  document.getElementById("results-screen").classList.remove("active")
  document.getElementById("home-screen").classList.add("active")
}

function calculateScores() {
  const scores = { O: 0, C: 0, E: 0, A: 0, N: 0 }

  questions.forEach((q) => {
    const value = answers[q.id] || 0
    scores[q.dimension] += value
  })

  return scores
}

function downloadResults() {
  const scores = calculateScores()
  const maxScores = getMaxScorePerDimension()

  let content = `HASIL TES KEPRIBADIAN BIG FIVE (OCEAN)\n`
  content += `==========================================\n\n`
  content += `Nama: ${userData.name || "-"}\n`
  content += `Tanggal Tes: ${userData.testDate || "-"}\n`
  content += `Usia: ${userData.age || "-"} tahun\n\n`
  content += `SKOR DIMENSI:\n`
  content += `------------------------------------------\n`

  const dimensions = ["O", "C", "E", "A", "N"]
  dimensions.forEach((dim) => {
    const percentage = Math.round((scores[dim] / maxScores[dim]) * 100)
    content += `${traitDescriptions[dim].fullName}: ${percentage}%\n`
  })

  content += `\n==========================================\n`
  content += `Terima kasih telah mengikuti tes ini!`

  const blob = new Blob([content], { type: "text/plain" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `hasil-tes-ocean-${userData.name || "user"}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

async function submitUserForm(event) {
  event.preventDefault();

  // Ambil data dari form
  const user = {
    name: document.getElementById("user-name").value,
    dob: document.getElementById("user-dob").value,
    gender: document.getElementById("user-gender").value,
    education: document.getElementById("user-education").value,
    occupation: document.getElementById("user-occupation").value,
    email: document.getElementById("user-email").value,
  };

  // Hitung umur
  if (user.dob) {
    const birthDate = new Date(user.dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
    user.age = age;
  }

  // Hitung skor Big Five
  const scores = calculateScores();
  const maxScores = getMaxScorePerDimension();

  const percentages = {
    O: Math.round((scores.O / maxScores.O) * 100),
    C: Math.round((scores.C / maxScores.C) * 100),
    E: Math.round((scores.E / maxScores.E) * 100),
    A: Math.round((scores.A / maxScores.A) * 100),
    N: Math.round((scores.N / maxScores.N) * 100),
  };

  // Gabungkan user + skor
  const payload = {
    ...user,
    ...percentages,
  };

  console.log("DATA DIKIRIM KE PYTHON:", payload);

  // Kirim ke Python
  let result = await eel.save_user(payload)();

  alert(result);

  // lanjut tampilkan halaman hasil
  finishTest();
}
