import React, { useState } from 'react';
import { X, Send, Copy, Check, ExternalLink, Loader2 } from 'lucide-react';
import { dispatchWhatsApp } from '../services/api';

export default function WhatsAppModal({ isOpen, onClose, currentAnalysis }) {
  if (!isOpen) return null;

  const [recipientGroup, setRecipientGroup] = useState('mpa'); // 'mpa' or 'residents'
  const [phone, setPhone] = useState('6281234567890');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dispatchResult, setDispatchResult] = useState(null);

  const mpaDefaultText = `🚨 *SEKAT-AI ALERT: REKOMENDASI SEKAT BAKAR* 🚨
Titik api awal dan semak kering terdeteksi di lokasi koordinat (-7.12340, 110.56780).
• Rekomendasi Jalur Sekat: ± 3.8 km
• Lebar Babatan: 4.0 meter
• Arah Angin: Tenggara (14 km/jam)
• Safety Buffer: 35 meter
Mohon Tim MPA segera menuju koordinat untuk pembabatan preventif.`;

  const residentDefaultText = `⚠️ *PERINGATAN DINI KUALITAS UDARA (PM2.5)* ⚠️
Diinformasikan kepada warga di area Kuningan & sekitarnya:
Terpantau potensi kepulan asap kebakaran semak di area barat.
• Tingkat Partikel PM2.5: Waspada (68 µg/m³)
• Arah Sebaran Asap: Mengarah ke Timur
Dihimbau untuk mengenakan masker dan menutup ventilasi sementara.`;

  const [message, setMessage] = useState(recipientGroup === 'mpa' ? mpaDefaultText : residentDefaultText);

  const handleGroupChange = (group) => {
    setRecipientGroup(group);
    setMessage(group === 'mpa' ? mpaDefaultText : residentDefaultText);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSend = async () => {
    setLoading(true);
    try {
      const payload = {
        analysis_data: currentAnalysis || null,
        image_id: currentAnalysis?.image_id || 'sample_aerial',
      };
      const res = await dispatchWhatsApp(payload);
      setDispatchResult(res);

      // Open WhatsApp web in new tab
      const cleanPhone = phone.replace(/[^0-9]/g, '');
      const encodedMsg = encodeURIComponent(message);
      const waUrl = `https://api.whatsapp.com/send?phone=${cleanPhone}&text=${encodedMsg}`;
      window.open(waUrl, '_blank');
    } catch (err) {
      console.error(err);
      // Fallback direct open
      const encodedMsg = encodeURIComponent(message);
      window.open(`https://api.whatsapp.com/send?text=${encodedMsg}`, '_blank');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <Send className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">Broadcast WhatsApp SEKAT-AI</h3>
              <p className="text-[11px] text-slate-500 font-medium">Kirim peringatan cepat ke regu atau warga</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-4">
          {/* Target Group Selector */}
          <div>
            <label className="text-xs font-bold text-slate-700 block mb-1.5">Target Penerima</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleGroupChange('mpa')}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition border ${
                  recipientGroup === 'mpa'
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                Regu Tim MPA (Taktis)
              </button>
              <button
                type="button"
                onClick={() => handleGroupChange('residents')}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition border ${
                  recipientGroup === 'residents'
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                Warga Downwind (PM2.5)
              </button>
            </div>
          </div>

          {/* Nomor WhatsApp */}
          <div>
            <label className="text-xs font-bold text-slate-700 block mb-1.5">Nomor Tujuan (Opsional)</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white rounded-xl px-3.5 py-2 text-xs text-slate-900 outline-none font-mono"
              placeholder="Contoh: 6281234567890"
            />
          </div>

          {/* Pesan Template */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold text-slate-700">Isi Pesan Peringatan</label>
              <button
                type="button"
                onClick={handleCopy}
                className="text-[11px] text-emerald-700 hover:underline flex items-center gap-1 font-bold"
              >
                {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Tersalin' : 'Salin Teks'}</span>
              </button>
            </div>
            <textarea
              rows={6}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white rounded-xl p-3 text-xs text-slate-900 outline-none font-mono leading-relaxed resize-none"
            />
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-end gap-2 bg-slate-50/70">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold transition shadow-sm"
          >
            Batal
          </button>
          <button
            onClick={handleSend}
            disabled={loading}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ExternalLink className="w-3.5 h-3.5" />}
            <span>Kirim via WhatsApp</span>
          </button>
        </div>
      </div>
    </div>
  );
}
