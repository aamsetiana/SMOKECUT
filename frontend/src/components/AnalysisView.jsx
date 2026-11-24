import React, { useState, useRef } from 'react';
import { Upload, Flame, ShieldCheck, CloudFog, ArrowRight, Loader2, Image as ImageIcon, Video } from 'lucide-react';
import { uploadMedia, runAnalysis, formatCuttingLength, formatPercent, formatNumber, NO_DATA } from '../services/api';
import FieldDataForm from './FieldDataForm';
import LayerViewer from './LayerViewer';
import WarningList from './WarningList';

const SAMPLES = [
  { id: 'sample', title: 'Foto Demo', tag: 'Citra sintetis', Icon: ImageIcon },
  { id: 'sample_video', title: 'Video Demo', tag: 'Citra sintetis', Icon: Video },
];

const LAYER_TABS = [
  { id: 'all', label: 'Semua Layer', layers: ['vari', 'detections', 'firebreak', 'tactical'] },
  { id: 'vari', label: 'VARI Heatmap', layers: ['vari'] },
  { id: 'firebreak', label: 'Sekat Bakar', layers: ['firebreak'] },
  { id: 'detections', label: 'Api & Asap', layers: ['detections'] },
  { id: 'map', label: 'Peta Cetak', layers: ['map'] },
];
// Detections and firebreak are part of the video itself, so separate toggles would do nothing
const VIDEO_TABS = ['all', 'map'];

export default function AnalysisView({ analysis, fieldData, setFieldData, source, setSource, onAnalysisCompleted }) {
  const [progress, setProgress] = useState('');
  const [error, setError] = useState('');
  const [activeLayer, setActiveLayer] = useState('all');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const loading = progress !== '';

  const run = async (getSource) => {
    if (loading) return;
    setError('');
    try {
      const next = await getSource();
      setSource(next);
      setProgress('Menganalisis (video bisa sampai 1 menit)...');
      onAnalysisCompleted(await runAnalysis(next.id, fieldData), next.name);
    } catch (err) {
      setError(err.message === 'Failed to fetch' ? 'Backend tidak dapat dihubungi.' : err.message);
    } finally {
      setProgress('');
    }
  };

  const analyzeFile = (file) => {
    if (!file) return;
    run(async () => {
      setProgress('Mengunggah...');
      return { id: (await uploadMedia(file)).image_id, name: file.name };
    });
  };

  const analyzeSource = (src) => run(async () => src);

  const setDrag = (dragging) => (e) => {
    e.preventDefault();
    setIsDragging(dragging);
  };

  const isVideo = Boolean(analysis?.video_url);
  const tabs = LAYER_TABS.filter((t) => !isVideo || VIDEO_TABS.includes(t.id));
  const tab = tabs.find((t) => t.id === activeLayer) || tabs[0];
  const summary = analysis?.summary;

  const results = [
    {
      label: 'Semak Kering', Icon: Flame, value: formatPercent(analysis?.vari_analysis?.dry_fuel_percentage),
      text: 'text-rose-600', box: 'bg-rose-50 border-rose-200 text-rose-600',
    },
    {
      label: 'Vegetasi Lembap', Icon: ShieldCheck, value: formatPercent(analysis?.vari_analysis?.safe_vegetation_percentage),
      text: 'text-emerald-700', box: 'bg-emerald-50 border-emerald-200 text-emerald-600',
    },
    {
      label: 'Api / Area Asap', Icon: CloudFog,
      value: summary ? `${summary.hotspots_detected} / ${summary.smoke_detected}` : NO_DATA,
      text: 'text-amber-600', box: 'bg-amber-50 border-amber-200 text-amber-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-5 space-y-4">
        <div
          onClick={() => !loading && fileInputRef.current?.click()}
          onDragOver={setDrag(true)}
          onDragEnter={setDrag(true)}
          onDragLeave={setDrag(false)}
          onDrop={(e) => {
            setDrag(false)(e);
            analyzeFile(e.dataTransfer?.files?.[0]);
          }}
          className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-200 cursor-pointer group shadow-sm ${isDragging
            ? 'border-emerald-500 bg-emerald-50/70 scale-[1.01] ring-2 ring-emerald-500/30'
            : 'border-slate-300 hover:border-emerald-500 bg-white'
            }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              analyzeFile(e.target.files?.[0]);
              e.target.value = '';
            }}
            accept=".jpg,.jpeg,.png,.mp4,.mov,.avi"
            className="hidden"
          />
          <div className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center transition mb-3 bg-emerald-50 group-hover:bg-emerald-100 text-emerald-600">
            <Upload className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-900">
            {isDragging ? 'Lepaskan file di sini' : 'Upload Gambar / Video'}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            {source ? `Aktif: ${source.name}` : 'Drag & drop atau pilih file'}
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2.5 shadow-sm">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Contoh Sampel</span>
          <div className="grid grid-cols-2 gap-2">
            {SAMPLES.map(({ id, title, tag, Icon }) => (
              <button
                key={id}
                disabled={loading}
                onClick={() => analyzeSource({ id, name: title })}
                className={`p-2.5 rounded-xl border text-left transition flex items-center gap-2.5 disabled:opacity-50 ${source?.id === id
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                  : 'bg-slate-50 border-slate-200 hover:border-emerald-300 text-slate-700'
                  }`}
              >
                <Icon className="w-5 h-5 text-emerald-600 shrink-0" />
                <span>
                  <span className="text-[11px] font-bold block">{title}</span>
                  <span className="text-[10px] text-slate-500 block">{tag}</span>
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3 shadow-sm">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Data Lapangan</span>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Isi dari hasil ukur; kolom kosong tidak ditebak. Foto DJI tegak lurus mengisi skala dan GPS otomatis.
            </p>
          </div>
          <FieldDataForm value={fieldData} onChange={setFieldData} />
        </div>

        {error && (
          <p role="alert" className="text-xs font-semibold text-rose-700 bg-rose-50 border border-rose-200 rounded-xl p-3">
            {error}
          </p>
        )}

        <button
          onClick={() => analyzeSource(source)}
          disabled={loading || !source}
          className="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          <span>{progress || (source ? 'Mulai Analisis' : 'Pilih foto/video dahulu')}</span>
          {!loading && source ? <ArrowRight className="w-4 h-4" /> : null}
        </button>
      </div>

      <div className="lg:col-span-7 space-y-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col min-h-[380px]">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 border border-slate-200 p-1 rounded-xl">
              {tabs.map((ly) => (
                <button
                  key={ly.id}
                  onClick={() => setActiveLayer(ly.id)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${tab.id === ly.id
                    ? 'bg-white text-emerald-800 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                    }`}
                >
                  {ly.id === 'all' && isVideo ? 'Video + Sekat' : ly.label}
                </button>
              ))}
            </div>
            <div className="bg-purple-50 border border-purple-200 text-purple-900 px-3 py-1 rounded-xl text-xs font-bold shadow-sm flex items-center gap-1.5">
              <span>Panjang sekat</span>
              <span className="text-purple-700 font-black">{formatCuttingLength(analysis)}</span>
            </div>
          </div>
          <LayerViewer analysis={analysis} layers={tab.layers} />
        </div>

        <div className="space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
            Hasil Analisis{summary ? ` • lebar sekat ${formatNumber(summary.recommended_width_meters, 'm')}` : ''}
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {results.map(({ label, Icon, value, text, box }) => (
              <div key={label} className="bg-white border border-slate-200 rounded-2xl p-3.5 flex items-center gap-3 shadow-sm">
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center shrink-0 ${box}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold block">{label}</span>
                  <span className={`text-base font-black ${text}`}>{value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <WarningList analysis={analysis} />
      </div>
    </div>
  );
}
