import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Plus,
  Send,
  Paperclip,
  Trash2,
  Edit2,
  Copy,
  Check,
  RefreshCw,
  Sparkles,
  AlertCircle,
  FileText,
  Globe2,
  BookOpen,
} from 'lucide-react';
import { api } from '../services/api';
import { Conversation, ChatMessage, KnowledgeBase, GeminiHealth } from '../types';
import { CitationCard } from '../components/CitationCard';

interface ChatDashboardProps {
  geminiHealth: GeminiHealth | null;
  onNavigate: (page: string) => void;
}

export const ChatDashboard: React.FC<ChatDashboardProps> = ({ geminiHealth, onNavigate }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [selectedKbId, setSelectedKbId] = useState<string>('default');
  const [useGeneralKnowledge, setUseGeneralKnowledge] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [editingTitleId, setEditingTitleId] = useState<string | null>(null);
  const [newTitleText, setNewTitleText] = useState('');
  const [chatError, setChatError] = useState<string | null>(null);
  const [uploadingDoc, setUploadingDoc] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load conversations and KBs on mount
  useEffect(() => {
    loadConversations();
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    try {
      const data = await api.listKnowledgeBases();
      setKbs(data);
      if (data.length > 0 && !selectedKbId) {
        setSelectedKbId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load knowledge bases', err);
    }
  };

  const loadConversations = async () => {
    try {
      const convs = await api.getConversationHistory();
      setConversations(convs);
      if (convs.length > 0 && !activeConvId) {
        selectConversation(convs[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversation history', err);
    }
  };

  const selectConversation = async (convId: string) => {
    setActiveConvId(convId);
    setChatError(null);
    try {
      const fullConv = await api.getConversation(convId);
      setMessages(fullConv.messages || []);
      if (fullConv.knowledge_base_id) {
        setSelectedKbId(fullConv.knowledge_base_id);
      }
    } catch (err: any) {
      console.error('Failed to load messages for conversation', err);
      setChatError(err.message || 'Could not load conversation messages.');
    }
  };

  const startNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setChatError(null);
  };

  const handleSendMessage = async (retryText?: string) => {
    const textToSend = retryText || inputText.trim();
    if (!textToSend || loading) return;

    setChatError(null);
    if (!retryText) {
      setInputText('');
    }

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: `temp_${Date.now()}`,
      conversation_id: activeConvId || '',
      role: 'user',
      content: textToSend,
      citations: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const res = await api.sendMessage(
        textToSend,
        activeConvId || undefined,
        selectedKbId,
        useGeneralKnowledge
      );

      // Replace optimistic message and append real assistant message
      setActiveConvId(res.conversation_id);
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        const actualUserMsg: ChatMessage = {
          ...tempUserMsg,
          conversation_id: res.conversation_id,
        };
        return [...withoutTemp, actualUserMsg, res.message];
      });

      // Reload conversations list to update title & timestamp
      loadConversations();
    } catch (err: any) {
      console.error('Failed to send message', err);
      setChatError(err.message || 'Failed to generate answer.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingDoc(true);
    setChatError(null);
    try {
      const doc = await api.uploadDocument(file, selectedKbId);
      // Append a helpful system notice in chat
      const sysMsg: ChatMessage = {
        id: `doc_${Date.now()}`,
        conversation_id: activeConvId || '',
        role: 'system',
        content: `Document "${doc.filename}" successfully uploaded and indexed into ChromaDB (${doc.total_chunks} chunks). You can now ask questions about its content in any language.`,
        citations: [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, sysMsg]);
    } catch (err: any) {
      setChatError(err.message || 'File upload failed.');
    } finally {
      setUploadingDoc(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    try {
      await api.deleteConversation(convId);
      if (activeConvId === convId) {
        startNewChat();
      }
      loadConversations();
    } catch (err: any) {
      alert(err.message || 'Failed to delete conversation.');
    }
  };

  const handleRename = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!newTitleText.trim()) {
      setEditingTitleId(null);
      return;
    }
    try {
      await api.renameConversation(convId, newTitleText.trim());
      setEditingTitleId(null);
      loadConversations();
    } catch (err: any) {
      alert(err.message || 'Failed to rename conversation.');
    }
  };

  return (
    <div className="flex h-[calc(100vh-61px)] overflow-hidden">
      {/* Sidebar: Conversations & KB Selector */}
      <aside className="w-80 border-r border-ari-border glass-panel flex flex-col shrink-0 hidden md:flex">
        {/* New Chat Button */}
        <div className="p-4 border-b border-ari-border/70">
          <button
            onClick={startNewChat}
            className="w-full py-2.5 px-4 rounded-xl ari-button-gradient text-xs font-semibold flex items-center justify-center gap-2 shadow-sm transition-all hover:scale-[1.01]"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Knowledge Base Selector */}
        <div className="px-4 py-3 border-b border-ari-border/50 bg-white/40">
          <label className="text-[10px] uppercase tracking-wider font-semibold text-ari-secondary flex items-center gap-1.5 mb-1.5">
            <BookOpen className="w-3 h-3 text-ari-mauve" />
            Active Knowledge Base
          </label>
          <select
            value={selectedKbId}
            onChange={(e) => setSelectedKbId(e.target.value)}
            className="w-full text-xs bg-white/80 border border-ari-border rounded-lg px-2.5 py-1.5 text-ari-text focus:outline-none focus:ring-1 focus:ring-ari-mauve"
          >
            {kbs.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name} ({kb.document_count} docs)
              </option>
            ))}
          </select>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          <div className="px-2 py-1 text-[10px] uppercase tracking-wider font-semibold text-ari-secondary">
            Recent Conversations
          </div>

          {conversations.length === 0 ? (
            <div className="text-center py-8 text-xs text-ari-secondary">
              No conversations yet. Start a new chat!
            </div>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => selectConversation(c.id)}
                className={`group px-3 py-2.5 rounded-xl text-xs font-medium cursor-pointer flex items-center justify-between transition-all ${
                  activeConvId === c.id
                    ? 'bg-ari-blush/80 text-ari-mauve-dark border border-ari-mauve/30 shadow-subtle'
                    : 'text-ari-text hover:bg-white/60'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 text-ari-mauve" />
                  {editingTitleId === c.id ? (
                    <input
                      type="text"
                      value={newTitleText}
                      onChange={(e) => setNewTitleText(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleRename(c.id, e as any)}
                      autoFocus
                      className="bg-white border border-ari-mauve rounded px-1.5 py-0.5 text-xs w-full text-ari-text"
                    />
                  ) : (
                    <span className="truncate">{c.title}</span>
                  )}
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                  {editingTitleId === c.id ? (
                    <button
                      onClick={(e) => handleRename(c.id, e)}
                      className="p-1 hover:text-emerald-600"
                    >
                      <Check className="w-3 h-3" />
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingTitleId(c.id);
                        setNewTitleText(c.title);
                      }}
                      className="p-1 text-ari-secondary hover:text-ari-text"
                      title="Rename"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                  )}
                  <button
                    onClick={(e) => handleDeleteConversation(c.id, e)}
                    className="p-1 text-ari-secondary hover:text-rose-600"
                    title="Delete"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Conversation Area */}
      <main className="flex-1 flex flex-col bg-ari-bg relative overflow-hidden">
        {/* Missing API Key Banner */}
        {!geminiHealth?.configured && (
          <div className="bg-amber-50 border-b border-amber-200 px-6 py-2.5 flex items-center justify-between text-xs text-amber-900">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Gemini API key missing:</strong> Live AI generation is paused. Add{' '}
                <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">GEMINI_API_KEY</code> to{' '}
                <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">backend/.env</code>.
              </span>
            </div>
            <button
              onClick={() => onNavigate('settings')}
              className="font-semibold underline hover:text-amber-700 ml-4 shrink-0"
            >
              Open Settings
            </button>
          </div>
        )}

        {/* Chat Messages Stream */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-6">
          {messages.length === 0 ? (
            <div className="max-w-xl mx-auto text-center py-20">
              <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center mx-auto mb-4 border border-white/70 shadow-subtle">
                <Sparkles className="w-7 h-7 text-ari-mauve" />
              </div>
              <h2 className="font-serif text-3xl font-bold text-ari-text mb-2">Hello, I'm ARI.</h2>
              <p className="text-xs sm:text-sm text-ari-secondary leading-relaxed mb-6">
                Your multilingual knowledge assistant. Ask me anything about your uploaded documents
                in Hindi, Spanish, French, Arabic, or English.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs text-left max-w-md mx-auto">
                <button
                  onClick={() => setInputText('इस दस्तावेज़ का मुख्य सारांश क्या है?')}
                  className="p-3 rounded-xl glass-card text-ari-text hover:border-ari-mauve/40 text-left"
                >
                  <span className="font-semibold block text-ari-mauve text-[11px]">हिन्दी (Hindi)</span>
                  "इस दस्तावेज़ का मुख्य सारांश क्या है?"
                </button>
                <button
                  onClick={() => setInputText('What are the key conclusions in this document?')}
                  className="p-3 rounded-xl glass-card text-ari-text hover:border-ari-mauve/40 text-left"
                >
                  <span className="font-semibold block text-ari-mauve text-[11px]">English</span>
                  "What are the key conclusions?"
                </button>
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 max-w-3xl ${
                  m.role === 'user' ? 'ml-auto justify-end' : 'mr-auto justify-start'
                }`}
              >
                {m.role !== 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center shrink-0 border border-white/80 shadow-subtle mt-1">
                    <Sparkles className="w-4 h-4 text-ari-mauve" />
                  </div>
                )}

                <div
                  className={`relative group rounded-2xl p-4 text-xs sm:text-sm leading-relaxed transition-all ${
                    m.role === 'user'
                      ? 'ari-button-gradient text-white rounded-br-none shadow-md max-w-xl'
                      : m.role === 'system'
                      ? 'bg-amber-50/80 border border-amber-200 text-amber-900 rounded-xl max-w-2xl'
                      : 'glass-card text-ari-text rounded-bl-none shadow-glass max-w-2xl border-ari-border'
                  }`}
                >
                  {/* Language / Model Tag */}
                  {m.role === 'assistant' && (
                    <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-ari-border/40 text-[10px] text-ari-secondary font-medium">
                      <div className="flex items-center gap-1.5">
                        <Globe2 className="w-3 h-3 text-ari-mauve" />
                        <span>Language: {m.language?.toUpperCase() || 'EN'}</span>
                        <span className="text-ari-border">•</span>
                        <span>Model: {m.model || 'gemini-3.8-flash'}</span>
                      </div>
                      <button
                        onClick={() => handleCopy(m.content, m.id)}
                        className="hover:text-ari-text flex items-center gap-1"
                        title="Copy answer"
                      >
                        {copiedId === m.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span className="text-emerald-600">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>

                  {/* Source Citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-ari-border/60 space-y-2">
                      <div className="text-[11px] font-semibold text-ari-secondary flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-ari-mauve" />
                        <span>Verified Document Sources ({m.citations.length})</span>
                      </div>
                      <div className="space-y-1.5">
                        {m.citations.map((cite, cIdx) => (
                          <CitationCard key={cite.chunk_id || cIdx} citation={cite} index={cIdx} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex gap-3 max-w-2xl mr-auto animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center shrink-0 border border-white/80 shadow-subtle animate-spin">
                <Sparkles className="w-4 h-4 text-ari-mauve" />
              </div>
              <div className="glass-card rounded-2xl p-4 text-xs text-ari-secondary flex items-center gap-2.5">
                <span className="inline-block w-2 h-2 rounded-full bg-ari-mauve animate-bounce" />
                <span className="inline-block w-2 h-2 rounded-full bg-ari-mauve animate-bounce [animation-delay:0.2s]" />
                <span className="inline-block w-2 h-2 rounded-full bg-ari-mauve animate-bounce [animation-delay:0.4s]" />
                <span className="font-medium text-ari-text ml-1">
                  Searching multilingual vectors & synthesizing with Gemini...
                </span>
              </div>
            </div>
          )}

          {/* Chat Error Notice */}
          {chatError && (
            <div className="max-w-2xl mx-auto bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-xl text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{chatError}</span>
              </div>
              <button
                onClick={() => handleSendMessage(messages[messages.length - 1]?.content)}
                className="flex items-center gap-1 text-rose-900 font-semibold underline hover:text-rose-700 shrink-0 ml-3"
              >
                <RefreshCw className="w-3 h-3" /> Retry
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar & Controls */}
        <div className="p-4 sm:p-5 glass-panel border-t border-ari-border bg-white/80">
          <div className="max-w-4xl mx-auto">
            {/* General Knowledge Toggle */}
            <div className="flex items-center justify-between text-[11px] text-ari-secondary mb-2 px-1">
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-1.5 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={useGeneralKnowledge}
                    onChange={(e) => setUseGeneralKnowledge(e.target.checked)}
                    className="rounded border-ari-border text-ari-mauve focus:ring-ari-mauve"
                  />
                  <span>Allow General Knowledge fallback if documents lack sufficient data</span>
                </label>
              </div>

              {uploadingDoc && (
                <span className="text-ari-mauve font-medium animate-pulse">
                  Uploading & indexing document...
                </span>
              )}
            </div>

            {/* Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2 bg-white rounded-2xl border border-ari-border p-1.5 shadow-sm focus-within:ring-2 focus-within:ring-ari-mauve/30 transition-all"
            >
              {/* Attachment Button */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileUpload}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingDoc}
                className="p-2 text-ari-secondary hover:text-ari-mauve hover:bg-ari-blush/40 rounded-xl transition-colors"
                title="Upload document to active Knowledge Base (PDF, DOCX, TXT, MD)"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              {/* Message Input */}
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask ARI a question in any language..."
                disabled={loading}
                className="flex-1 bg-transparent border-0 text-xs sm:text-sm text-ari-text placeholder:text-ari-secondary/60 focus:outline-none px-2 py-1.5"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={!inputText.trim() || loading}
                className="p-2.5 rounded-xl ari-button-gradient transition-all disabled:opacity-40 disabled:pointer-events-none hover:scale-105"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};
