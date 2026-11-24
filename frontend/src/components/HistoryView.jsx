import React from 'react';
import {
  Download,
  Eye,
  Calendar,
  MapPin,
  Flame,
  CheckCircle,
  FileSpreadsheet
} from 'lucide-react';

export default function HistoryView({ onViewDetail }) {
  const historyItems = [
    {
      id: 'REC-001',
      date: '29 Nov 2026, 14:20 WIB',
      location: 'Kuningan, Jawa Barat',
      risk: 'Bahaya',
      riskColor: 'bg-rose-100 text-rose-800 border border-rose-300 font-bold',
      firebreak: '3.8 km',
      hotspots: 1,
    },
    {
      id: 'REC-002',
      date: '29 Nov 2026, 11:45 WIB',
      location: 'Kuningan, Jawa Barat',
      risk: 'Waspada',
      riskColor: 'bg-amber-100 text-amber-900 border border-amber-300 font-bold',
      firebreak: '2.1 km',
      hotspots: 0,
    },
    {
      id: 'REC-003',
      date: '28 Nov 2026, 16:30 WIB',
      location: 'Kuningan, Jawa Barat',
      risk: 'Aman',
      riskColor: 'bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold',
      firebreak: '0.0 km',
      hotspots: 0,
    },
    {
      id: 'REC-004',
      date: '28 Nov 2026, 09:15 WIB',
      location: 'Ciremai Utara, Jawa Barat',
      risk: 'Bahaya',
      riskColor: 'bg-rose-100 text-rose-800 border border-rose-300 font-bold',
      firebreak: '4.2 km',
      hotspots: 2,
    },
  ];

  const handleExport = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      'ID,Tanggal,Lokasi,Risiko,PanjangSekat,Hotspot\n' +
      historyItems
        .map((r) => `${r.id},"${r.date}","${r.location}",${r.risk},${r.firebreak},${r.hotspots}`)
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'riwayat_analisis_smokecut.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-end">
        <button
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-xs font-bold text-slate-700 hover:text-emerald-700 transition shadow-sm"
        >
          <Download className="w-3.5 h-3.5 text-emerald-600" />
          <span>Export Data</span>
        </button>
      </div>

      {/* History Table Container (White & Green Theme) */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-50">
                <th className="py-3.5 px-5">Tanggal & Waktu</th>
                <th className="py-3.5 px-5">Lokasi</th>
                <th className="py-3.5 px-5">Risiko</th>
                <th className="py-3.5 px-5 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {historyItems.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-4 px-5 text-slate-900 font-medium">
                    {item.date}
                  </td>
                  <td className="py-4 px-5 text-slate-700">
                    {item.location}
                  </td>
                  <td className="py-4 px-5">
                    <span className={`inline-block px-3 py-0.5 rounded-full text-[10px] ${item.riskColor}`}>
                      {item.risk}
                    </span>
                  </td>
                  <td className="py-4 px-5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={onViewDetail}
                        className="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-600 hover:text-emerald-700 border border-slate-200 transition shadow-sm"
                        title="Lihat Detail Analisis"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={handleExport}
                        className="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-600 hover:text-emerald-700 border border-slate-200 transition shadow-sm"
                        title="Unduh Laporan"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
