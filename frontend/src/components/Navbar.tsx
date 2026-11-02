
import React from 'react';
import {
  Sparkles,
  MessageSquare,
  BookOpen,
  Settings,
  Info,
} from 'lucide-react';
import { GeminiHealth } from '../types';

interface NavbarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  geminiConfigured: boolean;
  geminiHealth?: GeminiHealth | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  onNavigate,
  geminiConfigured,
  geminiHealth,
}) => {
  const connected = geminiHealth?.status === 'connected';

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-ari-border px-6 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand / Logo */}
        <button
          onClick={() => onNavigate('home')}
          className="flex items-center gap-2.5 group text-left focus:outline-none"
        >
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center shadow-subtle group-hover:scale-105 transition-transform border border-white/60">
            <Sparkles className="w-5 h-5 text-ari-mauve transition-transform group-hover:rotate-12" />
          </div>

          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-serif text-2xl font-bold tracking-tight text-ari-text group-hover:text-ari-mauve transition-colors">
                ARI
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-widest text-ari-mauve bg-ari-blush/60 px-1.5 py-0.5 rounded-full border border-ari-mauve/20">
                AI
              </span>
            </div>

            <p className="text-[10px] text-ari-secondary font-medium tracking-wide">
              Multilingual Knowledge
            </p>
          </div>
        </button>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-white/60 p-1.5 rounded-full border border-ari-border/70 shadow-sm">
          <button
            onClick={() => onNavigate('chat')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
              currentPage === 'chat'
                ? 'bg-ari-mauve text-white shadow-sm'
                : 'text-ari-secondary hover:text-ari-text hover:bg-ari-blush/40'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Chat
          </button>

          <button
            onClick={() => onNavigate('knowledge-base')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
              currentPage === 'knowledge-base'
                ? 'bg-ari-mauve text-white shadow-sm'
                : 'text-ari-secondary hover:text-ari-text hover:bg-ari-blush/40'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            Knowledge Base
          </button>

          <button
            onClick={() => onNavigate('settings')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
              currentPage === 'settings'
                ? 'bg-ari-mauve text-white shadow-sm'
                : 'text-ari-secondary hover:text-ari-text hover:bg-ari-blush/40'
            }`}
          >
            <Settings className="w-3.5 h-3.5" />
            Settings
          </button>

          <button
            onClick={() => onNavigate('about')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
              currentPage === 'about'
                ? 'bg-ari-mauve text-white shadow-sm'
                : 'text-ari-secondary hover:text-ari-text hover:bg-ari-blush/40'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            About ARI
          </button>
        </nav>

        {/* Gemini Connection Status */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('settings')}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-all hover:opacity-90 glass-panel-subtle"
            title="Click to view Gemini API settings and diagnostics"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                geminiConfigured
                  ? connected
                    ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
                    : 'bg-amber-400'
                  : 'bg-rose-400 animate-pulse'
              }`}
            />

            <span className="text-ari-text font-semibold hidden sm:inline">
              Gemini
            </span>

            <span className="text-[11px] text-ari-secondary">
              {geminiConfigured
                ? connected
                  ? 'Connected'
                  : 'Configured'
                : 'Key Missing'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
