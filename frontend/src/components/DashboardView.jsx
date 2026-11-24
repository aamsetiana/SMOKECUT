import React, { useState } from 'react';
import {
  Flame,
  ShieldCheck,
  Spline,
  CloudFog,
  SunMedium,
  Wind,
  Compass,
  AlertTriangle,
  ArrowRight,
  ZoomIn,
  ZoomOut,
  Layers
} from 'lucide-react';
import { getAssetUrl, normalizeRiskLevel, formatCuttingLength, formatProtectedArea } from '../services/api';

export default function DashboardView({ analysisData, onNavigateToAnalysis, onNavigateToRiskMap }) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showOverlays, setShowOverlays] = useState(true);

  // Normalize raw backend status ("TINGGI" -> "Bahaya", "SEDANG" -> "Waspada", "RENDAH" -> "Aman")
  const rawRisk = analysisData?.summary?.risk_level;
  const riskLevel = normalizeRiskLevel(rawRisk);

  const riskConfig = {
    Bahaya: {
      textColor: 'text-rose-600',
      barColor: 'bg-rose-500 w-4/5',
      badge: 'bg-rose-50 text-rose-700 border-rose-200',
      iconBg: 'bg-rose-50 border-rose-200 text-rose-600',
      tag: 'Kritis',
    },
    Waspada: {
      textColor: 'text-amber-600',
      barColor: 'bg-amber-500 w-1/2',
      badge: 'bg-amber-50 text-amber-700 border-amber-200',
      iconBg: 'bg-amber-50 border-amber-200 text-amber-600',
      tag: 'Siaga',
    },
    Aman: {
      textColor: 'text-emerald-600',
      barColor: 'bg-emerald-500 w-1/4',
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      iconBg: 'bg-emerald-50 border-emerald-200 text-emerald-600',
      tag: 'Terkendali',
    },
  };
  const currentRisk = riskConfig[riskLevel] || riskConfig.Bahaya;

  const protectedArea = formatProtectedArea(analysisData?.summary?.protected_hectares);
  const cuttingLength = formatCuttingLength(analysisData?.summary?.cutting_length_meters);
  const pm25Value = '68 µg/m³';

  // Layer assets
  const originalUrl = analysisData?.layers?.original_image_url
    ? getAssetUrl(analysisData.layers.original_image_url)
    : '/static/uploads/sample_aerial.jpg';
  const heatmapUrl = analysisData?.layers?.vari_heatmap_url
    ? getAssetUrl(analysisData.layers.vari_heatmap_url)
    : null;
  const firebreakUrl = analysisData?.layers?.firebreak_overlay_url
    ? getAssetUrl(analysisData.layers.firebreak_overlay_url)
    : null;

  return (
    <div className="space-y-6">
      {/* 4 Stat Cards at the Top (White & Green Theme) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Tingkat Risiko */}
        <div className="bg-white border border-slate-200/80 hover:border-emerald-500 rounded-2xl p-4 flex items-center justify-between transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-emerald-500/5 group">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Tingkat Risiko</span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-xl font-black ${currentRisk.textColor}`}>{riskLevel}</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider border ${currentRisk.badge}`}>
                {currentRisk.tag}
              </span>
            </div>
            {/* Dynamic progress indicator bar */}
            <div className="w-28 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-2">
              <div className={`h-full rounded-full transition-all duration-500 ${currentRisk.barColor}`} />
            </div>
          </div>
          <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center shadow-sm shrink-0 ${currentRisk.iconBg}`}>
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
        </div>

        {/* Card 2: Lahan Aman */}
        <div className="bg-white border border-slate-200/90 hover:border-emerald-400 rounded-2xl p-4 flex items-center justify-between transition-all shadow-sm hover:shadow-md group">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Lahan Aman</span>
            <div className="text-xl font-black text-slate-900">{protectedArea}</div>
            <p className="text-[10px] text-emerald-600 font-bold">Vegetasi lembap terlindungi</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shrink-0 shadow-sm">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        {/* Card 3: Panjang Sekat */}
        <div className="bg-white border border-slate-200/90 hover:border-purple-400 rounded-2xl p-4 flex items-center justify-between transition-all shadow-sm hover:shadow-md group">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Panjang Sekat</span>
            <div className="text-xl font-black text-slate-900">{cuttingLength}</div>
            <p className="text-[10px] text-purple-600 font-semibold">Lebar rekomendasi: 3–5 m</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600 shrink-0 shadow-sm">
            <Spline className="w-6 h-6" />
          </div>
        </div>

        {/* Card 4: PM2.5 */}
        <div className="bg-white border border-slate-200/90 hover:border-amber-400 rounded-2xl p-4 flex items-center justify-between transition-all shadow-sm hover:shadow-md relative group">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">PM2.5</span>
            <div className="flex items-center gap-2">
              <span className="text-xl font-black text-slate-900">{pm25Value}</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-100 border border-amber-300 text-amber-900 text-[10px] font-extrabold uppercase tracking-wider shadow-sm">
                Waspada
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Kualitas udara downwind</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 shrink-0 shadow-sm">
            <CloudFog className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Grid: Map & Weather Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Center / Left: Aerial Map Canvas (3 cols) */}
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col relative overflow-hidden min-h-[470px]">
          {/* Top Left Floating Badges */}
          <div className="absolute top-6 left-6 z-20 flex items-center gap-2">
            <div className="flex items-center gap-2 bg-white/95 backdrop-blur-md border border-emerald-300 px-3.5 py-1.5 rounded-xl text-xs font-bold text-emerald-800 shadow-md">
              <Wind className="w-4 h-4 text-emerald-600" />
              <span>Angin 12 Km/jam → Timur</span>
            </div>
            <button
              onClick={() => setShowOverlays(!showOverlays)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border backdrop-blur-md transition shadow-sm ${
                showOverlays
                  ? 'bg-emerald-50 border-emerald-400 text-emerald-800'
                  : 'bg-white/90 border-slate-200 text-slate-600 hover:text-slate-900'
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-emerald-600" />
              <span>{showOverlays ? 'Overlay Aktif' : 'Citra Polos'}</span>
            </button>
          </div>

          {/* Compass Icon Top Right */}
          <div className="absolute top-6 right-6 z-20 flex items-center gap-2">
            <div className="w-9 h-9 rounded-full bg-white/95 border border-slate-200 flex items-center justify-center text-amber-500 shadow-md">
              <Compass className="w-5 h-5" />
            </div>
          </div>

          {/* Map Display Container */}
          <div className="flex-1 rounded-xl overflow-hidden relative bg-slate-900 border border-slate-200 flex items-center justify-center">
            {/* Drone Aerial Base Image */}
            <img
              src={getAssetUrl('/static/uploads/sample_aerial.jpg')}
              alt="Drone Aerial View"
              className="w-full h-full object-cover transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel})` }}
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />

            {/* Simulated Heatmap and Firebreak Canvas Overlay */}
            {showOverlays && (
              <div
                className="absolute inset-0 pointer-events-none mix-blend-screen transition-opacity duration-300"
                style={{ transform: `scale(${zoomLevel})` }}
              >
                {/* Heatmap overlay image if generated */}
                {heatmapUrl ? (
                  <img src={heatmapUrl} alt="Heatmap" className="w-full h-full object-cover opacity-85" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-tr from-red-600/35 via-amber-500/30 to-emerald-600/25" />
                )}

                {/* Hotspot Markers */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                  <div className="relative">
                    <span className="w-8 h-8 rounded-full bg-rose-500/60 animate-ping absolute -top-1 -left-1" />
                    <div className="w-6 h-6 rounded-full bg-rose-600 border-2 border-white flex items-center justify-center text-white shadow-lg">
                      <Flame className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>

                {/* Firebreak SVG Line (curved white dashed barrier) */}
                <svg className="absolute inset-0 w-full h-full">
                  <path
                    d="M 120 400 Q 300 200 480 220 T 700 300"
                    fill="none"
                    stroke="#FFFFFF"
                    strokeWidth="3.5"
                    strokeDasharray="8 6"
                    className="drop-shadow-[0_0_8px_rgba(255,255,255,0.9)]"
                  />
                </svg>
              </div>
            )}

            {/* Floating Legend Box (White Glassmorphism) */}
            <div className="absolute top-18 right-6 z-20 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-2xl p-3.5 text-xs text-slate-800 space-y-2 shadow-xl min-w-[155px]">
              <div className="font-extrabold text-slate-900 text-[11px] flex items-center gap-1.5 border-b border-slate-100 pb-1.5">
                <span className="text-amber-500">★</span> Legenda
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-rose-500 shrink-0 shadow-sm" />
                <span className="text-[11px] font-bold text-slate-800">Zona Bahaya</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-amber-400 shrink-0 shadow-sm" />
                <span className="text-[11px] font-bold text-slate-800">Zona Waspada</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-emerald-500 shrink-0 shadow-sm" />
                <span className="text-[11px] font-bold text-slate-800">Zona Aman</span>
              </div>
              <div className="border-t border-slate-100 pt-2 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="w-5 border-b-2 border-dashed border-slate-900 inline-block" />
                  <span className="text-[11px] font-medium text-slate-700">Sekat Bakar (3-5 m)</span>
                </div>
                <div className="flex items-center gap-2">
                  <Flame className="w-3.5 h-3.5 text-rose-500" />
                  <span className="text-[11px] font-medium text-slate-700">Deteksi Api</span>
                </div>
                <div className="flex items-center gap-2">
                  <Wind className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-[11px] font-medium text-slate-700">Arah Angin</span>
                </div>
              </div>
            </div>

            {/* Map Controls (+ / -) Bottom Right */}
            <div className="absolute bottom-4 right-4 z-20 flex flex-col gap-1.5">
              <button
                onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.2))}
                className="w-7 h-7 rounded-lg bg-white/95 border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-emerald-50 hover:text-emerald-700 transition shadow-md"
                title="Perbesar"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.8))}
                className="w-7 h-7 rounded-lg bg-white/95 border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-emerald-50 hover:text-emerald-700 transition shadow-md"
                title="Perkecil"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Scale Bar Bottom Left */}
            <div className="absolute bottom-4 left-4 z-20 bg-white/95 px-2.5 py-1 rounded-lg text-[10px] text-slate-700 border border-slate-200 font-mono font-bold shadow-md">
              0 ── 2 ── 5 Km
            </div>
          </div>
        </div>

        {/* Right Column: Cuaca & Peringatan Dini (1 col) */}
        <div className="space-y-4">
          {/* Informasi Cuaca Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Informasi Cuaca</h3>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-500 shrink-0">
                <SunMedium className="w-7 h-7" />
              </div>
              <div>
                <div className="text-2xl font-black text-slate-900">32°C</div>
                <div className="text-xs text-slate-500 font-medium">Cerah Berawan</div>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-3 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-600">
                  <Wind className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Arah Angin</span>
                </div>
                <span className="font-bold text-slate-900">Timur (90°)</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-600">
                  <Compass className="w-3.5 h-3.5 text-slate-400" />
                  <span>Kecepatan</span>
                </div>
                <span className="font-bold text-slate-900">12 Km/jam</span>
              </div>
            </div>
          </div>

          {/* Peringatan Dini Card (Clean Green Accent) */}
          <div className="bg-gradient-to-br from-emerald-50 via-white to-green-50/70 border border-emerald-200 rounded-2xl p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-emerald-800 font-extrabold text-xs">
              <AlertTriangle className="w-4 h-4 text-emerald-600" />
              <span>Peringatan Dini</span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              Potensi kebakaran meningkat di area utara hutan akibat vegetasi semak kering dan dorongan angin kencang ke arah timur.
            </p>
            <button
              onClick={onNavigateToAnalysis}
              className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition"
            >
              <span>Lihat Detail</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
