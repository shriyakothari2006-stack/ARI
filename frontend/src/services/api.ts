
import {
  DocumentItem,
  KnowledgeBase,
  Conversation,
  ChatMessage,
  GeminiHealth,
  SystemStatus,
  SystemSettings,
  DocumentCitation,
} from '../types';

const API_BASE = '/api';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    });

    if (!res.ok) {
      let detail = `Request failed with status ${res.status}`;

      try {
        const errorJson = await res.json();
        detail = errorJson.detail || detail;
      } catch {
        // Use fallback text.
      }

      throw new ApiError(detail, res.status);
    }

    return await res.json();
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }

    throw new ApiError(
      'Unable to connect to ARI backend server. Please verify the backend is running.',
      0
    );
  }
}

export const api = {
  // Health & Diagnostics
  getHealth: () => request<SystemStatus>('/health'),

  getGeminiHealth: (testLive: boolean = false) =>
    request<GeminiHealth>(`/health/gemini?test_live=${testLive}`),

  getEmbeddingsHealth: () => request<any>('/health/embeddings'),

  getVectorDBHealth: () => request<any>('/health/vector-db'),

  // Settings
  getSettings: () => request<SystemSettings>('/settings'),

  getDetailedStatus: () => request<any>('/settings/status'),

  // Knowledge Bases
  listKnowledgeBases: () => request<KnowledgeBase[]>('/knowledge-bases'),

  createKnowledgeBase: (name: string, description?: string) =>
    request<KnowledgeBase>('/knowledge-bases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    }),

  deleteKnowledgeBase: (id: string) =>
    request<{ success: boolean; message: string }>(
      `/knowledge-bases/${id}`,
      { method: 'DELETE' }
    ),

  // Documents
  listDocuments: (kbId?: string) =>
  request<DocumentItem[]>(
    kbId ? `/documents?knowledge_base_id=${kbId}` : '/documents'
  ),

  getDocument: (id: string) =>
    request<DocumentItem>(`/documents/${id}`),

  deleteDocument: (id: string) =>
    request<{ success: boolean; message: string }>(
      `/documents/${id}`,
      { method: 'DELETE' }
    ),

  reindexDocument: (id: string) =>
    request<DocumentItem>(`/documents/${id}/reindex`, {
      method: 'POST',
    }),

  uploadDocument: async (
    file: File,
    kbId: string = 'default'
  ): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('knowledge_base_id', kbId);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      let detail = 'Upload failed';

      try {
        const errorJson = await res.json();
        detail = errorJson.detail || detail;
      } catch {
        // Use fallback text.
      }

      throw new ApiError(detail, res.status);
    }

    return await res.json();
  },

  // Chat
  sendMessage: (
    message: string,
    conversationId?: string,
    kbId: string = 'default',
    useGeneralKnowledge: boolean = false
  ) =>
    request<{
      conversation_id: string;
      message: ChatMessage;
      detected_language: string;
      retrieval_used: boolean;
      context_chunks_retrieved: number;
    }>('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        knowledge_base_id: kbId,
        use_general_knowledge: useGeneralKnowledge,
      }),
    }),

  getConversationHistory: () =>
    request<Conversation[]>('/chat/history'),

  getConversation: (id: string) =>
    request<Conversation>(`/chat/${id}`),

  renameConversation: (id: string, title: string) =>
    request<Conversation>(`/chat/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    }),

  deleteConversation: (id: string) =>
    request<{ success: boolean; message: string }>(
      `/chat/${id}`,
      { method: 'DELETE' }
    ),
};
