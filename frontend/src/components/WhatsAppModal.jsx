import React, { useState } from 'react';
import { X, Send, Copy, Check, ExternalLink } from 'lucide-react';

/** dispatches: [MPA message, downwind residents message] from POST /api/dispatch-whatsapp. */
export default function WhatsAppModal({ dispatches, onClose }) {
  const [groupIndex, setGroupIndex] = useState(0);
  const [phone, setPhone] = useState('');
  const [copied, setCopied] = useState(false);
  const [message, setMessage] = useState(dispatches[0].message_text);

  const handleGroupChange = (index) => {
    setGroupIndex(index);
    setMessage(dispatches[index].message_text);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSend = () => {
    const number = phone.replace(/[^0-9]/g, '');
    window.open(`https://wa.me/${number}?text=${encodeURIComponent(message)}`, '_blank', 'noopener');
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
              {dispatches.map((item, index) => (
                <button
                  key={item.recipient_group}
                  type="button"
                  onClick={() => handleGroupChange(index)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold transition border ${
                    groupIndex === index
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {item.recipient_group}
                </button>
              ))}
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
              placeholder="62..."
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
              rows={10}
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
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Buka di WhatsApp</span>
          </button>
        </div>
      </div>
    </div>
  );
}
