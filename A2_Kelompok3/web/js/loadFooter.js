document.addEventListener("DOMContentLoaded", () => {
    const footer = document.getElementById("footer-placeholder");

    fetch("footer.html")
        .then(res => res.text())
        .then(html => footer.innerHTML = html)
        .catch(err => console.error("Footer gagal dimuat:", err));
});
