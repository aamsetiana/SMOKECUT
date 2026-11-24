import React, { useState } from 'react';
import {
  Wind,
  Layers,
  Flame,
  Calendar,
  ZoomIn,
  ZoomOut,
  ChevronDown,
  Eye,
  Maximize2
} from 'lucide-react';
import { getAssetUrl } from '../services/api';

export default function RiskMapView({ analysisData }) {
  const [timeFilter, setTimeFilter] = useState('hari_ini'); // 'hari_ini', 'minggu_ini', 'bulan_ini'
  const [selectedLayer, setSelectedLayer] = useState('VARI');
  const [zoomLevel, setZoomLevel] = useState(1);

  return (
    <div className="space-y-5">
      {/* Top Filter Bar */}
      <div className="flex items-center justify-end">
        <div className="flex items-center gap-3">
          {/* Time Filter Pills */}
          <div className="flex items-center bg-white border border-slate-200 p-1 rounded-xl text-xs shadow-sm">
            {[
              { id: 'hari_ini', label: 'Hari Ini' },
              { id: 'minggu_ini', label: 'Minggu Ini' },
              { id: 'bulan_ini', label: 'Bulan Ini' },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setTimeFilter(t.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  timeFilter === t.id
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Layer Selector */}
          <div className="relative">
            <select
              value={selectedLayer}
              onChange={(e) => setSelectedLayer(e.target.value)}
              className="bg-white border border-slate-200 text-xs font-bold text-slate-800 rounded-xl px-3 py-2 pr-8 appearance-none focus:outline-none focus:border-emerald-500 cursor-pointer shadow-sm"
            >
              <option value="VARI">Layer: VARI</option>
              <option value="HOTSPOT">Layer: Titik Api</option>
              <option value="FIREBREAK">Layer: Sekat Bakar</option>
              <option value="ALL">Layer: Komposit Lengkap</option>
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500 absolute right-2.5 top-2.5 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Main Map & Right Legend Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Full Interactive Heatmap Canvas (9 cols) */}
        <div className="lg:col-span-9 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col relative overflow-hidden min-h-[480px]">
          {/* Wind Vector Pill Top Left */}
          <div className="absolute top-6 left-6 z-20 flex items-center gap-2 bg-white/95 backdrop-blur-md border border-emerald-300 px-3.5 py-1.5 rounded-xl text-xs font-bold text-emerald-800 shadow-md">
            <Wind className="w-4 h-4 text-emerald-600" />
            <span>Angin 14 Km/jam → Timur</span>
          </div>

          {/* Canvas Display */}
          <div className="flex-1 rounded-xl overflow-hidden relative bg-slate-900 border border-slate-200 flex items-center justify-center">
            <img
              src={getAssetUrl('/static/uploads/sample_aerial.jpg')}
              alt="Peta Sebaran Risiko"
              className="w-full h-full object-cover transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel})` }}
            />

            {/* VARI Flammability Heatmap Gradient Overlay */}
            <div
              className="absolute inset-0 pointer-events-none mix-blend-screen transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <div className="w-full h-full bg-gradient-to-tr from-red-600/40 via-amber-500/35 to-emerald-600/20" />

              {/* Multiple Hotspots across the risk area */}
              <div className="absolute top-1/2 left-2/5 -translate-x-1/2 -translate-y-1/2">
                <span className="w-8 h-8 rounded-full bg-rose-500/60 animate-ping absolute -top-1 -left-1" />
                <div className="w-6 h-6 rounded-full bg-rose-600 border-2 border-white flex items-center justify-center text-white shadow-lg">
                  <Flame className="w-3.5 h-3.5" />
                </div>
              </div>

              <div className="absolute top-2/5 left-3/5 -translate-x-1/2 -translate-y-1/2">
                <span className="w-6 h-6 rounded-full bg-rose-500/60 animate-ping absolute -top-1 -left-1" />
                <div className="w-5 h-5 rounded-full bg-rose-600 border-2 border-white flex items-center justify-center text-white shadow-lg">
                  <Flame className="w-3 h-3" />
                </div>
              </div>

              {/* Firebreak Recommended Path */}
              <svg className="absolute inset-0 w-full h-full">
                <path
                  d="M 100 420 Q 320 220 540 240 T 780 320"
                  fill="none"
                  stroke="#FFFFFF"
                  strokeWidth="4"
                  strokeDasharray="9 6"
                  className="drop-shadow-[0_0_8px_rgba(255,255,255,0.85)]"
                />
              </svg>
            </div>

            {/* Controls */}
            <div className="absolute bottom-4 left-4 z-20 flex flex-col gap-1.5">
              <button
                onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.2))}
                className="w-7 h-7 rounded-lg bg-white/95 border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-emerald-50 hover:text-emerald-700 transition shadow"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.8))}
                className="w-7 h-7 rounded-lg bg-white/95 border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-emerald-50 hover:text-emerald-700 transition shadow"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Legend & Satellite Preview (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Tingkat Risiko Box */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-3">
            <span className="text-xs font-extrabold text-slate-900 block">Tingkat Risiko</span>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-rose-500 shrink-0" />
                <span className="text-slate-800 font-semibold">Bahaya (VARI &lt; 0.05)</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-amber-400 shrink-0" />
                <span className="text-slate-800 font-semibold">Waspada (0.05 – 0.10)</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-emerald-500 shrink-0" />
                <span className="text-slate-800 font-semibold">Aman (VARI &gt; 0.10)</span>
              </div>
            </div>
          </div>

          {/* Satellite Thumbnail Preview Box */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-2">
            <span className="text-xs font-extrabold text-slate-900 block">Citra Satelit</span>
            <div className="h-32 rounded-xl overflow-hidden bg-slate-900 relative border border-slate-200">
              <img
                src={getAssetUrl('/static/uploads/sample_aerial.jpg')}
                alt="Citra Satelit Referensi"
                className="w-full h-full object-cover filter brightness-90 contrast-125"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-2.5">
                <span className="text-[10px] font-mono text-white font-medium">Sentinel-2 • 10m Ground Res</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
