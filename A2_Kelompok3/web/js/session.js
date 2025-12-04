// session.js
let SESSION_ID = sessionStorage.getItem("eel_session_id");
if (!SESSION_ID) {
    SESSION_ID = "sess_" + Date.now() + "_" + Math.floor(Math.random() * 100000);
    sessionStorage.setItem("eel_session_id", SESSION_ID);
}

async function eel_py(func_name, ...args) {
    return await eel[func_name](SESSION_ID, ...args)();
}


async function checkSession() {
    const user = await eel.get_current_user(SESSION_ID)();
    if (!user) {
        sessionStorage.removeItem("eel_user");
        sessionStorage.removeItem("eel_session_id");
        window.location.href = "/pages/auth/login.html";
    }
    return user;
}


async function logout() {
    await eel.logout(SESSION_ID)();
    sessionStorage.removeItem("eel_user");
    sessionStorage.removeItem("eel_session_id");
    window.location.href = "/pages/index.html";
}
