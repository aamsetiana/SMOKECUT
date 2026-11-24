import React from 'react';
import {
  LayoutDashboard,
  Flame,
  Map,
  Spline,
  Bell,
  RotateCcw,
  Settings,
  LogOut,
  ChevronLeft,
  X
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  setActiveTab,
  onLogout,
  unreadNotifications = 3,
  isCollapsed = false,
  setIsCollapsed,
  isMobileOpen = false,
  setIsMobileOpen,
}) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analysis', label: 'Analisis AI', icon: Flame },
    { id: 'risk_map', label: 'Peta Risiko', icon: Map },
    { id: 'firebreak', label: 'Sekat Bakar', icon: Spline },
    { id: 'notifications', label: 'Notifikasi', icon: Bell, badge: unreadNotifications },
    { id: 'history', label: 'Riwayat', icon: RotateCcw },
    { id: 'settings', label: 'Pengaturan', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen && setIsMobileOpen(false)}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 md:hidden transition-opacity"
        />
      )}

      {/* Main Sidebar Container */}
      <aside
        className={`bg-white border-r border-slate-200 flex flex-col justify-between select-none shrink-0 shadow-sm transition-all duration-300 ease-in-out ${
          isCollapsed ? 'md:w-20' : 'md:w-64'
        } ${
          isMobileOpen
            ? 'fixed inset-y-0 left-0 z-50 w-64 translate-x-0 shadow-2xl'
            : 'fixed inset-y-0 left-0 z-50 -translate-x-full md:relative md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div>
          <div
            onClick={() => setIsCollapsed && setIsCollapsed(!isCollapsed)}
            className={`p-4 border-b border-slate-100 flex items-center transition-all cursor-pointer group hover:bg-slate-50/80 ${
              isCollapsed ? 'justify-center' : 'justify-between gap-3'
            }`}
            title={isCollapsed ? 'Klik untuk memperluas menu' : 'Klik untuk menciutkan menu'}
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-md shadow-emerald-500/20 shrink-0 group-hover:scale-105 transition-transform">
                <Flame className="w-6 h-6 text-white" />
              </div>
              {!isCollapsed && (
                <div className="min-w-0 transition-opacity duration-200">
                  <h1 className="font-extrabold text-base tracking-wider text-slate-900 truncate">SMOKECUT</h1>
                  <p className="text-[10px] text-emerald-700 font-semibold leading-tight line-clamp-1">
                    Smart Drone-Vision
                  </p>
                </div>
              )}
            </div>

            {/* Collapse Icon on Desktop */}
            {!isCollapsed && (
              <button
                type="button"
                className="hidden md:flex w-6 h-6 rounded-lg items-center justify-center text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition shrink-0"
                title="Ciutkan menu"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}

            {/* Close Icon on Mobile */}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                if (setIsMobileOpen) setIsMobileOpen(false);
              }}
              className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              title="Tutup Menu"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="p-2.5 space-y-1 mt-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    if (setIsMobileOpen) setIsMobileOpen(false);
                  }}
                  title={item.label}
                  className={`w-full flex items-center rounded-xl text-xs font-semibold transition-all duration-200 relative group ${
                    isCollapsed
                      ? 'justify-center p-3'
                      : 'justify-between px-3.5 py-2.5'
                  } ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/25 font-bold'
                      : 'text-slate-600 hover:text-emerald-700 hover:bg-emerald-50/80'
                  }`}
                >
                  <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-500 group-hover:text-emerald-600'}`} />
                    {!isCollapsed && <span>{item.label}</span>}
                  </div>
                  {!isCollapsed && item.badge && (
                    <span className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                      isActive ? 'bg-white text-emerald-700' : 'bg-rose-500 text-white'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                  {isCollapsed && item.badge && (
                    <span className="absolute top-1.5 right-2 w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Profile Footer */}
        <div className={`border-t border-slate-100 bg-slate-50/60 transition-all ${isCollapsed ? 'p-2' : 'p-4'}`}>
          <div className={`flex items-center ${isCollapsed ? 'flex-col gap-2 justify-center' : 'justify-between'}`}>
            <div className="flex items-center gap-3 min-w-0" title="Indra Agustiawan (Tim MPA)">
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-xs font-black text-white ring-2 ring-emerald-500/30 shadow-sm shrink-0">
                IA
              </div>
              {!isCollapsed && (
                <div className="text-left min-w-0 truncate">
                  <p className="text-xs font-bold text-slate-900 leading-tight truncate">Indra Agustiawan</p>
                  <p className="text-[11px] text-emerald-700 font-medium">Tim MPA</p>
                </div>
              )}
            </div>
            <button
              onClick={onLogout}
              title="Keluar dari sesi"
              className={`text-xs text-slate-500 hover:text-rose-600 font-semibold rounded-lg hover:bg-rose-50 transition ${
                isCollapsed ? 'p-2' : 'px-2 py-1'
              }`}
            >
              {isCollapsed ? <LogOut className="w-4 h-4" /> : 'Keluar'}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
