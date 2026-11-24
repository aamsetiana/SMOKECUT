import React, { useState } from 'react';
import {
  Sliders,
  Check,
  Shield,
  Bell,
  Cpu,
  Palette,
  Save
} from 'lucide-react';

export default function SettingsView() {
  const [activeTab, setActiveTab] = useState('umum'); // 'umum', 'notifikasi', 'ai_cv', 'tampilan'
  const [preventiveMode, setPreventiveMode] = useState(true);
  const [autoUpdateWeather, setAutoUpdateWeather] = useState(true);
  const [earlyNotification, setEarlyNotification] = useState(true);
  const [firebreakWidth, setFirebreakWidth] = useState('4 Meter');
  const [safetyBuffer, setSafetyBuffer] = useState(50);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const tabs = [
    { id: 'umum', label: 'Umum', icon: Sliders },
    { id: 'notifikasi', label: 'Notifikasi', icon: Bell },
    { id: 'ai_cv', label: 'AI & CV', icon: Cpu },
    { id: 'tampilan', label: 'Tampilan', icon: Palette },
  ];

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Settings Grid (White & Green Theme) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Pengaturan Umum */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Pengaturan Umum</h3>

          <div className="space-y-4">
            {/* Toggle 1: Mode Patroli Preventif */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Mode Patroli Preventif</p>
                <p className="text-[11px] text-slate-500">Fokus pada pemetaan semak kering sebelum api muncul</p>
              </div>
              <button
                type="button"
                onClick={() => setPreventiveMode(!preventiveMode)}
                className={`w-11 h-6 rounded-full transition-colors relative ${
                  preventiveMode ? 'bg-emerald-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                    preventiveMode ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Toggle 2: Auto Update Data Cuaca */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Auto Update Data Cuaca</p>
                <p className="text-[11px] text-slate-500">Sinkronisasi arah dan kecepatan angin lokal</p>
              </div>
              <button
                type="button"
                onClick={() => setAutoUpdateWeather(!autoUpdateWeather)}
                className={`w-11 h-6 rounded-full transition-colors relative ${
                  autoUpdateWeather ? 'bg-emerald-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                    autoUpdateWeather ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Toggle 3: Notifikasi Dini */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900">Notifikasi Dini</p>
                <p className="text-[11px] text-slate-500">Kirim peringatan otomatis saat risiko mencapai level Bahaya</p>
              </div>
              <button
                type="button"
                onClick={() => setEarlyNotification(!earlyNotification)}
                className={`w-11 h-6 rounded-full transition-colors relative ${
                  earlyNotification ? 'bg-emerald-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                    earlyNotification ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Parameter Analisis */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Parameter Analisis</h3>

          <div className="space-y-4 text-xs">
            {/* Lebar Sekat Bakar */}
            <div>
              <label className="text-slate-700 font-semibold block mb-1.5">Lebar Sekat Bakar</label>
              <select
                value={firebreakWidth}
                onChange={(e) => setFirebreakWidth(e.target.value)}
                className="w-full bg-white border border-slate-200 focus:border-emerald-500 text-slate-900 rounded-xl px-3.5 py-2.5 outline-none font-semibold cursor-pointer shadow-sm"
              >
                <option value="3 Meter">3 Meter (Standar Semak Rendah)</option>
                <option value="4 Meter">4 Meter (Rekomendasi Optimal)</option>
                <option value="5 Meter">5 Meter (Vegetasi Lebat & Angin Kencang)</option>
              </select>
            </div>

            {/* Safety Buffer Slider */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-slate-700 font-semibold">Safety Buffer</label>
                <span className="font-bold text-emerald-700 font-mono">{safetyBuffer} m</span>
              </div>
              <input
                type="range"
                min="20"
                max="100"
                value={safetyBuffer}
                onChange={(e) => setSafetyBuffer(Number(e.target.value))}
                className="w-full accent-emerald-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
                <span>20 m</span>
                <span>50 m</span>
                <span>100 m</span>
              </div>
            </div>

            {/* Simpan Perubahan Button */}
            <div className="pt-2">
              <button
                onClick={handleSave}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/25 transition"
              >
                {savedSuccess ? (
                  <>
                    <Check className="w-4 h-4 text-white" />
                    <span>Perubahan Berhasil Disimpan!</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Simpan Perubahan</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
