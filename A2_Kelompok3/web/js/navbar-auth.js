async function updateNavbarSession() {
    const navRight = document.getElementById('nav-right');
    const user = await eel.get_current_user(SESSION_ID)();
    console.log("User from session:", user);

    if (user) {
        const name = user.username || user.name || user.fullname || user.email || "User";
        navRight.innerHTML = `
            <div class="user-info">
                👤 ${name}
                <button class="nav-logout" onclick="logout()">Logout</button>
            </div>
        `;
    }
}
