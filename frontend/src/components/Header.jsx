import React from 'react';
import { Bell, Maximize2, Menu } from 'lucide-react';

export default function Header({ title, subtitle, onOpenNotifications, onToggleMobileSidebar, backendStatus, hasAlert }) {
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  };

  return (
    <header className="h-16 px-4 sm:px-6 bg-white/95 backdrop-blur-md border-b border-slate-200/80 flex items-center justify-between sticky top-0 z-10 select-none shadow-sm">
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Mobile Hamburger Button */}
        <button
          onClick={onToggleMobileSidebar}
          className="md:hidden p-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:text-emerald-700 hover:border-emerald-300 transition shadow-sm"
          title="Buka Menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="w-1.5 h-8 bg-gradient-to-b from-emerald-500 to-green-600 rounded-full shadow-sm shadow-emerald-500/20 shrink-0" />
        <div>
          <h2 className="text-base sm:text-lg font-black text-slate-900 tracking-tight leading-tight">
            {title}
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5 line-clamp-1">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Backend connection */}
        <span
          className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-[11px] font-bold ${
            backendStatus === 'ok'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
              : backendStatus === 'offline'
                ? 'bg-rose-50 border-rose-200 text-rose-700'
                : 'bg-slate-50 border-slate-200 text-slate-500'
          }`}
        >
          {{ ok: 'Backend terhubung', offline: 'Backend terputus' }[backendStatus] || 'Memeriksa...'}
        </span>

        {/* Notification Bell */}
        <button
          onClick={onOpenNotifications}
          className="relative p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-emerald-700 hover:border-emerald-300 transition shadow-sm"
          title="Notifikasi"
        >
          <Bell className="w-4 h-4" />
          {hasAlert && <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-amber-500" />}
        </button>

        {/* Fullscreen Button */}
        <button
          onClick={toggleFullscreen}
          className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-emerald-700 hover:border-emerald-300 transition shadow-sm"
          title="Layar Penuh"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
