import React, { useState, useEffect, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LoginView from './components/LoginView';
import DashboardView from './components/DashboardView';
import AnalysisView from './components/AnalysisView';
import RiskMapView from './components/RiskMapView';
import FirebreakView from './components/FirebreakView';
import NotificationsView from './components/NotificationsView';
import HistoryView from './components/HistoryView';
import SettingsView from './components/SettingsView';
import WhatsAppModal from './components/WhatsAppModal';
import { checkHealth } from './services/api';

const MAX_HISTORY = 20;

function loadStored(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function store(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage full or blocked: the app keeps working without persistence
  }
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [currentUser, setCurrentUser] = useState({
    name: 'Indra Agustiawan',
    role: 'Tim MPA',
    email: 'indra@smokecut.id',
  });
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [history, setHistory] = useState(() => loadStored('smokecut.history', []));
  const [current, setCurrent] = useState(() => loadStored('smokecut.history', [])[0] || null);
  const [source, setSource] = useState(null);
  const [fieldData, setFieldData] = useState(() => loadStored('smokecut.fieldData', {}));
  const [modalDispatches, setModalDispatches] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  // The backend overwrites overlay files when the same media is analysed again, so images
  // are versioned and those of superseded results are not shown.
  const analysisData = useMemo(() => {
    if (!current) return null;
    const outdated = history.some((h) => h.sourceId === current.sourceId && h.time > current.time);
    return { ...current.analysis, _version: current.time, _outdated: outdated };
  }, [current, history]);
  const warningCount = analysisData?.firebreak_plan?.warnings?.length || 0;

  useEffect(() => {
    const check = () => checkHealth().then((res) => setBackendStatus(res.status === 'ok' ? 'ok' : 'offline'));
    check();
    const timer = setInterval(check, 15000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => store('smokecut.history', history), [history]);
  useEffect(() => store('smokecut.fieldData', fieldData), [fieldData]);

  const handleAnalysisCompleted = (analysis, name) => {
    const entry = { time: Date.now(), name, sourceId: analysis.image_id, analysis };
    setCurrent(entry);
    setHistory((items) => [entry, ...items].slice(0, MAX_HISTORY));
    setBackendStatus('ok');
  };

  const openHistoryItem = (item) => {
    setCurrent(item);
    setSource({ id: item.sourceId === 'sample_drone_fire' ? 'sample_video' : item.sourceId, name: item.name });
    setActiveTab('analysis');
  };

  const tabMetadata = {
    dashboard: {
      title: 'Dashboard Monitoring',
      subtitle: 'Hasil analisis citra drone terakhir',
    },
    analysis: {
      title: 'Analisis Citra Drone',
      subtitle: 'Unggah foto/video untuk mendeteksi api dan merencanakan sekat bakar',
    },
    risk_map: {
      title: 'Peta Risiko Kebakaran',
      subtitle: 'Sebaran semak kering, api, dan sekat pada citra terakhir',
    },
    firebreak: {
      title: 'Perencanaan Sekat Bakar',
      subtitle: 'Jalur sekat di depan garis api sesuai standar tertulis',
    },
    notifications: {
      title: 'Notifikasi & Peringatan',
      subtitle: 'Kelola dan kirim peringatan kepada Tim MPA dan masyarakat',
    },
    history: {
      title: 'Riwayat Analisis',
      subtitle: 'Lihat kembali hasil analisis sebelumnya',
    },
    settings: {
      title: 'Pengaturan Sistem',
      subtitle: 'Atur preferensi dan parameter aplikasi',
    },
  };

  if (!isLoggedIn) {
    return (
      <LoginView
        onLogin={(user) => {
          setCurrentUser(user);
          setIsLoggedIn(true);
        }}
      />
    );
  }

  const currentMeta = tabMetadata[activeTab] || tabMetadata.dashboard;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans select-none">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={() => setIsLoggedIn(false)}
        warningCount={warningCount}
        user={currentUser}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
        isMobileOpen={isMobileSidebarOpen}
        setIsMobileOpen={setIsMobileSidebarOpen}
      />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <Header
          title={currentMeta.title}
          subtitle={currentMeta.subtitle}
          onOpenNotifications={() => setActiveTab('notifications')}
          onToggleMobileSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
          backendStatus={backendStatus}
          hasAlert={warningCount > 0}
        />

        {/* Dynamic Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-100/60">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'dashboard' && (
              <DashboardView
                analysisData={analysisData}
                sourceName={current?.name}
                onNavigateToAnalysis={() => setActiveTab('analysis')}
              />
            )}

            {/* Kept mounted so a running upload/analysis survives tab changes */}
            <div className={activeTab === 'analysis' ? '' : 'hidden'}>
              <AnalysisView
                analysis={analysisData}
                fieldData={fieldData}
                setFieldData={setFieldData}
                source={source}
                setSource={setSource}
                onAnalysisCompleted={handleAnalysisCompleted}
              />
            </div>

            {activeTab === 'risk_map' && <RiskMapView analysisData={analysisData} />}

            {activeTab === 'firebreak' && (
              <FirebreakView analysisData={analysisData} onNavigateToAnalysis={() => setActiveTab('analysis')} />
            )}

            {activeTab === 'notifications' && (
              <NotificationsView analysisData={analysisData} onOpenDispatchModal={setModalDispatches} />
            )}

            {activeTab === 'history' && <HistoryView history={history} onViewDetail={openHistoryItem} />}

            {activeTab === 'settings' && (
              <SettingsView
                fieldData={fieldData}
                setFieldData={setFieldData}
                backendStatus={backendStatus}
                historyCount={history.length}
                onClearHistory={() => setHistory([])}
              />
            )}
          </div>
        </main>
      </div>

      {/* WhatsApp Dispatch Modal */}
      {modalDispatches && <WhatsAppModal dispatches={modalDispatches} onClose={() => setModalDispatches(null)} />}
    </div>
  );
}
