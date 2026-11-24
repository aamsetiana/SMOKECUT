import React from 'react';
import {
  Spline,
  Shield,
  Compass,
  Clock,
  Layers,
  MapPin,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { getAssetUrl } from '../services/api';

export default function FirebreakView({ analysisData, onNavigateToAnalysis }) {
  const metrics = analysisData?.summary || {
    cutting_length_meters: 3800,
    recommended_width_meters: 4.0,
    clearing_time_hours: 3.1,
    protected_hectares: 2.45,
    effective_safety_buffer_meters: 35.0,
  };

  const coordinates = [
    { seq: 'WP-01', lat: '-7.12340', lng: '110.56780', desc: 'Titik Awal (Batas Jalan Setapak Barat)' },
    { seq: 'WP-02', lat: '-7.12410', lng: '110.56890', desc: 'Simpang Parit Alami / Zona Buffer' },
    { seq: 'WP-03', lat: '-7.12530', lng: '110.57020', desc: 'Puncak Punggung Bukit (Titik Kritis)' },
    { seq: 'WP-04', lat: '-7.12650', lng: '110.57140', desc: 'Batas Vegetasi Basah Timur' },
  ];

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 block mb-1 uppercase tracking-wider">Panjang Babatan Total</span>
          <span className="text-xl font-black text-slate-900">
            {(metrics.cutting_length_meters / 1000).toFixed(1)} Km
          </span>
          <p className="text-[10px] text-slate-400 mt-1 font-medium">Mengikuti kontur hambatan alami</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 block mb-1 uppercase tracking-wider">Lebar Babatan Rekomendasi</span>
          <span className="text-xl font-black text-emerald-600">
            {metrics.recommended_width_meters} Meter
          </span>
          <p className="text-[10px] text-slate-400 mt-1 font-medium">Cegah loncatan bara api (*spotting*)</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 block mb-1 uppercase tracking-wider">Estimasi Waktu Pengerjaan</span>
          <span className="text-xl font-black text-slate-900">
            {metrics.clearing_time_hours} Jam
          </span>
          <p className="text-[10px] text-slate-400 mt-1 font-medium">Regu 6 orang MPA dengan parang & cangkul</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 block mb-1 uppercase tracking-wider">Safety Buffer Personel</span>
          <span className="text-xl font-black text-emerald-600">
            {metrics.effective_safety_buffer_meters} Meter
          </span>
          <p className="text-[10px] text-slate-400 mt-1 font-medium">Jarak aman regu pembabat dari garis api</p>
        </div>
      </div>

      {/* Grid: Map Preview & GPS Waypoint Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Map Preview */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col min-h-[360px]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <Spline className="w-4 h-4 text-purple-600" />
              <span>Overlay Jalur Sekat Bakar</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">
              3–5 Meter Buffer
            </span>
          </div>

          <div className="flex-1 rounded-xl overflow-hidden relative bg-slate-900 border border-slate-200 flex items-center justify-center">
            <img
              src={getAssetUrl('/static/uploads/sample_aerial.jpg')}
              alt="Jalur Sekat Bakar"
              className="w-full h-full object-cover"
            />
            {/* SVG Firebreak Trajectory */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <path
                d="M 80 340 Q 240 160 400 180 T 600 240"
                fill="none"
                stroke="#A855F7"
                strokeWidth="5"
                strokeDasharray="10 6"
                className="drop-shadow-[0_0_10px_rgba(168,85,247,0.8)]"
              />
            </svg>
          </div>
        </div>

        {/* GPS Waypoints List */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col justify-between">
          <div>
            <span className="text-xs font-extrabold text-slate-900 block mb-3">Koordinat GPS Lapangan (Waypoints)</span>
            <div className="space-y-2.5">
              {coordinates.map((wp) => (
                <div key={wp.seq} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                  <div className="px-2 py-1 rounded bg-emerald-100 text-[10px] font-mono font-black text-emerald-800 border border-emerald-200">
                    {wp.seq}
                  </div>
                  <div className="flex-1 text-xs">
                    <p className="font-mono text-slate-900 font-bold">{wp.lat}, {wp.lng}</p>
                    <p className="text-[11px] text-slate-500">{wp.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={onNavigateToAnalysis}
            className="w-full mt-4 py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 text-xs font-bold flex items-center justify-center gap-2 transition"
          >
            <span>Hitung Ulang Berdasarkan Citra Baru</span>
          </button>
        </div>
      </div>
    </div>
  );
}
