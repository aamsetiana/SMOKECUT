import React, { useEffect, useState } from 'react';
import { Users, AlertTriangle, ArrowRight, Loader2, MessageSquare } from 'lucide-react';
import { dispatchWhatsApp } from '../services/api';

export default function NotificationsView({ analysisData, onOpenDispatchModal }) {
  const [dispatches, setDispatches] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setDispatches([]);
    setError('');
    if (!analysisData) return undefined;
    let active = true;
    setLoading(true);
    dispatchWhatsApp(analysisData)
      .then((res) => active && setDispatches(res.dispatches))
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [analysisData]);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shadow-sm">
          <MessageSquare className="w-7 h-7" />
        </div>
        <div>
          <h3 className="text-base font-extrabold text-slate-900">Kirim Notifikasi Melalui WhatsApp</h3>
          <p className="text-xs text-slate-500 font-medium">Pesan disusun dari hasil analisis terakhir</p>
        </div>
      </div>

      {!analysisData && <p className="text-xs text-slate-600">Belum ada analisis, jadi belum ada pesan untuk dikirim.</p>}
      {loading && <Loader2 className="w-5 h-5 animate-spin text-emerald-600" />}
      {error && <p role="alert" className="text-xs text-rose-700 font-semibold">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dispatches.map((item, idx) => {
          const Icon = idx === 0 ? Users : AlertTriangle;
          return (
            <div key={item.recipient_group} className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-slate-900">{item.recipient_group}</span>
              </div>
              <p className="text-xs text-slate-800 leading-relaxed bg-white p-3 rounded-xl border border-slate-200 whitespace-pre-wrap break-words select-text">
                {item.message_text}
              </p>
            </div>
          );
        })}
      </div>

      <button
        onClick={() => onOpenDispatchModal(dispatches)}
        disabled={!dispatches.length}
        className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition disabled:opacity-50"
      >
        <span>Buat Pesan</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
