import React from 'react';
import { Link } from 'react-router-dom';
import { useGetDocumentsQuery, useGetMeQuery } from '../api/apiSlice';
import { FileText, Search, ShieldCheck, Database, ArrowRight, Clock, PlusCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { data: user } = useGetMeQuery();
  const { data: documents = [], isLoading } = useGetDocumentsQuery();

  const readyDocs = documents.filter((d) => d.status === 'ready');
  const pendingDocs = documents.filter((d) => d.status === 'pending' || d.status === 'processing');
  const totalChunks = documents.reduce((sum, d) => sum + (d.chunk_count || 0), 0);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem 3rem' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '2rem 2.5rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <span className="badge badge-blue" style={{ marginBottom: '0.5rem', display: 'inline-block' }}>User-Isolated RAG Active</span>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.25rem' }}>
            Welcome back, {user?.full_name || 'Counsel'}!
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', fontSize: '0.95rem' }}>
            Manage your legal documents, track asynchronous vector chunking, and run user-scoped hybrid search queries.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/documents" className="btn-primary">
            <PlusCircle size={18} /> Upload Case File
          </Link>
          <Link to="/search" className="btn-secondary">
            <Search size={18} /> AI Research
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-panel glass-panel-interactive" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>Total Documents</p>
              <h3 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '0.25rem' }}>{isLoading ? '...' : documents.length}</h3>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(59, 130, 246, 0.15)' }}>
              <FileText size={24} color="#60a5fa" />
            </div>
          </div>
          <span style={{ fontSize: '0.8rem', color: '#4ade80', display: 'inline-flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.75rem' }}>
            {readyDocs.length} ready for search
          </span>
        </div>

        <div className="glass-panel glass-panel-interactive" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>Embedded Chunks</p>
              <h3 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '0.25rem' }}>{isLoading ? '...' : totalChunks}</h3>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(139, 92, 246, 0.15)' }}>
              <Database size={24} color="#c084fc" />
            </div>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem', display: 'block' }}>
            384-dim HuggingFace vectors
          </span>
        </div>

        <div className="glass-panel glass-panel-interactive" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>Ingestion Queue</p>
              <h3 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '0.25rem' }}>{isLoading ? '...' : pendingDocs.length}</h3>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)' }}>
              <Clock size={24} color="#fbbf24" />
            </div>
          </div>
          <span style={{ fontSize: '0.8rem', color: pendingDocs.length > 0 ? '#fbbf24' : '#4ade80', marginTop: '0.75rem', display: 'block' }}>
            {pendingDocs.length > 0 ? 'RabbitMQ workers processing' : 'Queue idle'}
          </span>
        </div>

        <div className="glass-panel glass-panel-interactive" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>Privacy Protection</p>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '0.5rem', color: '#4ade80' }}>100% Enforced</h3>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(34, 197, 94, 0.15)' }}>
              <ShieldCheck size={24} color="#4ade80" />
            </div>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem', display: 'block' }}>
            Strict SQL metadata scoping
          </span>
        </div>
      </div>

      {/* Recent Documents Table */}
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recent Case Documents</h2>
          <Link to="/documents" style={{ color: '#60a5fa', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            View all ({documents.length}) <ArrowRight size={16} />
          </Link>
        </div>

        {isLoading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading documents...</p>
        ) : documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
            <FileText size={48} color="#475569" style={{ marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>No case documents uploaded yet</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Upload your first legal file or judgement to begin RAG indexing.
            </p>
            <Link to="/documents" className="btn-primary">
              <PlusCircle size={18} /> Upload Document
            </Link>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Title</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Case ID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Chunks</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {documents.slice(0, 5).map((doc) => (
                  <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '1rem', fontWeight: 500 }}>{doc.title}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{doc.case_id || 'N/A'}</td>
                    <td style={{ padding: '1rem' }}>{doc.chunk_count}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`badge ${doc.status === 'ready' ? 'badge-green' : doc.status === 'failed' ? 'badge-amber' : 'badge-blue'}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
