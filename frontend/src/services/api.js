/* ==============================================================
   API Service — Centralized Backend Communication
   ==============================================================
   All API calls to the FastAPI backend go through here.
   This makes it easy to change the base URL or add auth later.
   ============================================================== */

const API_BASE = 'http://localhost:8000';

/**
 * POST /predict — Upload an image for AI prediction + sorting
 * @param {Blob} imageBlob - The captured frame as a Blob
 * @returns {Promise<Object>} Prediction result
 */
export async function predictImage(imageBlob) {
  const formData = new FormData();
  formData.append('file', imageBlob, 'capture.jpg');

  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Prediction failed' }));
    throw new Error(error.detail || 'Prediction failed');
  }

  return response.json();
}

/**
 * GET /predictions — Fetch recent prediction history
 * @param {number} limit - Number of predictions to fetch
 * @returns {Promise<Object>} { predictions: [...] }
 */
export async function getRecentPredictions(limit = 20) {
  const response = await fetch(`${API_BASE}/predictions?limit=${limit}`);
  return response.json();
}

/**
 * DELETE /predictions/:id — Delete a prediction by ID
 * @param {number} id - Prediction ID to remove
 * @returns {Promise<Object>} Result
 */
export async function deletePrediction(id) {
  const response = await fetch(`${API_BASE}/predictions/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

/**
 * GET /stats — Fetch dashboard statistics
 * @returns {Promise<Object>} Stats object
 */
export async function getStats() {
  const response = await fetch(`${API_BASE}/stats`);
  return response.json();
}

/**
 * GET /status — Fetch system status (camera, model, arduino, servo)
 * @returns {Promise<Object>} Status object
 */
export async function getStatus() {
  const response = await fetch(`${API_BASE}/status`);
  return response.json();
}

/**
 * GET /system-info — Fetch CPU, MEM, GPU stats
 * @returns {Promise<Object>} System info object
 */
export async function getSystemInfo() {
  const response = await fetch(`${API_BASE}/system-info`);
  return response.json();
}

/**
 * POST /serial/connect — Connect to Arduino
 * @param {string|null} port - COM port (null for default)
 * @returns {Promise<Object>} Connection result
 */
export async function connectArduino(port = null) {
  const url = port
    ? `${API_BASE}/serial/connect?port=${encodeURIComponent(port)}`
    : `${API_BASE}/serial/connect`;
  const response = await fetch(url, { method: 'POST' });
  return response.json();
}

/**
 * POST /serial/disconnect — Disconnect Arduino
 * @returns {Promise<Object>} Result
 */
export async function disconnectArduino() {
  const response = await fetch(`${API_BASE}/serial/disconnect`, { method: 'POST' });
  return response.json();
}
