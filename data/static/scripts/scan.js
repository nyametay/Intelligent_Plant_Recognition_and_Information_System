let currentStream = null;
let useFrontCamera = true;
const cameraFeed = document.getElementById('cameraFeed');
const capturedCanvas = document.getElementById('capturedCanvas');
const capturedImageInput = document.getElementById('capturedImageInput');
const uploadCaptureBtn = document.getElementById('uploadCaptureBtn');

async function startCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  const constraints = {
    video: {
      facingMode: useFrontCamera ? 'user' : 'environment'
    }
  };

  try {
    currentStream = await navigator.mediaDevices.getUserMedia(constraints);
    cameraFeed.srcObject = currentStream;
  } catch (err) {
    console.error('Camera access denied:', err);
  }
}

document.getElementById('openCamera').addEventListener('click', () => {
  document.getElementById('cameraModal').classList.remove('hidden');
  startCamera();
});

document.getElementById('switchCameraBtn').addEventListener('click', () => {
  useFrontCamera = !useFrontCamera;
  startCamera();
});

document.getElementById('captureBtn').addEventListener('click', () => {
  const context = capturedCanvas.getContext('2d');
  capturedCanvas.width = cameraFeed.videoWidth;
  capturedCanvas.height = cameraFeed.videoHeight;
  context.drawImage(cameraFeed, 0, 0);
  capturedCanvas.classList.remove('hidden');
  uploadCaptureBtn.classList.remove('hidden');

  // Convert to base64 and store
  const imageData = capturedCanvas.toDataURL('image/png');
  capturedImageInput.value = imageData;
});

document.getElementById('uploadCaptureBtn').addEventListener('click', () => {
  document.getElementById('uploadForm').submit();
});

document.getElementById('closeModalBtn').addEventListener('click', () => {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }
  document.getElementById('cameraModal').classList.add('hidden');
});
