import React, { useState } from 'react';
import {
  MessageSquare,
  Users,
  Send,
  CheckCircle2,
  Clock,
  MapPin,
  AlertTriangle,
  ArrowRight
} from 'lucide-react';

export default function NotificationsView({ onOpenDispatchModal }) {
  const notifications = [
    {
      target: 'Untuk Tim MPA',
      message: 'Info: Titik api terdeteksi di koordinat -7.1234, 110.5678. Jalur sekat bakar ± 3.8 km. Segera lakukan babatan sekat sesuai panduan koordinat.',
      time: '14:37 WIB',
      icon: Users,
      badge: 'Prioritas Tinggi',
      badgeColor: 'bg-rose-100 border border-rose-300 text-rose-800'
    },
    {
      target: 'Untuk Warga',
      message: 'Waspada asap PM2.5 di sekitar wilayah Anda. Gunakan masker saat beraktivitas di luar dan tutup jendela rumah untuk mencegah paparan partikel halus.',
      time: '14:37 WIB',
      icon: AlertTriangle,
      badge: 'Early Warning',
      badgeColor: 'bg-amber-100 border border-amber-300 text-amber-900 font-bold'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Main WhatsApp Card (White & Green Theme) */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
        {/* WhatsApp Header Badge */}
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shadow-sm">
            {/* WhatsApp SVG Icon */}
            <svg className="w-8 h-8 fill-current" viewBox="0 0 24 24">
              <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0012.04 2zm.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 012.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.196 8.196 0 01-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24zm4.52 11.66c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.98-.14.17-.29.19-.54.06-.25-.13-1.06-.39-2.02-1.24-.74-.66-1.24-1.48-1.39-1.73-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.44.13-.14.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.13-.56-1.35-.77-1.85-.2-.49-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.78 2.71 4.3 3.8.6.26 1.07.41 1.43.53.6.19 1.15.16 1.58.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.12-.22-.19-.47-.32z"/>
            </svg>
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">Kirim Notifikasi Melalui WhatsApp</h3>
            <p className="text-xs text-slate-500 font-medium">Peringatan cepat untuk keselamatan bersama</p>
          </div>
        </div>

        {/* 2 Preview Message Boxes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {notifications.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col justify-between space-y-3 relative group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <item.icon className="w-4 h-4 text-emerald-600" />
                    <span className="text-xs font-bold text-slate-900">{item.target}</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-800 font-mono leading-relaxed bg-white p-3 rounded-xl border border-slate-200">
                  {item.message}
                </p>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span className="flex items-center gap-1 font-medium">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {item.time}
                </span>
                <span className="text-emerald-700 text-[10px] font-bold">Tersinkronisasi Otomatis</span>
              </div>
            </div>
          ))}
        </div>

        {/* Trigger Button: Buat Pesan */}
        <div>
          <button
            onClick={onOpenDispatchModal}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition"
          >
            <span>Buat Pesan</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
