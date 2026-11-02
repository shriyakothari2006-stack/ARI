import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Hash } from 'lucide-react';
import { DocumentCitation } from '../types';

interface CitationCardProps {
  citation: DocumentCitation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-ari-border/80 bg-white/70 backdrop-blur-sm transition-all overflow-hidden text-xs shadow-subtle hover:border-ari-mauve/40">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left px-3 py-2 flex items-center justify-between gap-2 hover:bg-ari-blush/30 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className="w-5 h-5 rounded-full bg-ari-blush/80 text-ari-mauve font-semibold flex items-center justify-center text-[10px] shrink-0 border border-ari-mauve/20">
            {index + 1}
          </span>
          <FileText className="w-3.5 h-3.5 text-ari-mauve shrink-0" />
          <span className="font-medium text-ari-text truncate max-w-[180px] sm:max-w-[260px]">
            {citation.document_name}
          </span>
          {citation.page_number && (
            <span className="bg-ari-lavender/60 text-ari-text px-1.5 py-0.5 rounded text-[10px] font-medium shrink-0">
              Page {citation.page_number}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 shrink-0 text-ari-secondary">
          <span className="text-[10px] font-medium bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200">
            {Math.round(citation.similarity_score * 100)}% Match
          </span>
          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-ari-secondary" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-ari-secondary" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="px-3.5 py-2.5 bg-ari-bg/70 border-t border-ari-border/50 text-ari-text space-y-1.5 animate-fade-in">
          <div className="flex items-center justify-between text-[10px] text-ari-secondary pb-1 border-b border-ari-border/30">
            <span className="flex items-center gap-1">
              <Hash className="w-3 h-3 text-ari-mauve" />
              Chunk ID: <code className="font-mono">{citation.chunk_id}</code>
            </span>
            <span>Retrieved from ChromaDB Vector Store</span>
          </div>
          <p className="font-mono text-[11px] leading-relaxed text-ari-text/90 bg-white/80 p-2.5 rounded-lg border border-ari-border/60 whitespace-pre-wrap selection:bg-ari-blush">
            "{citation.snippet}"
          </p>
        </div>
      )}
    </div>
  );
};
