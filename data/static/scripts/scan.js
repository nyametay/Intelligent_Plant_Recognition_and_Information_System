let currentStream;
let useFrontCamera = true;

const cameraFeed = document.getElementById("cameraFeed");
const capturedCanvas = document.getElementById("capturedCanvas");
const capturedImageInput = document.getElementById("capturedImageInput");
const captureBtn = document.getElementById("captureBtn");
const switchCameraBtn = document.getElementById("switchCameraBtn");
const uploadCapturedBtn = document.getElementById("uploadCapturedBtn");

async function startCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  const constraints = { video: { facingMode: useFrontCamera ? "user" : "environment" } };
  currentStream = await navigator.mediaDevices.getUserMedia(constraints);
  cameraFeed.srcObject = currentStream;

  // Reset UI
  capturedCanvas.classList.add("hidden");
  cameraFeed.classList.remove("hidden");
  captureBtn.classList.remove("hidden");
  switchCameraBtn.classList.remove("hidden");
  uploadCapturedBtn.classList.add("hidden");
}

document.getElementById("openCamera").addEventListener("click", () => {
  document.getElementById("cameraModal").classList.remove("hidden");
  startCamera();
});

document.getElementById("closeModalBtn").addEventListener("click", () => {
  if (currentStream) currentStream.getTracks().forEach(track => track.stop());
  document.getElementById("cameraModal").classList.add("hidden");
});

switchCameraBtn.addEventListener("click", () => {
  useFrontCamera = !useFrontCamera;
  startCamera();
});

captureBtn.addEventListener("click", () => {
  const context = capturedCanvas.getContext("2d");
  capturedCanvas.width = cameraFeed.videoWidth;
  capturedCanvas.height = cameraFeed.videoHeight;
  context.drawImage(cameraFeed, 0, 0, cameraFeed.videoWidth, cameraFeed.videoHeight);

  // Show captured image, hide video
  cameraFeed.classList.add("hidden");
  capturedCanvas.classList.remove("hidden");

  // Hide capture/switch, show upload
  captureBtn.classList.add("hidden");
  switchCameraBtn.classList.add("hidden");
  uploadCapturedBtn.classList.remove("hidden");
});

uploadCapturedBtn.addEventListener("click", () => {
  //const imageData = capturedCanvas.toDataURL("image/png");
  const imageData = capturedCanvas.toDataURL("image/jpeg", 0.8); // compress to 70% quality
  capturedImageInput.value = imageData;

  // Close camera modal
  if (currentStream) currentStream.getTracks().forEach(track => track.stop());
  document.getElementById("cameraModal").classList.add("hidden");

  // Show preview on main form
  const uploadPreview = document.getElementById("uploadPreview");
  uploadPreview.src = imageData;
  uploadPreview.classList.remove("hidden");
});


