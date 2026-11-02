
import React, { useState, useEffect } from 'react';
import {
  Settings,
  Sparkles,
  Database,
  Cpu,
  Globe2,
  RefreshCw,
  Sliders,
  Shield,
} from 'lucide-react';
import { api } from '../services/api';
import { SystemSettings, GeminiHealth } from '../types';

interface SettingsPageProps {
  onRefreshHealth: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  onRefreshHealth,
}) => {
  const [settingsData, setSettingsData] = useState<SystemSettings | null>(null);
  const [geminiStatus, setGeminiStatus] = useState<GeminiHealth | null>(null);
  const [embeddingsStatus, setEmbeddingsStatus] = useState<any>(null);
  const [vectorDbStatus, setVectorDbStatus] = useState<any>(null);
  const [testingLiveGemini, setTestingLiveGemini] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  useEffect(() => {
    loadAllStatus();
  }, []);

  const loadAllStatus = async () => {
    try {
      const [settings, gemini, embeddings, vectorDb] = await Promise.all([
        api.getSettings(),
        api.getGeminiHealth(false),
        api.getEmbeddingsHealth(),
        api.getVectorDBHealth(),
      ]);

      setSettingsData(settings);
      setGeminiStatus(gemini);
      setEmbeddingsStatus(embeddings);
      setVectorDbStatus(vectorDb);
    } catch (err) {
      console.error('Failed to load settings', err);
    }
  };

  const handleTestLiveGemini = async () => {
    setTestingLiveGemini(true);
    setTestResult(null);

    try {
      const result = await api.getGeminiHealth(true);
      setGeminiStatus(result);
      setTestResult(result.message);
      onRefreshHealth();
    } catch (err: any) {
      setTestResult(err.message || 'Live Gemini diagnostic test failed.');
    } finally {
      setTestingLiveGemini(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-ari-mauve mb-1">
          <Settings className="w-5 h-5" />
          <span className="text-xs uppercase font-semibold tracking-wider">
            System Configuration
          </span>
        </div>

        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-ari-text">
          Settings & Diagnostics
        </h1>

        <p className="text-xs sm:text-sm text-ari-secondary mt-1">
          Inspect your Google Gemini integration, multilingual embedding engine,
          and ChromaDB vector storage.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 1. Gemini Integration */}
        <div className="glass-card p-6 rounded-2xl border border-ari-border">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-ari-border/60">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center text-ari-mauve border border-white">
                <Sparkles className="w-5 h-5" />
              </div>

              <div>
                <h3 className="font-serif text-base font-bold text-ari-text">
                  Google Gemini Integration
                </h3>
                <p className="text-[11px] text-ari-secondary">
                  Gemini Generate Content API
                </p>
              </div>
            </div>

            <span
              className={`px-2.5 py-1 rounded-full text-[10px] font-semibold flex items-center gap-1.5 ${
                geminiStatus?.configured
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  geminiStatus?.configured ? 'bg-emerald-500' : 'bg-rose-500'
                }`}
              />
              {geminiStatus?.configured ? 'Key Configured' : 'Missing Key'}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Target Model:</span>
              <span className="font-mono font-semibold text-ari-mauve">
                {settingsData?.gemini_model || 'gemini-3.8-flash'}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">API Provider:</span>
              <span className="font-mono text-ari-text">Google AI</span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">API Security:</span>
              <span className="text-emerald-700 font-medium flex items-center gap-1">
                <Shield className="w-3 h-3" />
                Protected in backend/.env
              </span>
            </div>

            {geminiStatus?.latency_ms != null && (
              <div className="flex justify-between py-1 border-b border-ari-border/30">
                <span className="text-ari-secondary">Diagnostic Latency:</span>
                <span className="font-mono text-ari-text">
                  {geminiStatus.latency_ms.toFixed(2)} ms
                </span>
              </div>
            )}

            <div className="flex justify-between py-1">
              <span className="text-ari-secondary">Connection Status:</span>
              <span className="font-semibold text-ari-text">
                {geminiStatus?.status || 'Not tested'}
              </span>
            </div>
          </div>

          {/* Live Test */}
          <div className="mt-5 pt-4 border-t border-ari-border/60">
            <button
              onClick={handleTestLiveGemini}
              disabled={testingLiveGemini}
              className="w-full py-2.5 rounded-xl ari-button-gradient text-xs font-semibold flex items-center justify-center gap-2 shadow-sm transition-all hover:scale-[1.01] disabled:opacity-50"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${
                  testingLiveGemini ? 'animate-spin' : ''
                }`}
              />
              <span>
                {testingLiveGemini
                  ? 'Testing Gemini Connection...'
                  : 'Run Live Gemini Diagnostic Test'}
              </span>
            </button>

            {testResult && (
              <div className="mt-3 p-3 rounded-xl bg-ari-bg text-[11px] font-mono leading-relaxed border border-ari-border text-ari-text">
                {testResult}
              </div>
            )}
          </div>
        </div>

        {/* 2. ChromaDB Vector Store */}
        <div className="glass-card p-6 rounded-2xl border border-ari-border">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-ari-border/60">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-ari-lavender flex items-center justify-center text-ari-mauve border border-white">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif text-base font-bold text-ari-text">
                  Vector Database
                </h3>
                <p className="text-[11px] text-ari-secondary">
                  ChromaDB Persistent Storage
                </p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              {vectorDbStatus?.status === 'ready'
                ? 'Operational'
                : 'Initializing'}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Storage Path:</span>
              <span className="font-mono text-[11px] text-ari-text truncate max-w-[200px]">
                {vectorDbStatus?.storage_path || '../storage/chroma'}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Collections:</span>
              <span className="font-semibold text-ari-text">
                {vectorDbStatus?.total_collections || 0}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Total Embedded Vectors:</span>
              <span className="font-semibold text-ari-mauve">
                {vectorDbStatus?.total_vectors || 0}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Distance Space:</span>
              <span className="font-mono text-ari-text">Cosine (HNSW)</span>
            </div>
          </div>
        </div>

        {/* 3. Multilingual Embeddings */}
        <div className="glass-card p-6 rounded-2xl border border-ari-border">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-ari-border/60">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-ari-blush flex items-center justify-center text-ari-mauve border border-white">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif text-base font-bold text-ari-text">
                  Multilingual Embeddings
                </h3>
                <p className="text-[11px] text-ari-secondary">
                  SentenceTransformers
                </p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              {embeddingsStatus?.status || 'Ready'}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Model:</span>
              <span className="font-mono text-ari-mauve font-semibold">
                {settingsData?.embedding_model || 'intfloat/multilingual-e5-base'}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Vector Dimension:</span>
              <span className="font-mono text-ari-text">
                {embeddingsStatus?.embedding_dimension || 768} dims
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Prefix Convention:</span>
              <span className="font-mono text-ari-text">passage: / query:</span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Normalization:</span>
              <span className="text-emerald-700 font-medium">L2 Normalized</span>
            </div>
          </div>
        </div>

        {/* 4. RAG Parameters */}
        <div className="glass-card p-6 rounded-2xl border border-ari-border">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-ari-border/60">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-ari-lavender flex items-center justify-center text-ari-mauve border border-white">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif text-base font-bold text-ari-text">
                  RAG Chunking & Retrieval
                </h3>
                <p className="text-[11px] text-ari-secondary">
                  Configurable Thresholds
                </p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-ari-blush text-ari-mauve-dark border border-ari-mauve/20">
              Active Parameters
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Chunk Size:</span>
              <span className="font-semibold text-ari-text">
                {settingsData?.chunk_size || 800} chars
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Chunk Overlap:</span>
              <span className="font-semibold text-ari-text">
                {settingsData?.chunk_overlap || 120} chars
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Similarity Cutoff Threshold:</span>
              <span className="font-semibold text-ari-mauve">
                {settingsData?.similarity_threshold ?? 0.35}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-ari-border/30">
              <span className="text-ari-secondary">Top-K Context Chunks:</span>
              <span className="font-semibold text-ari-text">
                {settingsData?.top_k_results || 4} chunks
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Supported Languages */}
      <div className="mt-8 glass-card p-6 rounded-2xl border border-ari-border">
        <div className="flex items-center gap-2 mb-4">
          <Globe2 className="w-5 h-5 text-ari-mauve" />
          <h3 className="font-serif text-base font-bold text-ari-text">
            Supported Multilingual Matrix
          </h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 text-xs">
          {settingsData?.supported_languages?.map((lang) => (
            <div
              key={lang.code}
              className="p-3 rounded-xl bg-white/70 border border-ari-border/80 text-left"
            >
              <div className="font-bold text-ari-text">{lang.native}</div>
              <div className="text-[11px] text-ari-secondary">
                {lang.name} ({lang.code})
              </div>
              <div className="text-[10px] text-ari-mauve mt-1 font-medium">
                {lang.script} • {lang.direction.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
