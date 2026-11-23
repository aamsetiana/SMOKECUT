/**
 * SEKAT-AI API Service Client
 * Handles communication between Frontend UI and FastAPI Core Engine.
 */

const API_BASE_URL = window.location.port === '5173' ? 'http://127.0.0.1:8000' : '';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function uploadMedia(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Gagal mengunggah media');
  }

  return await res.json();
}

export async function runAnalysis(params) {
  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Gagal menjalankan analisis AI');
  }

  return await res.json();
}

export async function dispatchWhatsApp(payload) {
  const res = await fetch(`${API_BASE_URL}/api/dispatch-whatsapp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Gagal mengirim notifikasi WhatsApp');
  }

  return await res.json();
}
