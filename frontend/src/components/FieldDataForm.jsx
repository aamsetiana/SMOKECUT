import React, { useId } from 'react';
import { FIELD_PARAMS } from '../services/api';

/** Inputs for field measurements. Empty inputs are not sent to the backend. */
export default function FieldDataForm({ value, onChange }) {
  const uid = useId();
  return (
    <div className="grid grid-cols-2 gap-3">
      {FIELD_PARAMS.map(({ name, label, hint }) => (
        <div key={name}>
          <label htmlFor={`${uid}${name}`} className="text-[11px] text-slate-600 font-medium block mb-1">
            {label}
          </label>
          <input
            id={`${uid}${name}`}
            type="number"
            step="any"
            value={value[name] ?? ''}
            onChange={(e) => onChange({ ...value, [name]: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 focus:border-emerald-500 focus:bg-white rounded-xl px-3 py-1.5 text-xs text-slate-900 outline-none"
          />
          <p className="text-[10px] text-slate-400 mt-0.5">{hint}</p>
        </div>
      ))}
    </div>
  );
}
