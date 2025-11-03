// LiveKit Voice Agent Web Client (uses UMD build loaded in index.html)
function getLivekit() {
    // try common globals from UMD bundle (official: LivekitClient)
    if (window.LivekitClient) return window.LivekitClient;
    if (window.Livekit) return window.Livekit;
    if (window.livekit) return window.livekit;
    if (window.livekitClient) return window.livekitClient;
    return null;
}

let room = null;
let isRecording = false;
let micButton = null;
let statusElement = null;
let transcriptElement = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    micButton = document.getElementById('micButton');
    statusElement = document.getElementById('status');
    transcriptElement = document.getElementById('transcript');
    
    micButton.addEventListener('click', toggleMicrophone);
    
    // Try to connect automatically after a short delay
    setTimeout(() => {
        connectToRoom();
    }, 500);
});

async function connectToRoom() {
    try {
        updateStatus('Connecting...');
        micButton.disabled = true;
        
        // Ensure LiveKit client is available
        const LK = getLivekit();
        if (!LK) {
            throw new Error('LiveKit client library failed to load. Try a hard refresh');
        }

        // Get access token from server
        const response = await fetch('/api/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get access token');
        }
        
        const { token, url, room: roomName } = await response.json();
        
        // Connect to LiveKit room
        room = new LK.Room();
        
        // Set up event handlers
        room.on('connected', () => {
            updateStatus('Connected');
            micButton.disabled = false;
            addTranscriptMessage('system', 'Connected to voice assistant');
        });
        
        room.on('disconnected', () => {
            updateStatus('Disconnected');
            micButton.disabled = true;
            addTranscriptMessage('system', 'Disconnected from voice assistant');
        });
        
        room.on('trackSubscribed', (track, publication, participant) => {
            if (track.kind === (getLivekit().Track.Kind.Audio)) {
                // Play audio from the assistant
                const audioElement = track.attach();
                document.body.appendChild(audioElement);
                audioElement.play();
            }
        });
        
        room.on('localTrackPublished', (publication, participant) => {
            if (publication.kind === (getLivekit().Track.Kind.Audio)) {
                updateStatus('Recording');
            }
        });
        
        room.on('localTrackUnpublished', (publication, participant) => {
            if (publication.kind === (getLivekit().Track.Kind.Audio)) {
                updateStatus('Connected');
            }
        });
        
        // Connect to the room
        await room.connect(url, token);
        
        // Get user's microphone (with permission request)
        try {
            const tracks = await room.localParticipant.setMicrophoneEnabled(true);
            if (tracks) {
                isRecording = true;
                micButton.classList.add('recording');
                micButton.querySelector('.mic-text').textContent = 'Stop';
                updateStatus('Recording');
                addTranscriptMessage('system', 'Microphone enabled - you can now speak');
            }
        } catch (micError) {
            console.error('Microphone permission error:', micError);
            addTranscriptMessage('system', 'Error: Please allow microphone access in your browser settings');
            micButton.disabled = false; // Keep button enabled so user can try again
        }
        
    } catch (error) {
        console.error('Connection error:', error);
        updateStatus('Connection Error');
        let errorMsg = error.message || 'Unknown error';
        if (errorMsg.includes('Failed to get access token')) {
            errorMsg = 'Server error: Check LiveKit credentials in .env file';
        } else if (errorMsg.includes('WebSocket')) {
            errorMsg = 'Cannot connect to LiveKit server. Check LIVEKIT_URL in .env';
        }
        addTranscriptMessage('system', `Error: ${errorMsg}`);
        micButton.disabled = true;
    }
}

async function toggleMicrophone() {
    if (!room) {
        await connectToRoom();
        return;
    }
    
    try {
        if (isRecording) {
            // Stop recording
            await room.localParticipant.setMicrophoneEnabled(false);
            isRecording = false;
            micButton.classList.remove('recording');
            micButton.querySelector('.mic-text').textContent = 'Start';
            updateStatus('Connected');
        } else {
            // Start recording
            await room.localParticipant.setMicrophoneEnabled(true);
            isRecording = true;
            micButton.classList.add('recording');
            micButton.querySelector('.mic-text').textContent = 'Stop';
            updateStatus('Recording');
        }
    } catch (error) {
        console.error('Microphone error:', error);
        addTranscriptMessage('system', `Microphone error: ${error.message}`);
    }
}

function updateStatus(status) {
    statusElement.textContent = status;
    statusElement.className = 'status';
    
    // Add status-specific styling
    if (status.includes('Connected') || status.includes('Recording')) {
        statusElement.style.backgroundColor = status.includes('Recording') ? '#3b82f6' : '#4ade80';
        statusElement.style.color = 'white';
    } else if (status.includes('Disconnected')) {
        statusElement.style.backgroundColor = '#ef4444';
        statusElement.style.color = 'white';
    } else if (status.includes('Connecting')) {
        statusElement.style.backgroundColor = '#fbbf24';
        statusElement.style.color = 'white';
    } else {
        statusElement.style.backgroundColor = '#ef4444';
        statusElement.style.color = 'white';
    }
}

function addTranscriptMessage(type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    transcriptElement.appendChild(messageDiv);
    transcriptElement.scrollTop = transcriptElement.scrollHeight;
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (room) {
        room.disconnect();
    }
});

