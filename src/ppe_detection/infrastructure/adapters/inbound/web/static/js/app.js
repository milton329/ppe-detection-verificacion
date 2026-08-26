const CLASS_COLORS = {
  helmet: "#22c55e",
  vest: "#3b82f6",
  "no-helmet": "#ef4444",
  human: "#9aa1ac",
};

const CLASS_LABELS = {
  helmet: "Casco",
  vest: "Chaleco",
  "no-helmet": "Sin casco",
  human: "Persona",
};

function classLabel(className) {
  return CLASS_LABELS[className] || className;
}

const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const dropzoneEmpty = document.getElementById("dropzone-empty");
const canvasWrap = document.getElementById("canvas-wrap");
const canvas = document.getElementById("preview-canvas");
const ctx = canvas.getContext("2d");

const confidenceInput = document.getElementById("confidence-input");
const confidenceValue = document.getElementById("confidence-value");
const detectButton = document.getElementById("detect-button");
const errorMessage = document.getElementById("error-message");

const resultsEmpty = document.getElementById("results-empty");
const resultsLoading = document.getElementById("results-loading");
const resultsContent = document.getElementById("results-content");
const detectionSummaryEl = document.getElementById("detection-summary");
const complianceSummaryEl = document.getElementById("compliance-summary");
const personListEl = document.getElementById("person-list");
const detectionListEl = document.getElementById("detection-list");

const cameraToggleBtn = document.getElementById("camera-toggle-btn");
const cameraWrap = document.getElementById("camera-wrap");
const cameraVideo = document.getElementById("camera-video");
const cameraCaptureBtn = document.getElementById("camera-capture-btn");
const cameraCancelBtn = document.getElementById("camera-cancel-btn");

let currentImage = null;
let currentFile = null;
let cameraStream = null;

confidenceInput.addEventListener("input", () => {
  confidenceValue.textContent = Number(confidenceInput.value).toFixed(2);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) loadImage(file);
});

["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone--active");
  })
);

["dragleave", "dragend"].forEach((evt) =>
  dropzone.addEventListener(evt, () => dropzone.classList.remove("dropzone--active"))
);

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dropzone--active");
  const file = e.dataTransfer.files[0];
  if (file) loadImage(file);
});

function loadImage(file) {
  hideError();
  currentFile = file;
  const image = new Image();
  image.onload = () => {
    currentImage = image;
    dropzoneEmpty.hidden = true;
    canvasWrap.hidden = false;
    drawImageOnly();
    detectButton.disabled = false;
  };
  image.src = URL.createObjectURL(file);
}

function drawImageOnly() {
  const maxWidth = 560;
  const scale = Math.min(1, maxWidth / currentImage.naturalWidth);
  canvas.width = currentImage.naturalWidth * scale;
  canvas.height = currentImage.naturalHeight * scale;
  ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
}

cameraToggleBtn.addEventListener("click", startCamera);
cameraCancelBtn.addEventListener("click", stopCamera);
cameraCaptureBtn.addEventListener("click", capturePhoto);

async function startCamera() {
  hideError();
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false,
    });
  } catch (err) {
    showError(
      "No se pudo acceder a la cámara. Revisa los permisos del navegador."
    );
    return;
  }
  cameraVideo.srcObject = cameraStream;
  dropzone.hidden = true;
  cameraToggleBtn.hidden = true;
  cameraWrap.hidden = false;
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
  cameraWrap.hidden = true;
  dropzone.hidden = false;
  cameraToggleBtn.hidden = false;
}

function capturePhoto() {
  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = cameraVideo.videoWidth;
  tempCanvas.height = cameraVideo.videoHeight;
  tempCanvas.getContext("2d").drawImage(cameraVideo, 0, 0);

  tempCanvas.toBlob(
    (blob) => {
      const file = new File([blob], "camara.jpg", { type: "image/jpeg" });
      stopCamera();
      loadImage(file);
    },
    "image/jpeg",
    0.92
  );
}

function drawDetections(detections) {
  drawImageOnly();
  const scaleX = canvas.width / currentImage.naturalWidth;
  const scaleY = canvas.height / currentImage.naturalHeight;

  detections.forEach((det) => {
    const [x1, y1, x2, y2] = det.bbox;
    const color = CLASS_COLORS[det.class_name] || "#e8eaed";
    const bx = x1 * scaleX;
    const by = y1 * scaleY;
    const bw = (x2 - x1) * scaleX;
    const bh = (y2 - y1) * scaleY;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(bx, by, bw, bh);

    const label = `${classLabel(det.class_name)} ${(det.confidence * 100).toFixed(0)}%`;
    ctx.font = "600 12px Segoe UI, sans-serif";
    const textWidth = ctx.measureText(label).width;
    ctx.fillStyle = color;
    ctx.fillRect(bx, Math.max(0, by - 18), textWidth + 10, 18);
    ctx.fillStyle = "#0f1115";
    ctx.fillText(label, bx + 5, Math.max(12, by - 5));
  });
}

detectButton.addEventListener("click", async () => {
  if (!currentFile) return;
  hideError();
  showLoading();

  const formData = new FormData();
  formData.append("file", currentFile);
  const confidence = confidenceInput.value;

  try {
    const response = await fetch(`/detect?confidence=${confidence}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`El servidor respondió con estado ${response.status}`);
    }

    const data = await response.json();
    drawDetections(data.detections);
    showResults(data);
  } catch (err) {
    showError(err.message || "No se pudo completar el análisis.");
    resultsEmpty.hidden = false;
    resultsLoading.hidden = true;
  }
});

function showLoading() {
  resultsEmpty.hidden = true;
  resultsContent.hidden = true;
  resultsLoading.hidden = false;
}

function statusLabel(status) {
  return {
    COMPLIANT: "Cumple",
    NON_COMPLIANT: "No cumple",
    NO_PERSONS: "Sin personas detectadas",
  }[status] || status;
}

function renderCompliance(persons, summary) {
  complianceSummaryEl.innerHTML = "";
  const status = document.createElement("div");
  status.className = `compliance-status compliance-status--${summary.status.toLowerCase()}`;
  status.textContent = `Estado general: ${statusLabel(summary.status)}`;
  complianceSummaryEl.appendChild(status);

  const summaryDetails = document.createElement("div");
  summaryDetails.className = "compliance-summary__details";
  [
    `Total de personas: ${summary.total_persons}`,
    `Conformes: ${summary.compliant}`,
    `No conformes: ${summary.non_compliant}`,
  ].forEach((text) => {
    const chip = document.createElement("span");
    chip.className = "summary__chip";
    chip.textContent = text;
    summaryDetails.appendChild(chip);
  });
  complianceSummaryEl.appendChild(summaryDetails);

  personListEl.innerHTML = "";
  if (summary.status === "NO_PERSONS") return;

  persons.forEach((person) => {
    const item = document.createElement("li");
    item.className = `person-item person-item--${person.status.toLowerCase()}`;

    const title = document.createElement("h3");
    title.textContent = `Persona ${person.id}`;

    const equipment = document.createElement("p");
    equipment.textContent = `Casco: ${person.helmet ? "Sí" : "No"} · Chaleco: ${person.vest ? "Sí" : "No"}`;

    const personStatus = document.createElement("p");
    personStatus.textContent = `Estado: ${statusLabel(person.status)}`;

    item.append(title, equipment, personStatus);
    personListEl.appendChild(item);
  });
}

function showResults(data) {
  const { detections, persons, summary } = data;
  resultsLoading.hidden = true;
  resultsContent.hidden = false;

  renderCompliance(persons, summary);

  const counts = {};
  detections.forEach((d) => {
    counts[d.class_name] = (counts[d.class_name] || 0) + 1;
  });

  detectionSummaryEl.innerHTML = "";
  if (Object.keys(counts).length === 0) {
    detectionSummaryEl.innerHTML = `<span class="summary__chip">Sin detecciones a este umbral</span>`;
  } else {
    Object.entries(counts).forEach(([className, count]) => {
      const chip = document.createElement("span");
      chip.className = "summary__chip";
      chip.textContent = `${classLabel(className)}: ${count}`;
      detectionSummaryEl.appendChild(chip);
    });
  }

  detectionListEl.innerHTML = "";
  detections
    .slice()
    .sort((a, b) => b.confidence - a.confidence)
    .forEach((det) => {
      const li = document.createElement("li");
      li.className = "detection-item";

      const dot = document.createElement("span");
      dot.className = "detection-item__dot";
      dot.style.background = CLASS_COLORS[det.class_name] || "#e8eaed";

      const name = document.createElement("span");
      name.className = "detection-item__name";
      name.textContent = classLabel(det.class_name);

      const confidence = document.createElement("span");
      confidence.className = "detection-item__confidence";
      confidence.textContent = `${(det.confidence * 100).toFixed(1)}%`;

      li.append(dot, name, confidence);
      detectionListEl.appendChild(li);
    });
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.hidden = true;
}
