const recordButton = document.getElementById("recordButton");
const chatMessages = document.getElementById("chatMessages");

let isRecording = false;
let socket;
let mediaRecorder;
let audioContext;
let audioChunks = []; // Array to hold audio chunks

// Create WebSocket connection when the user enters the page
window.addEventListener("load", () => {
  socket = new WebSocket("ws://localhost:8000/ws/audio");
  socket.binaryType = "arraybuffer";

  socket.onopen = () => {
    console.log("WebSocket connection opened");
  };

  socket.onmessage = async (event) => {
    console.log("Received message from server");
    if (typeof event.data === "string") {
      const message = JSON.parse(event.data);

      // Create a new chat box for the message
      createChatBox(message);
    } else {
        await playAudio(event.data);
    }
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onclose = (event) => {
    console.log("WebSocket connection closed:", event);
  };
});

recordButton.addEventListener("click", () => {
  if (!isRecording) {
    startRecording();
    recordButton.textContent = "Stop Recording";
  } else {
    stopRecording();
    recordButton.textContent = "Start Recording";
  }
  isRecording = !isRecording;
});

async function startRecording() {
  try {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log("Microphone access granted");

    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorder.start(250); // Send data in chunks every 250ms
    console.log("MediaRecorder started");

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data); // Store the audio chunk
        console.log("Buffered audio chunk");
      }
    };

    mediaRecorder.onerror = (error) => {
      console.error("MediaRecorder error:", error);
    };
  } catch (error) {
    console.error("Error accessing microphone:", error);
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    console.log("MediaRecorder stopped");

    // When the recording stops, send all buffered audio chunks
    if (audioChunks.length > 0) {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" }); // Create a blob from chunks
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(audioBlob); // Send the complete audio blob
        console.log("Sent all audio chunks to server");
      }
    }
  }
}

// async function playAudio(data) {
//   if (audioContext) {
//     audioContext.close();
//     console.log("Previous audio context closed");
//   }
//   audioContext = new (window.AudioContext || window.webkitAudioContext)();
//   console.log("Created new audio context");

//   try {
//     const arrayBuffer =
//       data instanceof ArrayBuffer ? data : await data.arrayBuffer();
//     const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
//     console.log("Decoded audio data");

//     const source = audioContext.createBufferSource();
//     source.buffer = audioBuffer;
//     source.connect(audioContext.destination);
//     source.start(0);
//     console.log("Started audio playback");
//   } catch (error) {
//     console.error("Error playing audio:", error);
//   }
// }

async function playAudio(data) {
    // Create a new Blob from the received audio data
    const audioBlob = new Blob([data], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob); // Create a URL for the Blob

    // Create an audio element and set its source
    const audioElement = new Audio(audioUrl);
    audioElement.play(); // Play the audio
    console.log('Started audio playback');
}

function createChatBox(message) {
  const chatMessageDiv = document.createElement("div");
  chatMessageDiv.classList.add("chat-message");

  // Display the assistant's response or transcription
  if (message.type === "text") {
    chatMessageDiv.innerHTML = `<strong>User:</strong> ${message.content}`;
  } else if (message.type === "audio") {
    chatMessageDiv.innerHTML = `<strong>Assistant:</strong> <audio controls><source src="${URL.createObjectURL(
      message.data
    )}" type="audio/webm">Your browser does not support the audio element.</audio>`;
  }

  // Append the new chat message to the chat messages container
  chatMessages.appendChild(chatMessageDiv);
}
