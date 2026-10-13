import React, { useState } from 'react';
import {
  useGetDocumentsQuery,
  useCreateDocumentMutation,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useRetryDocumentMutation,
} from '../api/apiSlice';
import { Upload, FileText, Plus, RefreshCw, Trash2, RotateCcw } from 'lucide-react';

const MAX_FILE_BYTES = 10 * 1024 * 1024;

const formatSize = (bytes: number) =>
  bytes >= 1024 * 1024 ? `${(bytes / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;

export const Documents: React.FC = () => {
  const { data: documents = [], isLoading, refetch } = useGetDocumentsQuery();
  const [createDocument, { isLoading: isCreating }] = useCreateDocumentMutation();
  const [uploadDocument, { isLoading: isUploading }] = useUploadDocumentMutation();
  const busy = isCreating || isUploading;
  const [deleteDocument] = useDeleteDocumentMutation();
  const [retryDocument] = useRetryDocumentMutation();
  // Id of the document whose Delete/Retry request is in flight.
  const [actionId, setActionId] = useState<string | null>(null);

  const handleDelete = async (id: string, docTitle: string) => {
    if (!window.confirm(`Delete "${docTitle}"? This also removes its search data and cannot be undone.`)) return;
    setActionId(id);
    try {
      await deleteDocument(id).unwrap();
    } catch (err: any) {
      alert('Delete failed: ' + (err.data?.detail || 'Unknown error'));
    } finally {
      setActionId(null);
    }
  };

  const handleRetry = async (id: string) => {
    setActionId(id);
    try {
      await retryDocument(id).unwrap();
    } catch (err: any) {
      alert('Retry failed: ' + (err.data?.detail || 'Unknown error'));
    } finally {
      setActionId(null);
    }
  };

  const [mode, setMode] = useState<'pdf' | 'text'>('pdf');
  const [title, setTitle] = useState('');
  const [caseId, setCaseId] = useState('');
  const [rawText, setRawText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    try {
      if (mode === 'pdf') {
        if (!file) {
          setFileError('Please choose a PDF file.');
          return;
        }
        const formData = new FormData();
        formData.append('title', title);
        if (caseId) formData.append('case_id', caseId);
        formData.append('file', file);
        await uploadDocument(formData).unwrap();
        setFile(null);
        setFileError(null);
        const input = (e.target as HTMLFormElement).querySelector<HTMLInputElement>('input[type="file"]');
        if (input) input.value = '';
      } else {
        await createDocument({
          title,
          case_id: caseId || undefined,
          raw_text: rawText,
        }).unwrap();
        setRawText('');
      }
      setTitle('');
      setCaseId('');
      setSuccessMsg('Document uploaded! RabbitMQ worker will chunk and embed it asynchronously.');
    } catch (err: any) {
      alert('Upload failed: ' + (err.data?.detail || 'Unknown error'));
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem 3rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '2rem' }}>
        {/* Upload Form */}
        <div>
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '0.5rem', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)' }}>
                <Upload size={20} color="#60a5fa" />
              </div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Upload Case File</h2>
            </div>

            {successMsg && (
              <div style={{ background: 'rgba(34, 197, 94, 0.15)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '8px', padding: '0.75rem 1rem', color: '#4ade80', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                {successMsg}
              </div>
            )}

            <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Document Title *</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="e.g. Supreme Court Judgement 2024 - Contract Dispute"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Case ID / Reference (Optional)</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. CASE-2024-884"
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setMode('pdf')}
                  className={mode === 'pdf' ? 'btn-primary' : 'btn-secondary'}
                  style={{ flex: 1, justifyContent: 'center', padding: '0.5rem', fontSize: '0.85rem' }}
                >
                  Upload PDF
                </button>
                <button
                  type="button"
                  onClick={() => setMode('text')}
                  className={mode === 'text' ? 'btn-primary' : 'btn-secondary'}
                  style={{ flex: 1, justifyContent: 'center', padding: '0.5rem', fontSize: '0.85rem' }}
                >
                  Paste text
                </button>
              </div>

              {mode === 'pdf' ? (
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>PDF File * (max 10 MB)</label>
                  <input
                    type="file"
                    accept="application/pdf,.pdf"
                    className="input-field"
                    onChange={(e) => {
                      setFileError(null);
                      const f = e.target.files?.[0] ?? null;
                      if (f && f.size > MAX_FILE_BYTES) {
                        setFile(null);
                        setFileError('File is too large (max 10 MB).');
                        return;
                      }
                      setFile(f);
                    }}
                  />
                  {file && (
                    <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {file.name} ({formatSize(file.size)})
                    </p>
                  )}
                  {fileError && (
                    <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#f87171' }}>{fileError}</p>
                  )}
                </div>
              ) : (
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Case Text Content *</label>
                  <textarea
                    required
                    rows={8}
                    className="input-field"
                    placeholder="Paste legal document text, judgement, petition, or contract clauses here..."
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value)}
                    style={{ fontFamily: 'inherit', resize: 'vertical' }}
                  />
                </div>
              )}

              <button type="submit" disabled={busy} className="btn-primary" style={{ justifyContent: 'center', padding: '0.8rem' }}>
                {busy ? 'Publishing Ingestion Job...' : <><Plus size={18} /> Queue Ingestion Job</>}
              </button>
            </form>
          </div>
        </div>

        {/* Documents List */}
        <div>
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <FileText size={20} color="#c084fc" />
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Your Documents ({documents.length})</h2>
              </div>
              <button onClick={() => refetch()} className="btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
                <RefreshCw size={14} /> Refresh Status
              </button>
            </div>

            {isLoading ? (
              <p style={{ color: 'var(--text-muted)' }}>Loading documents...</p>
            ) : documents.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                <FileText size={40} style={{ marginBottom: '0.75rem', opacity: 0.5 }} />
                <p>No documents uploaded yet. Use the form on the left to add legal documents.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {documents.map((doc) => (
                  <div key={doc.id} className="glass-panel" style={{ padding: '1.25rem', borderRadius: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.25rem' }}>{doc.title}</h4>
                        {doc.source_filename && (
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>{doc.source_filename}</p>
                        )}
                        {doc.case_id && (
                          <span style={{ fontSize: '0.8rem', color: '#93c5fd', background: 'rgba(59, 130, 246, 0.15)', padding: '0.1rem 0.5rem', borderRadius: '4px', display: 'inline-block', marginBottom: '0.5rem' }}>
                            Case: {doc.case_id}
                          </span>
                        )}
                      </div>
                      <span className={`badge ${doc.status === 'ready' ? 'badge-green' : doc.status === 'failed' ? 'badge-amber' : 'badge-blue'}`}>
                        {doc.status}
                      </span>
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1.5rem', marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <span>Chunks: <strong style={{ color: '#fff' }}>{doc.chunk_count}</strong></span>
                      <span>Created: {new Date(doc.created_at).toLocaleDateString()}</span>
                      <div style={{ display: 'flex', gap: '0.5rem', marginLeft: 'auto' }}>
                        {doc.status === 'failed' && (
                          <button
                            type="button"
                            onClick={() => handleRetry(doc.id)}
                            disabled={actionId === doc.id}
                            className="btn-secondary"
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                          >
                            <RotateCcw size={13} /> Retry
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => handleDelete(doc.id, doc.title)}
                          disabled={actionId === doc.id}
                          className="btn-secondary"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', color: '#fca5a5' }}
                          aria-label={`Delete ${doc.title}`}
                        >
                          <Trash2 size={13} /> Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
