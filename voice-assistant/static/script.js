
const toggleMicButton = document.getElementById('toggle-mic');
const statusElement = document.getElementById('status');

let websocket;
let mediaRecorder;
let isRecording = false;

const setupWebSocket = () => {
    websocket = new WebSocket("ws://localhost:8000/ws");

    websocket.onopen = () => {
        console.log("WebSocket connection established");
        statusElement.textContent = "Connected";
    };

    websocket.onmessage = (event) => {
        console.log("Message from server: ", event.data);
        const transcriptElement = document.getElementById('transcript');
        transcriptElement.textContent += event.data + ' ';
    };

    websocket.onclose = () => {
        console.log("WebSocket connection closed");
        statusElement.textContent = "Disconnected";
    };

    websocket.onerror = (error) => {
        console.error("WebSocket error: ", error);
        statusElement.textContent = "Connection Error";
    };
};

toggleMicButton.addEventListener('click', () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            mediaRecorder.start(1000); // Slice the stream into 1-second chunks

            mediaRecorder.ondataavailable = (event) => {
                if (websocket.readyState === WebSocket.OPEN) {
                    const reader = new FileReader();
                    reader.readAsDataURL(event.data); 
                    reader.onloadend = function() {
                        const base64data = reader.result;                
                        websocket.send(JSON.stringify({type: 'audio', data: base64data}));
                    }
                }
            };

            isRecording = true;
            toggleMicButton.textContent = 'Stop Microphone';
            statusElement.textContent = 'Recording...';
            if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                setupWebSocket();
            }
        })
        .catch(err => console.error('Error getting user media:', err));
};

const stopRecording = () => {
    mediaRecorder.stop();
    isRecording = false;
    toggleMicButton.textContent = 'Start Microphone';
    statusElement.textContent = 'Idle';
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({type: 'stop'}));
    }
};

// Initial state
statusElement.textContent = 'Idle';
