
import React, { useEffect, useState } from 'react';
import { GeminiHealth } from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';

import { ChatDashboard } from './pages/ChatDashboard';
import { LandingPage } from './pages/LandingPage';
import { SettingsPage } from './pages/SettingsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { AboutPage } from './pages/AboutPage';

type Page = 'home' | 'chat' | 'settings' | 'knowledge-base' | 'about';

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
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
            onExploreKB={() => navigateTo('knowledge-base')}
          />
        )}

        {currentPage === 'chat' && (
          <ChatDashboard
            geminiHealth={geminiHealth}
            onNavigate={navigateTo}
          />
        )}

        {currentPage === 'knowledge-base' && (
          <KnowledgeBasePage />
        )}

        {currentPage === 'settings' && (
          <SettingsPage onRefreshHealth={fetchGeminiHealth} />
        )}

        {currentPage === 'about' && (
          <AboutPage />
        )}
      </main>
    </div>
  );
};

export default App;
