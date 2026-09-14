
let currentStream;
let useFrontCamera = true;

const cameraFeed = document.getElementById("cameraFeed");
const capturedCanvas = document.getElementById("capturedCanvas");
const capturedImageInput = document.getElementById("capturedImageInput");
const captureBtn = document.getElementById("captureBtn");
const switchCameraBtn = document.getElementById("switchCameraBtn");
const uploadCapturedBtn = document.getElementById("uploadCapturedBtn");

// File input and preview
const fileInput = document.getElementById("fileInput");
const uploadPreview = document.getElementById("uploadPreview");

let selectedImageURL = null;


// ========================================
// FILE UPLOAD PREVIEW
// ========================================

fileInput.addEventListener("change", function () {
  const file = this.files[0];

  if (!file) return;

  // Validate image type
  if (!file.type.startsWith("image/")) {
    alert("Please select a valid image file.");
    this.value = "";
    return;
  }

  // Validate file size (5MB)
  const maxSize = 5 * 1024 * 1024;

  if (file.size > maxSize) {
    alert("Image size must not exceed 5MB.");
    this.value = "";
    return;
  }

  // Revoke previous temporary URL
  if (selectedImageURL) {
    URL.revokeObjectURL(selectedImageURL);
  }

  // Create preview URL
  selectedImageURL = URL.createObjectURL(file);

  // Display uploaded image
  uploadPreview.src = selectedImageURL;
  uploadPreview.classList.remove("hidden");

  // Clear camera's hidden base64 input
  capturedImageInput.value = "";
});


// ========================================
// START CAMERA
// ========================================

async function startCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  const constraints = {
    video: {
      facingMode: useFrontCamera ? "user" : "environment"
    }
  };

  currentStream = await navigator.mediaDevices.getUserMedia(constraints);

  cameraFeed.srcObject = currentStream;

  // Reset UI
  capturedCanvas.classList.add("hidden");
  cameraFeed.classList.remove("hidden");

  captureBtn.classList.remove("hidden");
  switchCameraBtn.classList.remove("hidden");
  uploadCapturedBtn.classList.add("hidden");
}


// ========================================
// OPEN CAMERA
// ========================================

document.getElementById("openCamera").addEventListener("click", () => {
  document.getElementById("cameraModal").classList.remove("hidden");

  startCamera();
});


// ========================================
// CLOSE CAMERA MODAL
// ========================================

document.getElementById("closeModalBtn").addEventListener("click", () => {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  document.getElementById("cameraModal").classList.add("hidden");
});


// ========================================
// SWITCH CAMERA
// ========================================

switchCameraBtn.addEventListener("click", () => {
  useFrontCamera = !useFrontCamera;

  startCamera();
});


// ========================================
// CAPTURE IMAGE
// ========================================

captureBtn.addEventListener("click", () => {
  const context = capturedCanvas.getContext("2d");

  capturedCanvas.width = cameraFeed.videoWidth;
  capturedCanvas.height = cameraFeed.videoHeight;

  context.drawImage(
    cameraFeed,
    0,
    0,
    cameraFeed.videoWidth,
    cameraFeed.videoHeight
  );

  // Show captured image
  cameraFeed.classList.add("hidden");
  capturedCanvas.classList.remove("hidden");

  // Hide capture and switch buttons
  captureBtn.classList.add("hidden");
  switchCameraBtn.classList.add("hidden");

  // Show upload button
  uploadCapturedBtn.classList.remove("hidden");
});


// ========================================
// UPLOAD CAPTURED CAMERA IMAGE
// ========================================

uploadCapturedBtn.addEventListener("click", () => {
  const imageData = capturedCanvas.toDataURL("image/jpeg", 0.8);

  // Store camera image as base64
  capturedImageInput.value = imageData;

  // Close camera modal
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  document.getElementById("cameraModal").classList.add("hidden");

  // Show preview on main form
  uploadPreview.src = imageData;
  uploadPreview.classList.remove("hidden");

  // Clear file input because camera image is being used
  fileInput.value = "";
});
