const fileInput = document.getElementById('fileInput');
const uploadPreview = document.getElementById('uploadPreview');
const uploadLabel = document.getElementById('uploadLabel');
const cameraModal = document.getElementById('cameraModal');
const openCamera = document.getElementById('openCamera');
const closeModalBtn = document.getElementById('closeModalBtn');
const closeCamera = document.getElementById('closeCamera');
const cameraFeed = document.getElementById('cameraFeed');
const capturedCanvas = document.getElementById('capturedCanvas');
const captureBtn = document.getElementById('captureBtn');
const capturedImageInput = document.getElementById('capturedImageInput');

let stream;

// === FILE UPLOAD PREVIEW ===
fileInput.addEventListener("change", (event) => {
const file = event.target.files[0];
if (file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    uploadPreview.src = e.target.result;
    uploadPreview.classList.remove('hidden');
  };
  reader.readAsDataURL(file);
  uploadLabel.querySelector("p").textContent = "Selected: " + file.name;
}
});

// === CAMERA HANDLING ===
openCamera.addEventListener("click", async () => {
try {
  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  cameraFeed.srcObject = stream;
  cameraModal.classList.remove("hidden");
  capturedCanvas.classList.add("hidden");
  cameraFeed.classList.remove("hidden");
} catch (err) {
  alert("Unable to access the camera. Please allow permissions.");
}
});

const closeCameraModal = () => {
cameraModal.classList.add("hidden");
if (stream) stream.getTracks().forEach(track => track.stop());
};

closeModalBtn.addEventListener("click", closeCameraModal);
closeCamera.addEventListener("click", closeCameraModal);

captureBtn.addEventListener("click", () => {
capturedCanvas.width = cameraFeed.videoWidth;
capturedCanvas.height = cameraFeed.videoHeight;
const context = capturedCanvas.getContext("2d");
context.drawImage(cameraFeed, 0, 0, cameraFeed.videoWidth, cameraFeed.videoHeight);

const capturedData = capturedCanvas.toDataURL("image/png");
capturedImageInput.value = capturedData;

capturedCanvas.classList.remove("hidden");
cameraFeed.classList.add("hidden");
alert("Image captured! You can now submit the form.");
});