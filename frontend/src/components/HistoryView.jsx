import React from 'react';
import { Download, Eye } from 'lucide-react';
import { normalizeRiskLevel, formatCuttingLength, NO_DATA } from '../services/api';

const RISK_COLOR = {
  Bahaya: 'bg-rose-100 text-rose-800 border border-rose-300',
  Waspada: 'bg-amber-100 text-amber-900 border border-amber-300',
  Aman: 'bg-emerald-100 text-emerald-800 border border-emerald-300',
};

// Quote every cell and neutralise spreadsheet formulas in file names
const csvCell = (value) => `"${String(value).replace(/^([=+\-@])/, "'$1").replace(/"/g, '""')}"`;

export default function HistoryView({ history, onViewDetail }) {
  const rows = history.map((item) => ({
    item,
    date: new Date(item.time).toLocaleString('id-ID'),
    risk: normalizeRiskLevel(item.analysis.summary.risk_level) || NO_DATA,
    length: formatCuttingLength(item.analysis),
    hotspots: item.analysis.summary.hotspots_detected,
  }));

  const handleExport = () => {
    const lines = [['Tanggal', 'Citra', 'Risiko', 'Panjang Sekat', 'Titik/Garis Api']]
      .concat(rows.map((r) => [r.date, r.item.name, r.risk, r.length, r.hotspots]))
      .map((cells) => cells.map(csvCell).join(','));
    const url = URL.createObjectURL(new Blob(['﻿' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'riwayat_analisis_smokecut.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        <button
          onClick={handleExport}
          disabled={!rows.length}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-xs font-bold text-slate-700 hover:text-emerald-700 transition shadow-sm disabled:opacity-50"
        >
          <Download className="w-3.5 h-3.5 text-emerald-600" />
          <span>Export Data</span>
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl overflow-x-auto shadow-sm">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-50">
              <th className="py-3.5 px-5">Tanggal & Waktu</th>
              <th className="py-3.5 px-5">Citra</th>
              <th className="py-3.5 px-5">Risiko</th>
              <th className="py-3.5 px-5">Panjang Sekat</th>
              <th className="py-3.5 px-5">Api</th>
              <th className="py-3.5 px-5 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {!rows.length && (
              <tr><td colSpan={6} className="py-8 text-center text-slate-500">Belum ada analisis di browser ini.</td></tr>
            )}
            {rows.map(({ item, date, risk, length, hotspots }) => (
              <tr key={item.time} className="hover:bg-slate-50/80 transition">
                <td className="py-4 px-5 text-slate-900 font-medium">{date}</td>
                <td className="py-4 px-5 text-slate-700">{item.name}</td>
                <td className="py-4 px-5">
                  <span className={`inline-block px-3 py-0.5 rounded-full text-[10px] font-bold ${RISK_COLOR[risk] || ''}`}>{risk}</span>
                </td>
                <td className="py-4 px-5 text-slate-700">{length}</td>
                <td className="py-4 px-5 text-slate-700">{hotspots}</td>
                <td className="py-4 px-5 text-right">
                  <button
                    onClick={() => onViewDetail(item)}
                    className="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-600 hover:text-emerald-700 border border-slate-200 transition shadow-sm"
                    title="Lihat Detail Analisis"
                  >
                    <Eye className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
