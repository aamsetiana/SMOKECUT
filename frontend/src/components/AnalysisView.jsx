import React, { useState, useRef } from 'react';
import {
  Upload,
  Flame,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Layers,
  Wind,
  CheckCircle,
  Loader2,
  Image as ImageIcon
} from 'lucide-react';
import { uploadMedia, runAnalysis, getAssetUrl, formatCuttingLength } from '../services/api';

export default function AnalysisView({ onAnalysisCompleted, initialData, onNavigateToHistory }) {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(initialData || null);
  const [windDirection, setWindDirection] = useState(135);
  const [windSpeed, setWindSpeed] = useState(14);
  const [firebreakWidth, setFirebreakWidth] = useState(4);
  const [safetyBuffer, setSafetyBuffer] = useState(35);
  const [activeLayer, setActiveLayer] = useState('all'); // 'all', 'vari', 'firebreak', 'detections'
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const samplePresets = [
    { id: 'sample', title: 'Sampel Udara 1', desc: 'Area Semak Kering Kuningan', tag: 'Hotspot Terdeteksi' },
    { id: 'sample2', title: 'Sampel Udara 2', desc: 'Koridor Ilalang Rawan', tag: 'Bahan Bakar Kering' },
    { id: 'sample3', title: 'Sampel Udara 3', desc: 'Perbatasan Pemukiman', tag: 'Prioritas Sekat' },
  ];

  const processFile = async (file) => {
    if (!file) return;
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));

    // Upload to backend
    try {
      setLoading(true);
      const uploadRes = await uploadMedia(file);
      await triggerAnalysis(uploadRes.image_id);
    } catch (err) {
      alert(`Gagal upload: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    processFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const triggerAnalysis = async (imageId = 'sample') => {
    setLoading(true);
    try {
      const res = await runAnalysis({
        image_id: imageId,
        wind_direction: Number(windDirection),
        wind_speed: Number(windSpeed),
        firebreak_width: Number(firebreakWidth),
        safety_buffer: Number(safetyBuffer),
      });
      setAnalysisResult(res);
      if (onAnalysisCompleted) onAnalysisCompleted(res);
    } catch (err) {
      console.error(err);
      alert(`Analisis gagal: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Metrics from result or fallback to consistent baseline figures
  const dryPercent = analysisResult?.vari_analysis?.dry_fuel_percentage
    ? `${analysisResult.vari_analysis.dry_fuel_percentage.toFixed(1)}%`
    : '66.2%';
  const safePercent = analysisResult?.vari_analysis?.safe_vegetation_percentage
    ? `${analysisResult.vari_analysis.safe_vegetation_percentage.toFixed(1)}%`
    : '33.7%';
  const cuttingMeters = formatCuttingLength(analysisResult?.summary?.cutting_length_meters);

  return (
    <div className="space-y-6">
      {/* Main Grid: Upload & Controls on Left, Visualizer on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Upload Dropzone with Drag and Drop Support */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragEnter={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-200 cursor-pointer group shadow-sm ${isDragging
              ? 'border-emerald-500 bg-emerald-50/70 scale-[1.01] ring-2 ring-emerald-500/30'
              : 'border-slate-300 hover:border-emerald-500 bg-white'
              }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.mp4"
              className="hidden"
            />
            <div
              className={`w-12 h-12 rounded-2xl mx-auto flex items-center justify-center transition mb-3 ${isDragging
                ? 'bg-emerald-600 text-white animate-bounce shadow-md shadow-emerald-600/30'
                : 'bg-emerald-50 group-hover:bg-emerald-100 text-emerald-600'
                }`}
            >
              <Upload className="w-6 h-6" />
            </div>
            <p className="text-xs font-bold text-slate-900">
              {isDragging ? 'Lepaskan file di sini' : 'Upload Gambar / Video'}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              {isDragging ? 'File akan langsung dianalisis otomatis' : 'Drag & drop atau pilih file'}
            </p>
          </div>

          {/* Contoh Sampel */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2.5 shadow-sm">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Contoh Sampel</span>
            <div className="grid grid-cols-3 gap-2">
              {samplePresets.map((sample, idx) => (
                <button
                  key={sample.id}
                  onClick={() => triggerAnalysis('sample')}
                  className={`p-2 rounded-xl border text-left transition flex flex-col justify-between ${idx === 0
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                    : 'bg-slate-50 border-slate-200 hover:border-emerald-300 text-slate-700'
                    }`}
                >
                  <div className="h-10 rounded-lg bg-slate-200 flex items-center justify-center mb-1.5 overflow-hidden">
                    <img
                      src={getAssetUrl('/static/uploads/sample_aerial.jpg')}
                      alt="Sample"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="text-[10px] font-bold truncate block">{sample.title}</span>
                  <span className="text-[9px] text-slate-500 truncate block">{sample.tag}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Environmental Parameter Sliders */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3.5 shadow-sm">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Parameter Dinamis</span>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600 font-medium">Arah Angin</span>
                <span className="text-emerald-700 font-bold">{windDirection}° (Tenggara)</span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                value={windDirection}
                onChange={(e) => setWindDirection(Number(e.target.value))}
                className="w-full accent-emerald-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600 font-medium">Kecepatan Angin</span>
                <span className="text-emerald-700 font-bold">{windSpeed} Km/jam</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                value={windSpeed}
                onChange={(e) => setWindSpeed(Number(e.target.value))}
                className="w-full accent-emerald-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <span className="text-slate-600 text-xs block mb-1.5 font-medium">Lebar Sekat Bakar</span>
              <div className="grid grid-cols-3 gap-2">
                {[3, 4, 5].map((w) => (
                  <button
                    key={w}
                    onClick={() => setFirebreakWidth(w)}
                    className={`py-1.5 rounded-xl text-xs font-bold transition border ${firebreakWidth === w
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                  >
                    {w} Meter
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            onClick={() => triggerAnalysis('sample')}
            disabled={loading}
            className="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Memproses Citra Drone (CV & VARI)...</span>
              </>
            ) : (
              <>
                <span>Mulai Analisis</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Right Column: Visualizer Canvas & Hasil Analisis (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Main Visualizer Container */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col relative overflow-hidden min-h-[380px]">
            {/* Top Toolbar: Layer Selector & Badge */}
            <div className="flex items-center justify-between mb-3 z-10">
              <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 p-1 rounded-xl text-xs">
                {[
                  { id: 'all', label: 'Semua Layer' },
                  { id: 'vari', label: 'VARI Heatmap' },
                  { id: 'firebreak', label: 'Sekat Bakar' },
                  { id: 'detections', label: 'Titik Api' },
                ].map((ly) => (
                  <button
                    key={ly.id}
                    onClick={() => setActiveLayer(ly.id)}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${activeLayer === ly.id
                      ? 'bg-white text-emerald-800 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                      }`}
                  >
                    {ly.label}
                  </button>
                ))}
              </div>

              {/* Floating Firebreak Length Pill */}
              <div className="bg-purple-50 border border-purple-200 text-purple-900 px-3 py-1 rounded-xl text-xs font-bold shadow-sm flex items-center gap-1.5">
                <span>Jalur Sekat Bakar</span>
                <span className="text-purple-700 font-black">{cuttingMeters}</span>
              </div>
            </div>

            {/* Canvas View Area */}
            <div className="flex-1 rounded-xl overflow-hidden relative bg-slate-900 border border-slate-200 flex items-center justify-center min-h-[300px]">
              {/* Original Aerial Base Image */}
              <img
                src={previewUrl || getAssetUrl('/static/uploads/sample_aerial.jpg')}
                alt="Analisis Visual"
                className="w-full h-full object-cover"
              />

              {/* Overlays */}
              <div className="absolute inset-0 pointer-events-none mix-blend-screen">
                {(activeLayer === 'all' || activeLayer === 'vari') && (
                  <div className="w-full h-full bg-gradient-to-tr from-red-600/35 via-amber-500/30 to-emerald-600/25" />
                )}

                {(activeLayer === 'all' || activeLayer === 'detections') && (
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                    <div className="w-7 h-7 rounded-full bg-rose-600 border-2 border-white flex items-center justify-center text-white shadow-lg animate-bounce">
                      <Flame className="w-4 h-4" />
                    </div>
                  </div>
                )}

                {(activeLayer === 'all' || activeLayer === 'firebreak') && (
                  <svg className="absolute inset-0 w-full h-full">
                    <path
                      d="M 120 320 Q 280 180 440 200 T 650 260"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth="4"
                      strokeDasharray="9 6"
                      className="drop-shadow-[0_0_8px_rgba(255,255,255,0.9)]"
                    />
                  </svg>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Hasil Analisis Stats (3 Cards) */}
          <div className="space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Hasil Analisis</span>
            <div className="grid grid-cols-3 gap-3">
              {/* Zona Bahaya */}
              <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex items-center gap-3 shadow-sm">
                <div className="w-10 h-10 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 shrink-0">
                  <Flame className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold block">Zona Bahaya</span>
                  <span className="text-base font-black text-rose-600">{dryPercent}</span>
                </div>
              </div>

              {/* Zona Aman */}
              <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex items-center gap-3 shadow-sm">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shrink-0">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold block">Zona Aman</span>
                  <span className="text-base font-black text-emerald-700">{safePercent}</span>
                </div>
              </div>

              {/* Risiko PM2.5 */}
              <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex items-center gap-3 shadow-sm">
                <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 shrink-0">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold block">Risiko PM2.5</span>
                  <span className="text-base font-black text-amber-600">Waspada</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
