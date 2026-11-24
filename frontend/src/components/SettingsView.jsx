import React from 'react';
import { API_BASE_URL } from '../services/api';
import FieldDataForm from './FieldDataForm';

export default function SettingsView({ fieldData, setFieldData, backendStatus, onClearHistory, historyCount }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Data Lapangan</h3>
        <p className="text-[11px] text-slate-500">Dipakai untuk analisis berikutnya dan tersimpan di browser ini.</p>
        <FieldDataForm value={fieldData} onChange={setFieldData} />
        <button
          onClick={() => setFieldData({})}
          className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold transition shadow-sm"
        >
          Kosongkan Isian
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 text-xs">
        <h3 className="font-bold uppercase tracking-wider text-slate-500">Sistem</h3>
        <p className="flex justify-between">
          <span className="text-slate-600">Backend</span>
          <b className={backendStatus === 'ok' ? 'text-emerald-700' : 'text-rose-700'}>
            {backendStatus === 'ok' ? 'Terhubung' : 'Tidak terhubung'}
          </b>
        </p>
        <p className="flex justify-between">
          <span className="text-slate-600">Alamat</span>
          <span className="font-mono">{API_BASE_URL || window.location.origin}</span>
        </p>
        <p className="flex justify-between">
          <span className="text-slate-600">Riwayat tersimpan</span>
          <b>{historyCount}</b>
        </p>
        <button
          onClick={() => window.confirm('Hapus seluruh riwayat analisis di browser ini?') && onClearHistory()}
          disabled={!historyCount}
          className="px-4 py-2 rounded-xl bg-white hover:bg-rose-50 border border-slate-200 text-rose-700 font-bold transition shadow-sm disabled:opacity-50"
        >
          Hapus Riwayat
        </button>
      </div>
    </div>
  );
}
