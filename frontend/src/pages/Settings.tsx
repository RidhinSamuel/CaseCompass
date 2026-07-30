import React, { useState } from 'react';
import { useGetMeQuery } from '../api/apiSlice';
import { Settings as SettingsIcon, User, Shield, Cpu, Moon, Sun } from 'lucide-react';

export const Settings: React.FC = () => {
  const { data: user } = useGetMeQuery();

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '0 1rem 3rem' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '8px', background: 'rgba(139, 92, 246, 0.15)' }}>
            <SettingsIcon size={22} color="#c084fc" />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Account & System Settings</h1>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* User Profile */}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <User size={18} color="#60a5fa" /> Profile Details
            </h3>
            <div className="glass-panel" style={{ padding: '1.25rem', background: 'rgba(15, 23, 42, 0.4)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '0.75rem', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Name:</span>
                <span style={{ fontWeight: 500 }}>{user?.full_name || 'N/A'}</span>
                <span style={{ color: 'var(--text-muted)' }}>Email:</span>
                <span style={{ fontWeight: 500 }}>{user?.email}</span>
                <span style={{ color: 'var(--text-muted)' }}>Account ID:</span>
                <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#94a3b8' }}>{user?.id}</span>
              </div>
            </div>
          </div>

          {/* Model Config */}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Cpu size={18} color="#c084fc" /> Active RAG Models
            </h3>
            <div className="glass-panel" style={{ padding: '1.25rem', background: 'rgba(15, 23, 42, 0.4)' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Embeddings:</span>
                  <span className="badge badge-blue">sentence-transformers/all-MiniLM-L6-v2</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>LLM Model:</span>
                  <span className="badge badge-green">google/flan-t5-base</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Vector Store:</span>
                  <span>PostgreSQL 16 + pgvector (384 dims)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={18} color="#4ade80" /> Data Isolation
            </h3>
            <div className="glass-panel" style={{ padding: '1.25rem', background: 'rgba(15, 23, 42, 0.4)', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              All documents, chunk embeddings, and search queries are strictly isolated to user ID <strong style={{ color: '#fff' }}>{user?.id}</strong>. Multi-tenant SQL filters guarantee cross-user data boundaries.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
