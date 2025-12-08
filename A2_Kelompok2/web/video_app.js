let localVideo = document.getElementById('localVideo');
let remoteVideo = document.getElementById('remoteVideo');
let remoteScreenVideo = document.getElementById('remoteScreenVideo');
let localScreen = document.getElementById('localScreen');

let joinBtn = document.getElementById('joinBtn');
let leaveBtn = document.getElementById('leaveBtn');
let shareScreenBtn = document.getElementById('shareScreenBtn');

let micToggleBtn = document.getElementById('micToggleBtn');
let cameraToggleBtn = document.getElementById('cameraToggleBtn');
let hangUpBtn = document.getElementById('hangUpBtn'); 

let pc = null;
let ws = null;
let roomId = null;
let localStream = null;
let screenStream = null;
let screenSender = null; 
let isScreenSharing = false;

const SIGNALING_SERVER_URL = "libratory-heike-manlier.ngrok-free.dev"; 
const USE_SECURE_WS = false;
const pcConfig = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" }
    ]
};

async function openMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error("Error accessing media devices:", error);
        throw new Error("Gagal mengakses kamera dan mikrofon. Periksa izin browser.");
    }
}

function createPeerConnection() {
    pc = new RTCPeerConnection(pcConfig);

    pc.onicecandidate = (event) => {
            if (event.candidate && ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'candidate',
                    room: roomId,
                    candidate: event.candidate
                }));
            }
    };

    pc.onnegotiationneeded = async () => {
            try {
                if (pc.signalingState !== 'stable') {
                    console.log('Skipping renegotiation: State is not stable:', pc.signalingState);
                    return;
                }
                console.log('Renegotiation needed, creating offer...');
                await createOffer(); 
            } catch (e) {
                console.warn('Error during negotiation:', e);
            }
    };

    pc.ontrack = (event) => {
        const stream = event.streams[0];
        const track = event.track;

        if (track.kind === 'video' && stream.getAudioTracks().length === 0) {
            remoteScreenVideo.srcObject = stream;
            remoteScreenVideo.style.display = 'block';
            
            track.onended = () => {
                remoteScreenVideo.srcObject = null;
                remoteScreenVideo.style.display = 'none';
            };
            
        } else if (track.kind === 'video' || track.kind === 'audio') {
            if (remoteVideo.srcObject !== stream) {
                remoteVideo.srcObject = stream;
            }
        }
    };

    localStream.getTracks().forEach(track => {
        pc.addTrack(track, localStream);
    });
}

function cleanupPeer() {
    if (pc) {
        pc.close();
        pc = null;
        screenSender = null;
    }
    if (localStream) {
        localStream.getTracks().forEach(track => { track.stop(); });
        localStream = null;
        localVideo.srcObject = null;
    }
    if (screenStream) {
        screenStream.getTracks().forEach(t => t.stop());
        screenStream = null;
        localScreen.srcObject = null;
    }
    if (ws && ws.readyState !== WebSocket.CLOSED) {
        ws.close();
        ws = null;
    }

    remoteVideo.srcObject = null;
    if (remoteScreenVideo) remoteScreenVideo.srcObject = null;

    isScreenSharing = false;
    shareScreenBtn.innerHTML = '<span class="material-icons">screen_share</span>';
}

function connectWebSocket() {
    if (ws && ws.readyState !== WebSocket.CLOSED && ws.readyState !== WebSocket.CLOSING) return;
    
    const protocol = USE_SECURE_WS ? "wss://" : "ws://";
    ws = new WebSocket(`${protocol}${SIGNALING_SERVER_URL}/ws`);

    ws.onopen = () => {
        console.log("WebSocket connected.");
        createPeerConnection(); 
        ws.send(JSON.stringify({ type: "join", room: roomId }));
    };

    ws.onmessage = async (evt) => {
        const data = JSON.parse(evt.data);

        if (!pc) return; 

        if (data.type === "new-peer") {
            setTimeout(createOffer, 100); 
        }

        else if (data.type === "offer") {
            await pc.setRemoteDescription(new RTCSessionDescription({type: data.type, sdp: data.sdp}));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            ws.send(JSON.stringify({ type: "answer", room: roomId, sdp: pc.localDescription.sdp }));
        }

        else if (data.type === "answer") {
            await pc.setRemoteDescription(new RTCSessionDescription({type: data.type, sdp: data.sdp}));
        }

        else if (data.type === "candidate") {
            try {
                await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
            } catch (err) {
                console.error("ICE error:", err);
            }
        }

        else if (data.type === "peer-left") {
            remoteVideo.srcObject = null;
            if (remoteScreenVideo) remoteScreenVideo.srcObject = null;
        }
    };
}

async function createOffer() {
    if (!pc || pc.signalingState === 'closed' || !ws || ws.readyState !== WebSocket.OPEN) return;
    
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    
    ws.send(JSON.stringify({
        type: "offer",
        room: roomId,
        sdp: pc.localDescription.sdp
    }));
}

async function createAnswer() {
    if (!pc || pc.signalingState === 'closed' || !ws || ws.readyState !== WebSocket.OPEN) return;
    
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    
    ws.send(JSON.stringify({
        type: "answer",
        room: roomId,
        sdp: pc.localDescription.sdp
    }));
}


function toggleMic() {
    if (!localStream) return;
    const audioTrack = localStream.getAudioTracks()[0];
    if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        const icon = micToggleBtn.querySelector('.material-icons');
        icon.textContent = audioTrack.enabled ? 'mic' : 'mic_off';
    }
}

function toggleVideo() {
    if (!localStream) return;
    const videoTrack = localStream.getVideoTracks()[0];
    if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        const icon = cameraToggleBtn.querySelector('.material-icons');
        icon.textContent = videoTrack.enabled ? 'videocam' : 'videocam_off';
    }
}


async function startScreenShare() {
    if (!pc || isScreenSharing) return;

    try {
        screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: true,
            audio: false 
        });

        const screenTrack = screenStream.getVideoTracks()[0];
        
        screenSender = pc.addTrack(screenTrack, screenStream);

        localScreen.srcObject = screenStream;
        localScreen.style.display = 'block';
        
        screenTrack.onended = stopScreenShare;

        isScreenSharing = true;
        shareScreenBtn.innerHTML = '<span class="material-icons">stop_screen_share</span>';

    } catch (err) {
        console.error("share screen failed:", err);
    }
}

async function stopScreenShare() {
    if (!pc || !isScreenSharing || !screenSender) return;

    pc.removeTrack(screenSender);
    screenSender = null;
    
    screenStream.getTracks().forEach(t => t.stop());
    screenStream = null;
    localScreen.srcObject = null;
    localScreen.style.display = 'none';

    isScreenSharing = false;
    shareScreenBtn.innerHTML = '<span class="material-icons">screen_share</span>';
}


micToggleBtn.addEventListener('click', toggleMic);
cameraToggleBtn.addEventListener('click', toggleVideo);

shareScreenBtn.addEventListener('click', () => {
    if (isScreenSharing) {
        stopScreenShare();
    } else {
        startScreenShare();
    }
});

hangUpBtn.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "leave", room: roomId }));
    }
    
    cleanupPeer();
    window.location.href = "./index.html";
});


(async () => {
    roomId = window.currentGroupName;
    await openMedia();
    connectWebSocket();
})();