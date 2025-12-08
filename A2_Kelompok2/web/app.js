let currentUser = "";

function switchTab(mode) {
    document.getElementById("host-section").classList.toggle("hidden", mode !== "host");
    document.getElementById("join-section").classList.toggle("hidden", mode !== "join");

    document.getElementById("tab-host").classList.toggle("active", mode === "host");
    document.getElementById("tab-join").classList.toggle("active", mode === "join");

    if (mode === "join") {
        console.log("scann");
        document.getElementById('group-list').innerHTML =
            '<div id="no-groups-msg" class="no-items">Searching...<br><span class="hint">(Make sure Host is on same WiFi)</span></div>';
        eel.start_scanning();
    }
}

function showLogin() {
    document.getElementById("registerSection").style.display = "none";
    document.getElementById("loginSection").style.display = "block";
}

function showRegister() {
    document.getElementById("loginSection").style.display = "none";
    document.getElementById("registerSection").style.display = "block";
}

// --- AUTH ---
async function doLogin() {
    const u = document.getElementById('auth-user').value.trim();
    const p = document.getElementById('auth-pass').value.trim();
    if(!u || !p) return;
    const res = await eel.login_user(u, p)();
    if (res === true) {
        currentUser = u;
        document.getElementById('display-username').innerText = u;
        showSetup();
    } else {
        document.getElementById('auth-error').innerText = res;
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

async function doRegister() {
    const u = document.getElementById('auth-user').value.trim();
    const p = document.getElementById('auth-pass').value.trim();
    if(!u || !p) return;
    const res = await eel.register_user(u, p)();
    if (res === true) alert("Registered! Login now.");
    else {
        document.getElementById('auth-error').innerText = res;
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

function showSetup() {
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('setup-screen').classList.remove('hidden');
}

eel.expose(ui_add_group);
function ui_add_group(name, hostUser, ip, port) {
    const noMsg = document.getElementById('no-groups-msg');
    if (noMsg) noMsg.remove();

    const list = document.getElementById('group-list');
    if (document.getElementById(`btn-${ip}-${port}`)) return;

    const html = `
    <div id="btn-${ip}-${port}" class="group-card" 
        onclick="connectToGroup('${ip}', '${port}', '${name}')">
        
        <div class="group-info">
            <h3 class="group-name">${escapeHtml(name)}</h3>
            <p class="group-host">Host: ${escapeHtml(hostUser)}</p>
        </div>

        <div class="group-join">JOIN</div>
    </div>`;
    
    list.insertAdjacentHTML('beforeend', html);
}

async function startHosting() {
    const groupName = document.getElementById('group-name-input').value.trim();
    if (!groupName) return alert("Please enter a Group Name");

    document.getElementById('chat-title').innerText = groupName;
    const res = await eel.host_chat(groupName)();
    
    if (res === true) enterChat();
    else alert("Error hosting: " + res);
}

async function connectToGroup(ip, port, name) {
    document.getElementById('chat-title').innerText = name;
    const res = await eel.join_chat(ip, port)();
    if (res === true) enterChat();
    else alert("Connection failed: " + res);
}

function enterChat() {
    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('chat-screen').classList.remove('hidden');
    addMessage("System", "text", "", "Joined the chat.");

    window.currentGroupName = document.getElementById('chat-title').innerText;
}

function leaveChat() {
    location.reload();
}

// --- FILE & CHAT (Unchanged Logic) ---
function handleFileSelect(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        if(file.size > 5 * 1024 * 1024) { alert("File too large"); return; }
        reader.onload = function(e) {
            const base64Data = e.target.result;
            const type = file.type.startsWith('image/') ? 'image' : 'file';
            eel.send_data_py(type, file.name, base64Data, currentUser);
        };
        reader.readAsDataURL(file);
    }
    input.value = '';
}

eel.expose(js_receive_message);
function js_receive_message(sender, type, filename, content) {
    addMessage(sender, type, filename, content);
    if(sender !== currentUser && sender !== "System") {
        eel.trigger_notification(sender, type === 'text' ? content : "Sent a file");
    }
}

function sendMsg(e) {
    e.preventDefault();
    const input = document.getElementById('msg-input');
    const text = input.value.trim();
    if(!text) return;
    eel.send_data_py("text", "", text, currentUser);
    input.value = '';
}

function addMessage(sender, type, filename, content) {
    const container = document.getElementById('messages');
    const isMe = sender === currentUser;
    const isSys = sender === "System";

    let innerContent = "";

    if (type === 'image') {
        innerContent = `
            <p class="file-label">${escapeHtml(filename)}</p>
            <img src="${content}" class="img-preview" onclick="openImage(this.src)">
        `;
    } else if (type === 'file') {
        innerContent = `
            <div class="file-box">
                <i class="fa-solid fa-file file-icon"></i>
                <div class="file-info">
                    <p class="file-name">${escapeHtml(filename)}</p>
                    <a href="${content}" download="${filename}" class="file-download">Download</a>
                </div>
            </div>
        `;
    } else {
        innerContent = `<p class="msg-text">${escapeHtml(content)}</p>`;
    }

    let html = "";

    if (isSys) {
        html = `
            <div class="sys-msg">- ${escapeHtml(content)} -</div>
        `;
    } else if (isMe) {
        html = `
            <div class="msg-row right">
                <div class="msg-bubble msg-right fade-in">
                    ${innerContent}
                </div>
            </div>
        `;
    } else {
        html = `
            <div class="msg-row left fade-in">
                <div class="msg-bubble msg-left">
                    <p class="msg-sender">${escapeHtml(sender)}</p>
                    ${innerContent}
                </div>
            </div>
        `;
    }

    container.insertAdjacentHTML("beforeend", html);
    container.scrollTop = container.scrollHeight;
}

function openImage(src) {
    const w = window.open("");
    w.document.write('<img src="' + src + '" style="max-width:100%">');
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}