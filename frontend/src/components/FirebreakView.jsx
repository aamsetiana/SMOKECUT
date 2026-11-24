import React from 'react';
import { Spline } from 'lucide-react';
import { formatCuttingLength, formatNumber, NO_DATA } from '../services/api';
import LayerViewer from './LayerViewer';
import WarningList from './WarningList';

export default function FirebreakView({ analysisData, onNavigateToAnalysis }) {
  const summary = analysisData?.summary;
  const plan = analysisData?.firebreak_plan;
  const gps = plan?.gps_coordinates;
  const waypoints = [
    { seq: 'A', point: gps?.start, desc: 'Titik mulai' },
    { seq: 'B', point: gps?.end, desc: 'Titik selesai' },
  ];
  const cards = [
    { label: 'Panjang Sekat', value: formatCuttingLength(analysisData), note: 'Dihitung bila skala diketahui' },
    { label: 'Lebar Sekat', value: formatNumber(summary?.recommended_width_meters, 'm'), note: 'Permen LHK 28/2021', green: true },
    { label: 'Jarak Aman Tim', value: formatNumber(summary?.effective_safety_buffer_meters, 'm'), note: 'USFS: 8 × faktor × tinggi vegetasi', green: true },
    { label: 'Lahan Terlindungi', value: formatNumber(summary?.protected_hectares, 'ha', 2), note: 'Bahan bakar di luar sekat' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(({ label, value, note, green }) => (
          <div key={label} className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <span className="text-[11px] font-bold text-slate-500 block mb-1 uppercase tracking-wider">{label}</span>
            <span className={`font-black ${value === NO_DATA ? 'text-sm text-slate-400' : `text-xl ${green ? 'text-emerald-600' : 'text-slate-900'}`}`}>
              {value}
            </span>
            <p className="text-[10px] text-slate-400 mt-1 font-medium">{note}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col min-h-[360px]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <Spline className="w-4 h-4 text-purple-600" />
              <span>Peta Jalur Sekat Bakar</span>
            </span>
            {plan && (
              <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">
                {plan.is_to_scale ? 'Sesuai skala' : 'Ilustrasi, bukan skala'}
              </span>
            )}
          </div>
          <LayerViewer analysis={analysisData} layers={['map']} />
        </div>

        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <span className="text-xs font-extrabold text-slate-900 block mb-3">Koordinat GPS Sekat</span>
            <div className="space-y-2.5">
              {waypoints.map(({ seq, point, desc }) => (
                <div key={seq} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                  <div className="px-2 py-1 rounded bg-emerald-100 text-[10px] font-mono font-black text-emerald-800 border border-emerald-200">{seq}</div>
                  <div className="flex-1 text-xs">
                    <p className="font-mono text-slate-900 font-bold">
                      {point ? `${point.latitude}, ${point.longitude}` : NO_DATA}
                    </p>
                    <p className="text-[11px] text-slate-500">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={onNavigateToAnalysis}
              className="w-full mt-4 py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 text-xs font-bold transition"
            >
              Ubah Data Lapangan / Citra
            </button>
          </div>

          {plan?.standards && (
            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm text-xs text-slate-700">
              <span className="font-extrabold text-slate-900 block mb-2">Aturan Pembersihan</span>
              <ul className="list-disc pl-4 space-y-1">
                {plan.standards.aturan_pembersihan.map((rule) => <li key={rule}>{rule}</li>)}
              </ul>
              <span className="font-extrabold text-slate-900 block mt-3 mb-1">Sumber</span>
              <ul className="space-y-1">
                {Object.entries(plan.standards.sumber).map(([key, s]) => (
                  <li key={key}>
                    <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-emerald-700 underline">{s.judul}</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
      <WarningList analysis={analysisData} />
    </div>
  );
}
