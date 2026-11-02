import React from 'react';
import { Sparkles, MessageSquare, BookOpen, Globe2, ShieldCheck, FileSearch, ArrowRight, Layers, CheckCircle2 } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
  onExploreKB: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onExploreKB }) => {
  return (
    <div className="relative overflow-hidden">
      {/* Background Dreamy Elements */}
      <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-b from-ari-blush/50 via-ari-lavender/40 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />
      <div className="absolute top-60 right-10 w-72 h-72 bg-ari-blush/30 blur-2xl pointer-events-none -z-10 rounded-full" />
      <div className="absolute top-80 left-10 w-80 h-80 bg-ari-lavender/30 blur-2xl pointer-events-none -z-10 rounded-full" />

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-20 text-center">
        {/* Subtle Pill Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold ari-pill text-ari-mauve mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Multilingual RAG Assistant</span>
        </div>

        {/* Main Title */}
        <h1 className="font-serif text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight text-ari-text leading-[1.1] mb-6">
          Knowledge, in <br />
          <span className="italic font-normal bg-gradient-to-r from-ari-mauve via-ari-mauve-dark to-ari-mauve bg-clip-text text-transparent">
            every language.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="max-w-2xl mx-auto text-base sm:text-lg text-ari-secondary font-normal leading-relaxed mb-10">
          Upload documents in English, Hindi, Arabic, or Spanish. Ask questions in any language.
          ARI semantically retrieves verified source passages and crafts grounded answers with precise page citations.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onGetStarted}
            className="w-full sm:w-auto px-8 py-3.5 rounded-full ari-button-gradient font-medium text-sm flex items-center justify-center gap-2 shadow-md transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Start Chatting with ARI</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={onExploreKB}
            className="w-full sm:w-auto px-7 py-3.5 rounded-full glass-card text-ari-text font-medium text-sm flex items-center justify-center gap-2 transition-all hover:bg-white"
          >
            <BookOpen className="w-4 h-4 text-ari-mauve" />
            <span>Manage Knowledge Base</span>
          </button>
        </div>

        {/* Supported Languages Strip */}
        <div className="mt-14 pt-8 border-t border-ari-border/60 max-w-3xl mx-auto">
          <p className="text-xs uppercase tracking-widest text-ari-secondary font-semibold mb-3">
            Seamless Cross-Language Retrieval Across 10+ Languages
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs font-medium text-ari-text">
            {['English', 'हिन्दी (Hindi)', 'मराठी (Marathi)', 'বাংলা (Bengali)', 'தமிழ் (Tamil)', 'తెలుగు (Telugu)', 'Español (Spanish)', 'Français (French)', 'Deutsch (German)', 'العربية (Arabic)'].map((lang, idx) => (
              <span key={idx} className="bg-white/70 px-3 py-1 rounded-full border border-ari-border/80 shadow-subtle">
                {lang}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-ari-text mb-3">
            Intelligent Architecture. Grounded Results.
          </h2>
          <p className="text-sm text-ari-secondary max-w-xl mx-auto">
            Engineered from scratch to solve hallucinations, language barriers, and citation trust issues.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="glass-card p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-ari-blush/70 flex items-center justify-center text-ari-mauve mb-4 border border-ari-mauve/20">
              <Globe2 className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-ari-text mb-2">
              Cross-Language Semantic Search
            </h3>
            <p className="text-xs text-ari-secondary leading-relaxed">
              Powered by <code className="text-ari-mauve font-semibold font-mono">multilingual-e5-base</code>. Upload an English study guide and ask questions in Hindi or French — ARI retrieves the exact passage across language boundaries.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-card p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-ari-lavender/70 flex items-center justify-center text-ari-mauve mb-4 border border-ari-mauve/20">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-ari-text mb-2">
              Clickable Source Citations
            </h3>
            <p className="text-xs text-ari-secondary leading-relaxed">
              Every factual assertion links directly back to the document name and page number. Click any citation to inspect the original text chunk retrieved from the vector database.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-card p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-ari-blush/70 flex items-center justify-center text-ari-mauve mb-4 border border-ari-mauve/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-ari-text mb-2">
              Official xAI Grok Integration
            </h3>
            <p className="text-xs text-ari-secondary leading-relaxed">
              Direct connection to xAI's state-of-the-art <code className="text-ari-mauve font-semibold font-mono">/v1/responses</code> API endpoint with exponential backoff and independent diagnostic tools.
            </p>
          </div>
        </div>
      </section>

      {/* How RAG Works Section */}
      <section className="max-w-4xl mx-auto px-6 py-12 mb-12">
        <div className="glass-panel p-8 sm:p-10 rounded-3xl border border-ari-border">
          <div className="flex items-center gap-2.5 text-ari-mauve mb-3">
            <Layers className="w-5 h-5" />
            <span className="text-xs font-semibold uppercase tracking-wider">How ARI Works</span>
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-ari-text mb-6">
            The 4-Step Multilingual Verification Journey
          </h2>

          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-ari-mauve shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-ari-text">1. Ingestion & Preservation</h4>
                <p className="text-xs text-ari-secondary">
                  PDF, DOCX, TXT, and Markdown files are split into recursive chunks while preserving page numbers and document titles.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-ari-mauve shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-ari-text">2. Multilingual Vector Indexing</h4>
                <p className="text-xs text-ari-secondary">
                  Chunks are encoded with e5 multilingual embeddings into persistent ChromaDB storage.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-ari-mauve shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-ari-text">3. Cross-Language Similarity Match</h4>
                <p className="text-xs text-ari-secondary">
                  Queries in any script match document concepts in the vector space, filtered by strict similarity thresholds.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-ari-mauve shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-ari-text">4. Grounded Grok Synthesis</h4>
                <p className="text-xs text-ari-secondary">
                  xAI Grok formulates an answer in your language, backed by source citations. If context is missing, ARI admits it politely.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
