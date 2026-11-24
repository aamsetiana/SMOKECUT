import React, { useState } from 'react';
import { Wind, ChevronDown } from 'lucide-react';
import { formatNumber, formatPercent, formatWind, NO_DATA } from '../services/api';
import LayerViewer from './LayerViewer';

const LAYERS = {
  ALL: { label: 'Komposit Lengkap', layers: ['vari', 'detections', 'firebreak', 'tactical'] },
  VARI: { label: 'VARI', layers: ['vari'] },
  HOTSPOT: { label: 'Api & Asap', layers: ['detections'] },
  FIREBREAK: { label: 'Sekat Bakar', layers: ['firebreak'] },
  MAP: { label: 'Peta Cetak', layers: ['map'] },
};

export default function RiskMapView({ analysisData }) {
  const [selected, setSelected] = useState('MAP');
  const isVideo = Boolean(analysisData?.video_url);
  const ids = Object.keys(LAYERS).filter((id) => !isVideo || id === 'MAP' || id === 'ALL');
  const current = ids.includes(selected) ? selected : 'MAP';
  const vari = analysisData?.vari_analysis;
  const zones = analysisData?.land_mapping?.fuel_zones || [];
  const legend = [
    ['bg-rose-500', 'Kering (VARI ≤ 0,10)', vari?.dry_fuel_percentage],
    ['bg-amber-400', 'Sedang (0,10 – 0,25)', vari?.moderate_percentage],
    ['bg-emerald-500', 'Lembap (VARI > 0,25)', vari?.safe_vegetation_percentage],
  ];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 bg-white border border-emerald-300 px-3.5 py-1.5 rounded-xl text-xs font-bold text-emerald-800 shadow-sm">
          <Wind className="w-4 h-4 text-emerald-600" />
          <span>Angin: {formatWind(analysisData?.firebreak_plan?.wind)}</span>
        </div>
        <div className="relative">
          <select
            aria-label="Layer peta"
            value={current}
            onChange={(e) => setSelected(e.target.value)}
            className="bg-white border border-slate-200 text-xs font-bold text-slate-800 rounded-xl px-3 py-2 pr-8 appearance-none focus:outline-none focus:border-emerald-500 cursor-pointer shadow-sm"
          >
            {ids.map((id) => (
              <option key={id} value={id}>Layer: {id === 'ALL' && isVideo ? 'Video + Sekat' : LAYERS[id].label}</option>
            ))}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-slate-500 absolute right-2.5 top-2.5 pointer-events-none" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-9 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col min-h-[480px]">
          <LayerViewer analysis={analysisData} layers={LAYERS[current].layers} />
        </div>

        <div className="lg:col-span-3 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-3">
            <span className="text-xs font-extrabold text-slate-900 block">Kekeringan Vegetasi</span>
            <div className="space-y-2 text-xs">
              {legend.map(([color, label, value]) => (
                <div key={label} className="flex items-center gap-2.5">
                  <span className={`w-3 h-3 rounded-full shrink-0 ${color}`} />
                  <span className="text-slate-800 font-semibold flex-1">{label}</span>
                  <span className="font-bold text-slate-900">{vari ? formatPercent(value) : '–'}</span>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-slate-400">Persentase dari lahan yang belum terbakar dan tidak tertutup asap.</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-2">
            <span className="text-xs font-extrabold text-slate-900 block">Zona Semak Kering</span>
            {zones.length === 0 && <p className="text-xs text-slate-500">{analysisData ? 'Tidak ada zona besar' : NO_DATA}</p>}
            {zones.slice(0, 5).map((z) => (
              <div key={z.zone_id} className="flex justify-between text-xs">
                <span className="text-slate-600">Zona {z.zone_id}</span>
                <span className="font-bold text-slate-900">{formatNumber(z.area_hectares, 'ha', 2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
