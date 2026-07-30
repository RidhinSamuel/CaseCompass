import React, { useState } from 'react';
import { useGetDocumentsQuery, useCreateDocumentMutation } from '../api/apiSlice';
import { Upload, FileText, CheckCircle2, Clock, AlertTriangle, Plus, RefreshCw } from 'lucide-react';

export const Documents: React.FC = () => {
  const { data: documents = [], isLoading, refetch } = useGetDocumentsQuery();
  const [createDocument, { isLoading: isCreating }] = useCreateDocumentMutation();

  const [title, setTitle] = useState('');
  const [caseId, setCaseId] = useState('');
  const [rawText, setRawText] = useState('');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    try {
      await createDocument({
        title,
        case_id: caseId || undefined,
        raw_text: rawText,
      }).unwrap();
      setTitle('');
      setCaseId('');
      setRawText('');
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

              <button type="submit" disabled={isCreating} className="btn-primary" style={{ justifyContent: 'center', padding: '0.8rem' }}>
                {isCreating ? 'Publishing Ingestion Job...' : <><Plus size={18} /> Queue Ingestion Job</>}
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

                    <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <span>Chunks: <strong style={{ color: '#fff' }}>{doc.chunk_count}</strong></span>
                      <span>Created: {new Date(doc.created_at).toLocaleDateString()}</span>
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
