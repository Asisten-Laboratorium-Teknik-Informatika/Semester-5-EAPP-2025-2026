document.addEventListener("DOMContentLoaded", async () => {
    const placeholder = document.getElementById("navbar-placeholder");

    const res = await fetch("navbar.html");
    const html = await res.text();
    placeholder.innerHTML = html;

    console.log("NAVBAR LOADED ✔");

    if (typeof eel !== "undefined") updateNavbarSession();
});
async function updateNavbarSession() {
    const navRight = document.getElementById("nav-right");
    if (!navRight) return;

    const user = await eel.get_current_user(SESSION_ID)();
    if (user) {
        navRight.innerHTML = `
    <span class="nav-username">
        <i class="fa-solid fa-user"></i>
        ${user.username}
    </span>
    <button class="nav-outline" onclick="logout()">Logout</button>
`;

    }
}


async function logout() {
    await eel.logout(SESSION_ID)();
    window.location.href = "../pages/index.html";
}
