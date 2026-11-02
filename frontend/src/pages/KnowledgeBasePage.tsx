import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  UploadCloud,
  FileText,
  Trash2,
  RefreshCw,
  Plus,
  Layers,
  File,
  CheckCircle2,
  AlertCircle,
  Database,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentItem, KnowledgeBase } from '../types';

export const KnowledgeBasePage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [selectedKbId, setSelectedKbId] = useState<string>('default');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [reindexingId, setReindexingId] = useState<string | null>(null);
  const [newKbName, setNewKbName] = useState('');
  const [showNewKbModal, setShowNewKbModal] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  useEffect(() => {
    if (selectedKbId) {
      loadDocuments(selectedKbId);
    }
  }, [selectedKbId]);

  const loadKnowledgeBases = async () => {
    try {
      const data = await api.listKnowledgeBases();
      setKbs(data);
      if (data.length > 0 && !selectedKbId) {
        setSelectedKbId(data[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load KBs', err);
    }
  };

  const loadDocuments = async (kbId: string) => {
    setLoading(true);
    try {
      const docs = await api.listDocuments(kbId);
      setDocuments(docs);
    } catch (err: any) {
      console.error('Failed to load documents', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setStatusMessage(null);

    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        await api.uploadDocument(file, selectedKbId);
        successCount++;
      } catch (err: any) {
        errorCount++;
        setStatusMessage({ type: 'error', text: `${file.name}: ${err.message}` });
      }
    }

    if (successCount > 0) {
      setStatusMessage({
        type: 'success',
        text: `Successfully uploaded & indexed ${successCount} document(s) into ChromaDB.`,
      });
      loadDocuments(selectedKbId);
      loadKnowledgeBases();
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDeleteDoc = async (docId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}" and its vector chunks from ChromaDB?`)) {
      return;
    }
    try {
      await api.deleteDocument(docId);
      setStatusMessage({ type: 'success', text: `Document "${filename}" and its chunks deleted.` });
      loadDocuments(selectedKbId);
      loadKnowledgeBases();
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to delete document.' });
    }
  };

  const handleReindex = async (docId: string, filename: string) => {
    setReindexingId(docId);
    setStatusMessage(null);
    try {
      const updated = await api.reindexDocument(docId);
      setStatusMessage({
        type: 'success',
        text: `Re-indexed "${filename}" successfully (${updated.total_chunks} chunks).`,
      });
      loadDocuments(selectedKbId);
      loadKnowledgeBases();
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Re-indexing failed.' });
    } finally {
      setReindexingId(null);
    }
  };

  const handleCreateKb = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKbName.trim()) return;
    try {
      const created = await api.createKnowledgeBase(newKbName.trim());
      setNewKbName('');
      setShowNewKbModal(false);
      await loadKnowledgeBases();
      setSelectedKbId(created.id);
      setStatusMessage({ type: 'success', text: `Knowledge base "${created.name}" created.` });
    } catch (err: any) {
      alert(err.message || 'Failed to create knowledge base.');
    }
  };

  const totalChunks = documents.reduce((sum, d) => sum + d.total_chunks, 0);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 text-ari-mauve mb-1">
            <BookOpen className="w-5 h-5" />
            <span className="text-xs uppercase font-semibold tracking-wider">Knowledge Base</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-ari-text">
            Documents & Semantic Index
          </h1>
          <p className="text-xs sm:text-sm text-ari-secondary mt-1">
            Manage files stored in SQLite and indexed into persistent ChromaDB vector storage.
          </p>
        </div>

        {/* KB Switcher and Create Button */}
        <div className="flex items-center gap-2.5">
          <select
            value={selectedKbId}
            onChange={(e) => setSelectedKbId(e.target.value)}
            className="text-xs bg-white border border-ari-border rounded-xl px-3 py-2 text-ari-text shadow-sm focus:outline-none focus:ring-1 focus:ring-ari-mauve"
          >
            {kbs.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name} ({kb.document_count} files)
              </option>
            ))}
          </select>

          <button
            onClick={() => setShowNewKbModal(true)}
            className="p-2 bg-white text-ari-mauve rounded-xl border border-ari-border hover:bg-ari-blush/40 transition-colors shadow-sm"
            title="Create new Knowledge Base"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-ari-blush/70 flex items-center justify-center text-ari-mauve border border-ari-mauve/20">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-ari-text">{documents.length}</div>
            <div className="text-xs text-ari-secondary font-medium">Uploaded Documents</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-ari-lavender/70 flex items-center justify-center text-ari-mauve border border-ari-mauve/20">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-ari-text">{totalChunks}</div>
            <div className="text-xs text-ari-secondary font-medium">Total Vector Chunks</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 border border-emerald-200">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-800">Persistent</div>
            <div className="text-xs text-emerald-700 font-medium">ChromaDB Storage</div>
          </div>
        </div>
      </div>

      {/* Status Notice */}
      {statusMessage && (
        <div
          className={`mb-6 p-3.5 rounded-xl text-xs flex items-center gap-2.5 ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border border-rose-200 text-rose-800'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileUpload(e.dataTransfer.files);
        }}
        className="glass-card border-2 border-dashed border-ari-mauve/30 hover:border-ari-mauve rounded-3xl p-8 sm:p-12 text-center cursor-pointer mb-8 transition-all hover:bg-white/90"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
        />
        <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-ari-blush to-ari-lavender flex items-center justify-center mx-auto mb-4 border border-white shadow-subtle">
          <UploadCloud className="w-7 h-7 text-ari-mauve" />
        </div>
        <h3 className="font-serif text-lg font-bold text-ari-text mb-1">
          {uploading ? 'Processing & Indexing Document...' : 'Click to Upload or Drag & Drop'}
        </h3>
        <p className="text-xs text-ari-secondary max-w-sm mx-auto mb-3">
          Supports PDF, Word (DOCX), Plain Text (TXT), and Markdown (MD) up to 25MB.
        </p>
        <span className="inline-block text-[11px] font-semibold text-ari-mauve bg-ari-blush/60 px-3 py-1 rounded-full border border-ari-mauve/20">
          Recursive 800-token chunking • Multilingual E5 Vectors
        </span>
      </div>

      {/* Document List Table */}
      <div className="glass-card rounded-2xl overflow-hidden border border-ari-border shadow-subtle">
        <div className="px-6 py-4 border-b border-ari-border/70 flex items-center justify-between">
          <h3 className="font-serif text-base font-bold text-ari-text">Indexed Documents</h3>
          <button
            onClick={() => loadDocuments(selectedKbId)}
            className="flex items-center gap-1.5 text-xs text-ari-secondary hover:text-ari-text"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-16 text-xs text-ari-secondary">
            No documents in this knowledge base yet. Upload a document above to get started!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-ari-bg/60 text-ari-secondary text-[11px] uppercase tracking-wider border-b border-ari-border/50">
                <tr>
                  <th className="py-3 px-6">Document Name</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Pages / Sections</th>
                  <th className="py-3 px-4">Chroma Chunks</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ari-border/40">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-ari-blush/20 transition-colors">
                    <td className="py-3.5 px-6 font-medium text-ari-text flex items-center gap-2.5">
                      <File className="w-4 h-4 text-ari-mauve shrink-0" />
                      <span className="truncate max-w-[220px]">{doc.filename}</span>
                    </td>
                    <td className="py-3.5 px-4 uppercase text-[10px] font-semibold text-ari-secondary">
                      {doc.file_type}
                    </td>
                    <td className="py-3.5 px-4 text-ari-secondary">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3.5 px-4 text-ari-secondary">{doc.total_pages}</td>
                    <td className="py-3.5 px-4 font-semibold text-ari-text">
                      {doc.total_chunks} chunks
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          doc.status === 'indexed'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : doc.status === 'processing'
                            ? 'bg-amber-50 text-amber-700 border border-amber-200 animate-pulse'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {doc.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleReindex(doc.id, doc.filename)}
                          disabled={reindexingId === doc.id}
                          className="p-1.5 text-ari-secondary hover:text-ari-mauve rounded-lg hover:bg-ari-blush/40 transition-colors"
                          title="Re-index document into ChromaDB"
                        >
                          <RefreshCw
                            className={`w-3.5 h-3.5 ${
                              reindexingId === doc.id ? 'animate-spin text-ari-mauve' : ''
                            }`}
                          />
                        </button>
                        <button
                          onClick={() => handleDeleteDoc(doc.id, doc.filename)}
                          className="p-1.5 text-ari-secondary hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                          title="Delete document and chunks"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Knowledge Base Modal */}
      {showNewKbModal && (
        <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-sm w-full p-6 rounded-2xl border border-ari-border shadow-2xl bg-white animate-fade-in">
            <h3 className="font-serif text-lg font-bold text-ari-text mb-2">
              Create New Knowledge Base
            </h3>
            <p className="text-xs text-ari-secondary mb-4">
              Isolate documents and vector search collections for specific subjects or projects.
            </p>
            <form onSubmit={handleCreateKb} className="space-y-4">
              <input
                type="text"
                placeholder="e.g. Legal Documents, Science Research..."
                value={newKbName}
                onChange={(e) => setNewKbName(e.target.value)}
                autoFocus
                className="w-full text-xs border border-ari-border rounded-xl px-3 py-2 text-ari-text focus:outline-none focus:ring-1 focus:ring-ari-mauve"
              />
              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewKbModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-ari-secondary hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newKbName.trim()}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold ari-button-gradient shadow-sm disabled:opacity-40"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
