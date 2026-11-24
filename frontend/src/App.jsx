import React, { useState, useEffect } from 'react';
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
import { checkHealth, runAnalysis, DEFAULT_ANALYSIS_DATA } from './services/api';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [currentUser, setCurrentUser] = useState({
    name: 'Indra Agustiawan',
    role: 'Tim MPA',
    email: 'indra@smokecut.id',
  });
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState('ok');
  const [analysisData, setAnalysisData] = useState(DEFAULT_ANALYSIS_DATA);
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Check health and run baseline sample analysis on mount
  useEffect(() => {
    checkHealth()
      .then((res) => {
        if (res.status === 'ok') {
          setBackendStatus('ok');
          // Fetch initial analysis for live dashboard data
          return runAnalysis({ image_id: 'sample' });
        } else {
          setBackendStatus('offline');
        }
      })
      .then((data) => {
        if (data) setAnalysisData(data);
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  const tabMetadata = {
    dashboard: {
      title: 'Dashboard Monitoring',
      subtitle: 'Pantau kondisi hutan secara real-time',
    },
    analysis: {
      title: 'Analisis Citra Drone',
      subtitle: 'Dapatkan hasil analisis lengkap dalam hitungan detik',
    },
    risk_map: {
      title: 'Peta Risiko Kebakaran',
      subtitle: 'Pantau sebaran risiko di seluruh wilayah',
    },
    firebreak: {
      title: 'Perencanaan Sekat Bakar',
      subtitle: 'Rute jalur potong terpendek dan aman untuk pencegahan rambatan api',
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
        unreadNotifications={3}
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
        />

        {/* Dynamic Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-100/60">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'dashboard' && (
              <DashboardView
                analysisData={analysisData}
                onNavigateToAnalysis={() => setActiveTab('analysis')}
                onNavigateToRiskMap={() => setActiveTab('risk_map')}
              />
            )}

            {activeTab === 'analysis' && (
              <AnalysisView
                initialData={analysisData}
                onAnalysisCompleted={(res) => setAnalysisData(res)}
                onNavigateToHistory={() => setActiveTab('history')}
              />
            )}

            {activeTab === 'risk_map' && (
              <RiskMapView analysisData={analysisData} />
            )}

            {activeTab === 'firebreak' && (
              <FirebreakView
                analysisData={analysisData}
                onNavigateToAnalysis={() => setActiveTab('analysis')}
              />
            )}

            {activeTab === 'notifications' && (
              <NotificationsView
                onOpenDispatchModal={() => setIsWhatsAppModalOpen(true)}
              />
            )}

            {activeTab === 'history' && (
              <HistoryView
                onViewDetail={() => setActiveTab('analysis')}
              />
            )}

            {activeTab === 'settings' && <SettingsView />}
          </div>
        </main>
      </div>

      {/* WhatsApp Dispatch Modal */}
      <WhatsAppModal
        isOpen={isWhatsAppModalOpen}
        onClose={() => setIsWhatsAppModalOpen(false)}
        currentAnalysis={analysisData}
      />
    </div>
  );
}
