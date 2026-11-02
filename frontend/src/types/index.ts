
export interface DocumentCitation {
  document_id: string;
  document_name: string;
  page_number?: number | null;
  chunk_id: string;
  snippet: string;
  similarity_score: number;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  language?: string;
  citations: DocumentCitation[];
  model?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  knowledge_base_id?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: ChatMessage[];
}

export interface DocumentItem {
  id: string;
  knowledge_base_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  total_pages: number;
  total_chunks: number;
  status: 'indexed' | 'processing' | 'failed';
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  document_count: number;
  total_chunks: number;
}

export interface GeminiHealth {
  configured: boolean;
  status: string;
  model: string;
  message: string;
  latency_ms?: number | null;
  endpoint_tested: string;
}

export interface SystemStatus {
  status: string;
  version: string;
  timestamp: string;
  services: {
    backend: string;
    database: string;
    gemini_configured: boolean;
    gemini_model: string;
    embeddings: string;
    vector_store: string;
  };
}

export interface SystemSettings {
  gemini_configured: boolean;
  gemini_model: string;
  embedding_model: string;
  similarity_threshold: number;
  top_k_results: number;
  chunk_size: number;
  chunk_overlap: number;
  max_upload_size_mb: number;
  allowed_extensions: string[];
  supported_languages: {
    code: string;
    name: string;
    native: string;
    script: string;
    direction: 'ltr' | 'rtl';
  }[];
}
