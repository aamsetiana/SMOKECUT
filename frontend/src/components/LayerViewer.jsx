import React, { useState } from 'react';
import { ZoomIn, ZoomOut } from 'lucide-react';
import { getAssetUrl } from '../services/api';

/**
 * Shows the analysed photo/video with the overlay images rendered by the backend.
 * For video, detections and firebreak are already burned into the footage.
 *
 * layers: array of 'vari' | 'detections' | 'firebreak' | 'tactical', or 'map' for the printable map.
 */
export default function LayerViewer({ analysis, layers = [], children }) {
  const [zoom, setZoom] = useState(1);
  const urls = analysis?.layers;

  if (!urls) {
    return (
      <div className="flex-1 min-h-[300px] rounded-xl bg-slate-100 border border-dashed border-slate-300 flex items-center justify-center text-xs text-slate-500 p-6 text-center">
        Belum ada analisis. Unggah foto/video drone di menu Analisis AI.
      </div>
    );
  }

  if (analysis._outdated) {
    return (
      <div className="flex-1 min-h-[300px] rounded-xl bg-slate-100 border border-dashed border-slate-300 flex items-center justify-center text-xs text-slate-500 p-6 text-center">
        Gambar hasil ini sudah diganti analisis yang lebih baru untuk citra yang sama. Jalankan ulang untuk melihatnya.
      </div>
    );
  }

  const asset = (url) => `${getAssetUrl(url)}?v=${analysis._version}`;
  const { width, height } = analysis.dimensions;
  const isMap = layers.includes('map');
  const overlays = [
    ['vari', urls.vari_heatmap_url],
    ['detections', urls.detection_overlay_url],
    ['firebreak', urls.firebreak_overlay_url],
    ['tactical', urls.tactical_overlay_url],
  ].filter(([id, url]) => !isMap && layers.includes(id) && url);
  const fill = 'absolute inset-0 w-full h-full';

  return (
    <div className="flex-1 rounded-xl overflow-hidden relative bg-slate-900 border border-slate-200 flex items-center justify-center">
      <div
        className="relative w-full transition-transform duration-300"
        style={{
          aspectRatio: `${width} / ${height}`,
          maxWidth: `calc(70vh * ${width / height})`,
          transform: `scale(${zoom})`,
        }}
      >
        {isMap ? (
          <img src={asset(urls.tactical_map_url)} alt="Peta sekat bakar" className={fill} />
        ) : urls.video_url ? (
          <video key={urls.video_url} src={getAssetUrl(urls.video_url)} className={fill} autoPlay loop muted playsInline />
        ) : (
          <img src={asset(urls.original_image_url)} alt="Citra drone" className={fill} />
        )}
        {overlays.map(([id, url]) => (
          <img key={id} src={asset(url)} alt="" className={`${fill} pointer-events-none`} />
        ))}
      </div>
      {children}
      <div className="absolute bottom-3 left-3 z-20 flex flex-col gap-1.5">
        {[
          ['Perbesar', ZoomIn, () => setZoom((z) => Math.min(z + 0.2, 2.2))],
          ['Perkecil', ZoomOut, () => setZoom((z) => Math.max(z - 0.2, 1))],
        ].map(([title, Icon, onClick]) => (
          <button
            key={title}
            onClick={onClick}
            title={title}
            className="w-7 h-7 rounded-lg bg-white/95 border border-slate-200 text-slate-700 flex items-center justify-center hover:bg-emerald-50 hover:text-emerald-700 transition shadow-md"
          >
            <Icon className="w-3.5 h-3.5" />
          </button>
        ))}
      </div>
    </div>
  );
}
