import React, { useState, useEffect } from 'react';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [activeMode, setActiveMode] = useState('preventive'); // 'preventive' or 'quick_response'

  useEffect(() => {
    fetch('http://127.0.0.1:8000/health')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'ok') setBackendStatus('connected');
        else setBackendStatus('error');
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-[#0F172A]/90 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center font-bold text-sky-400">
            SC
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-wide text-white flex items-center gap-2">
              SMOKECUT
              <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 font-medium">
                AIRIMPACT 2026
              </span>
            </h1>
            <p className="text-xs text-slate-400">Smart Drone-Vision untuk Mitigasi Sekat Bakar & Pencegahan Asap PM2.5</p>
          </div>
        </div>

        {/* Operational Mode Toggle & Connection Badge */}
        <div className="flex items-center gap-4">
          <div className="bg-slate-900 border border-slate-700/60 p-1 rounded-lg flex text-xs font-medium">
            <button
              onClick={() => setActiveMode('preventive')}
              className={`px-3 py-1.5 rounded-md transition ${activeMode === 'preventive' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
            >
              Patroli Preventif
            </button>
            <button
              onClick={() => setActiveMode('quick_response')}
              className={`px-3 py-1.5 rounded-md transition ${activeMode === 'quick_response' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
            >
              Respons Cepat
            </button>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <span className={`h-2 w-2 rounded-full ${backendStatus === 'connected' ? 'bg-emerald-400 animate-pulse' : backendStatus === 'offline' ? 'bg-rose-400' : 'bg-amber-400'}`} />
            <span className="text-slate-300 capitalize">Backend: {backendStatus}</span>
          </div>
        </div>
      </header>

      {/* Main Content Dashboard Container */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Media Uploader & Controls */}
        <div className="space-y-6">
          <div className="bg-[#1E293B] border border-slate-700/60 rounded-xl p-5 shadow-lg">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">1. Unggah Citra / Video Udara</h2>
            <div className="border-2 border-dashed border-slate-600 hover:border-sky-500/60 rounded-lg p-6 text-center transition cursor-pointer bg-slate-900/40">
              <div className="text-sky-400 text-3xl mb-2">📸</div>
              <p className="text-sm font-medium text-slate-200">Drag & drop foto (.jpg) atau video (.mp4)</p>
              <p className="text-xs text-slate-400 mt-1">Drone Kamera RGB Biasa (Ketinggian 60–100m)</p>
            </div>
          </div>

          <div className="bg-[#1E293B] border border-slate-700/60 rounded-xl p-5 shadow-lg">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">2. Parameter Lingkungan & Sekat</h2>
            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-300 font-medium block mb-1">Arah Angin (Mata Angin): Tenggara (135°)</label>
                <input type="range" min="0" max="360" defaultValue="135" className="w-full accent-sky-500" />
              </div>
              <div>
                <label className="text-slate-300 font-medium block mb-1">Kecepatan Angin: 14 km/jam</label>
                <input type="range" min="0" max="50" defaultValue="14" className="w-full accent-sky-500" />
              </div>
              <div>
                <label className="text-slate-300 font-medium block mb-1">Lebar Sekat Bakar: 4 Meter</label>
                <div className="grid grid-cols-3 gap-2">
                  {['3 Meter', '4 Meter', '5 Meter'].map((w, idx) => (
                    <button key={idx} className={`py-1.5 rounded border ${idx === 1 ? 'border-sky-500 bg-sky-500/20 text-sky-300 font-bold' : 'border-slate-700 bg-slate-800 text-slate-400'}`}>
                      {w}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Center & Right Column: Aerial Visualizer & Action Card */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#1E293B] border border-slate-700/60 rounded-xl p-5 shadow-lg min-h-[420px] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-4">
              <div>
                <h2 className="text-sm font-semibold text-white">Visualizer Multi-Layer Drone</h2>
                <p className="text-xs text-slate-400">Analisis VARI, Deteksi Asap/Api, dan Rekomendasi Garis Sekat Bakar</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Ready for Input
                </span>
              </div>
            </div>

            <div className="flex-1 bg-slate-950/60 rounded-lg border border-slate-800 flex flex-col items-center justify-center p-8 text-center">
              <div className="text-4xl text-slate-600 mb-3">🛰️</div>
              <p className="text-slate-300 font-medium">Belum Ada Citra yang Dianalisis</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Unggah video atau foto drone udara untuk menjalankan algoritma VARI dan kalkulasi rute pemotongan api.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-[#0F172A] px-6 py-3 text-xs text-slate-500 flex justify-between items-center">
        <span>SMOKECUT — Cegah Api Melebar, Jaga Napas Warga.</span>
        <span>Kompetisi AIRIMPACT 2026 (MarkPlus, Inc.)</span>
      </footer>
    </div>
  );
}
