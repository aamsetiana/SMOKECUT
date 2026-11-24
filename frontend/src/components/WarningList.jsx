import React from 'react';
import { AlertTriangle } from 'lucide-react';

/** Limits of the current result, as reported by the backend. */
export default function WarningList({ analysis }) {
  const warnings = analysis?.firebreak_plan?.warnings || [];
  if (!warnings.length) return null;
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs text-amber-900">
      <div className="flex items-center gap-2 font-extrabold mb-1.5">
        <AlertTriangle className="w-4 h-4 text-amber-600" />
        <span>Catatan hasil</span>
      </div>
      <ul className="list-disc pl-5 space-y-0.5">
        {warnings.map((w) => (
          <li key={w}>{w}</li>
        ))}
      </ul>
    </div>
  );
}
