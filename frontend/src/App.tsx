
import React, { useEffect, useState } from 'react';
import { GeminiHealth } from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { ChatDashboard } from './pages/ChatDashboard';
import { LandingPage } from './pages/LandingPage';
import { SettingsPage } from './pages/SettingsPage';

type Page = 'home' | 'chat' | 'settings';

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [geminiHealth, setGeminiHealth] = useState<GeminiHealth | null>(null);

  const fetchGeminiHealth = async () => {
    try {
      const health = await api.getGeminiHealth(false);
      setGeminiHealth(health);
    } catch {
      setGeminiHealth({
        configured: false,
        status: 'offline',
        model: 'gemini-3.8-flash',
        message: 'Backend offline.',
        latency_ms: null,
        endpoint_tested: '/api/health/gemini',
      });
    }
  };

  useEffect(() => {
    fetchGeminiHealth();
  }, []);

  const navigateTo = (page: string) => {
    setCurrentPage(page as Page);
  };

  return (
    <div className="min-h-screen">
      <Navbar
        currentPage={currentPage}
        onNavigate={navigateTo}
        geminiConfigured={geminiHealth?.configured ?? false}
        geminiHealth={geminiHealth}
      />

      <main>
        {currentPage === 'home' && (
  <LandingPage
    onGetStarted={() => navigateTo('chat')}
    onExploreKB={() => navigateTo('chat')}
  />
)}

{currentPage === 'chat' && (
 <ChatDashboard
  geminiHealth={geminiHealth}
  onNavigate={navigateTo}
/>
)}

        {currentPage === 'settings' && (
          <SettingsPage onRefreshHealth={fetchGeminiHealth} />
        )}
      </main>
    </div>
  );
};

export default App;
