/**
 * SEKAT-AI API Service Client.
 * Values missing from the backend stay missing: nothing is filled in on the client.
 */

export const API_BASE_URL = window.location.port === '5173' ? 'http://127.0.0.1:8000' : '';

export const NO_DATA = 'Belum ada data';

/** Field measurements accepted by POST /api/analyze. */
export const FIELD_PARAMS = [
  { name: 'fuel_height_m', label: 'Tinggi vegetasi terbakar (m)', hint: 'Untuk jarak aman' },
  { name: 'protected_plant_height_m', label: 'Tinggi tanaman dilindungi (m)', hint: 'Untuk lebar sekat' },
  { name: 'wind_direction', label: 'Arah angin datang (°)', hint: '0 = utara, 90 = timur' },
  { name: 'wind_speed', label: 'Kecepatan angin (km/jam)', hint: 'Dari alat ukur / BMKG' },
  { name: 'slope_wind_factor', label: 'Faktor angin-lereng (≥ 1)', hint: 'Tabel USFS' },
  { name: 'ground_width_m', label: 'Lebar area di foto (m)', hint: 'Sisi terpanjang, untuk skala' },
  { name: 'latitude', label: 'Lintang pusat foto', hint: 'Untuk GPS' },
  { name: 'longitude', label: 'Bujur pusat foto', hint: 'Untuk GPS' },
  { name: 'heading_deg', label: 'Arah atas foto (°)', hint: '0 = utara, untuk GPS' },
];

export function getAssetUrl(path) {
  if (!path) return '';
  if (/^(https?:|data:|blob:)/.test(path)) return path;
  return `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;
}

/** Map the backend level (TINGGI/SEDANG/RENDAH) to the dashboard wording. */
export function normalizeRiskLevel(level) {
  return { TINGGI: 'Bahaya', SEDANG: 'Waspada', RENDAH: 'Aman' }[String(level || '').toUpperCase()] || null;
}

const isMissing = (value) => value === undefined || value === null || Number.isNaN(Number(value));

export function formatNumber(value, unit, digits = 1) {
  if (isMissing(value)) return NO_DATA;
  return `${Number(value).toLocaleString('id-ID', { maximumFractionDigits: digits })} ${unit}`.trim();
}

/** Firebreak length; only a lower bound when part of the line is outside the frame. */
export function formatCuttingLength(analysis) {
  const meters = analysis?.summary?.cutting_length_meters;
  if (isMissing(meters)) return NO_DATA;
  return `${analysis?.firebreak_plan?.is_partial ? '≥ ' : ''}${formatNumber(meters, 'm')}`;
}

export function formatPercent(value) {
  return isMissing(value) ? NO_DATA : `${formatNumber(value, '')}%`;
}

export function formatWind(wind) {
  if (!wind?.direction_compass) return NO_DATA;
  const speed = isMissing(wind.speed_kmh) ? '' : `, ${formatNumber(wind.speed_kmh, 'km/jam')}`;
  return `Dari ${wind.direction_compass}${speed}${wind.is_auto_detected ? ' (perkiraan)' : ''}`;
}

async function parseResponse(res, fallback) {
  const data = await res.json().catch(() => null);
  if (res.ok && data) return data;
  const detail = data?.detail;
  if (Array.isArray(detail)) {
    const fields = detail.map((d) => {
      const name = d.loc?.[d.loc.length - 1];
      return FIELD_PARAMS.find((f) => f.name === name)?.label || name;
    });
    throw new Error(`Isian tidak valid: ${fields.join(', ')}`);
  }
  throw new Error(detail || fallback);
}

export async function checkHealth() {
  try {
    return await parseResponse(await fetch(`${API_BASE_URL}/health`), 'Backend bermasalah');
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function uploadMedia(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/api/upload`, { method: 'POST', body: formData });
  return parseResponse(res, 'Gagal mengunggah media');
}

/** Run the analysis, sending only the field measurements that were filled in. */
export async function runAnalysis(imageId, fieldData = {}) {
  const payload = { image_id: imageId };
  FIELD_PARAMS.forEach(({ name }) => {
    const value = fieldData[name];
    if (value !== undefined && value !== null && value !== '') payload[name] = Number(value);
  });
  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseResponse(res, 'Gagal menjalankan analisis');
}

export async function dispatchWhatsApp(analysis) {
  const res = await fetch(`${API_BASE_URL}/api/dispatch-whatsapp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_data: analysis }),
  });
  return parseResponse(res, 'Gagal membuat pesan WhatsApp');
}
