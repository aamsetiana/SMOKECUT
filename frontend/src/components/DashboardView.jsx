import React, { useState } from 'react';
import { Flame, ShieldCheck, Spline, CloudFog, Wind, Compass, AlertTriangle, ArrowRight, Layers } from 'lucide-react';
import {
  normalizeRiskLevel, formatCuttingLength, formatNumber, formatPercent, formatWind, NO_DATA,
} from '../services/api';
import LayerViewer from './LayerViewer';

const RISK = {
  Bahaya: {
    text: 'text-rose-600', bar: 'bg-rose-500 w-full', icon: 'bg-rose-50 border-rose-200 text-rose-600',
  },
  Waspada: {
    text: 'text-amber-600', bar: 'bg-amber-500 w-2/3', icon: 'bg-amber-50 border-amber-200 text-amber-600',
  },
  Aman: {
    text: 'text-emerald-600', bar: 'bg-emerald-500 w-1/3', icon: 'bg-emerald-50 border-emerald-200 text-emerald-600',
  },
};
const NO_RISK = { text: 'text-slate-500', bar: 'w-0', icon: 'bg-slate-50 border-slate-200 text-slate-400' };

function StatCard({ label, value, note, Icon, valueClass = 'text-slate-900', noteClass, iconClass, children }) {
  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-4 flex items-center justify-between gap-2 transition-all shadow-sm hover:shadow-md">
      <div className="space-y-1 min-w-0">
        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</span>
        <div className={`${value === NO_DATA ? 'text-sm text-slate-400' : `text-xl ${valueClass}`} font-black`}>{value}</div>
        {note && <p className={`text-[10px] font-semibold ${noteClass}`}>{note}</p>}
        {children}
      </div>
      <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center shrink-0 shadow-sm ${iconClass}`}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
  );
}

export default function DashboardView({ analysisData, sourceName, onNavigateToAnalysis }) {
  const [showOverlays, setShowOverlays] = useState(true);
  const summary = analysisData?.summary;
  const wind = analysisData?.firebreak_plan?.wind;
  const riskLevel = normalizeRiskLevel(summary?.risk_level);
  const risk = RISK[riskLevel] || NO_RISK;
  const notes = summary?.penjelasan_lapangan;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Tingkat Risiko" value={riskLevel || NO_DATA} valueClass={risk.text} Icon={Flame} iconClass={risk.icon}>
          <div className="w-28 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-2">
            <div className={`h-full rounded-full transition-all duration-500 ${risk.bar}`} />
          </div>
        </StatCard>
        <StatCard
          label="Lahan Terlindungi" value={formatNumber(summary?.protected_hectares, 'ha', 2)}
          note={`Vegetasi lembap: ${formatPercent(analysisData?.vari_analysis?.safe_vegetation_percentage)}`}
          noteClass="text-emerald-600" Icon={ShieldCheck} iconClass="bg-emerald-50 border-emerald-200 text-emerald-600"
        />
        <StatCard
          label="Panjang Sekat" value={formatCuttingLength(analysisData)}
          note={summary ? `Lebar ${formatNumber(summary.recommended_width_meters, 'm')} (Permen LHK 28/2021)` : null}
          noteClass="text-purple-600" Icon={Spline} iconClass="bg-purple-50 border-purple-200 text-purple-600"
        />
        <StatCard
          label="Area Asap" value={summary ? `${summary.smoke_detected} area` : NO_DATA}
          note="PM2.5 tidak diukur" noteClass="text-slate-400"
          Icon={CloudFog} iconClass="bg-amber-50 border-amber-200 text-amber-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col min-h-[470px]">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <span className="text-xs font-bold text-slate-700">{sourceName || 'Belum ada citra'}</span>
            {analysisData && !analysisData.video_url && (
              <button
                onClick={() => setShowOverlays(!showOverlays)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border transition shadow-sm ${showOverlays
                  ? 'bg-emerald-50 border-emerald-400 text-emerald-800'
                  : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'
                  }`}
              >
                <Layers className="w-3.5 h-3.5 text-emerald-600" />
                <span>{showOverlays ? 'Overlay Aktif' : 'Citra Polos'}</span>
              </button>
            )}
          </div>
          <LayerViewer
            analysis={analysisData}
            layers={showOverlays ? ['vari', 'detections', 'firebreak', 'tactical'] : []}
          />
          <div className="flex flex-wrap gap-x-5 gap-y-1.5 mt-3 text-[11px] font-semibold text-slate-700">
            {!analysisData?.video_url && (
              <>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-rose-500" />Semak kering</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-amber-400" />Sedang</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-500" />Lembap</span>
              </>
            )}
            <span className="flex items-center gap-1.5"><span className="w-5 h-1.5 bg-yellow-400 border border-slate-800" />Sekat bakar</span>
            <span className="flex items-center gap-1.5"><Flame className="w-3.5 h-3.5 text-rose-500" />Garis api</span>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Angin</h3>
            <div className="flex items-start gap-2 text-xs font-bold text-slate-900">
              <Wind className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{formatWind(wind)}</span>
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-600">
              <Compass className="w-4 h-4 text-slate-400 shrink-0" />
              <span>Jarak aman tim: <b>{formatNumber(summary?.effective_safety_buffer_meters, 'm')}</b></span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-emerald-50 via-white to-green-50/70 border border-emerald-200 rounded-2xl p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-emerald-800 font-extrabold text-xs">
              <AlertTriangle className="w-4 h-4 text-emerald-600" />
              <span>Ringkasan Lapangan</span>
            </div>
            {notes ? (
              <ul className="text-xs text-slate-700 leading-relaxed font-medium list-disc pl-4 space-y-1">
                <li>{summary.risk_description}</li>
                <li>{notes.deteksi_bahaya}</li>
                <li>{notes.instruksi_babat}</li>
                <li>{notes.jarak_aman}</li>
              </ul>
            ) : (
              <p className="text-xs text-slate-600">{NO_DATA}</p>
            )}
            <button
              onClick={onNavigateToAnalysis}
              className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition"
            >
              <span>{analysisData ? 'Lihat Detail' : 'Mulai Analisis'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
