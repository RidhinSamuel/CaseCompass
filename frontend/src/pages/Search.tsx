import React, { useState } from 'react';
import { useSearchCasesMutation, useGetDocumentsQuery } from '../api/apiSlice';
import { Search as SearchIcon, Bot, BookOpen, Filter, CheckCircle, Sparkles } from 'lucide-react';

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [topK, setTopK] = useState(5);

  const { data: documents = [] } = useGetDocumentsQuery();
  const [searchCases, { data: searchResult, isLoading, error }] = useSearchCasesMutation();

  const caseIds = Array.from(new Set(documents.map((d) => d.case_id).filter(Boolean)));

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    await searchCases({
      query,
      case_id: selectedCaseId || undefined,
      top_k: Number(topK),
    });
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 1rem 3rem' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <div style={{ display: 'inline-flex', padding: '0.75rem', borderRadius: '14px', background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))', marginBottom: '1rem' }}>
          <Sparkles size={32} color="#93c5fd" />
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 700 }}>AI Judicial Research Assistant</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', maxWidth: '600px', margin: '0.5rem auto 0', fontSize: '0.95rem' }}>
          Perform hybrid vector + keyword search over your user-isolated legal documents and synthesize cited answers.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
        <form onSubmit={handleSearch}>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem' }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <input
                type="text"
                required
                className="input-field"
                placeholder="Ask a legal question (e.g. What are the requirements for breach of contract remedies?)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{ paddingLeft: '2.75rem', fontSize: '1.05rem', padding: '0.85rem 1rem 0.85rem 2.75rem' }}
              />
              <SearchIcon size={20} color="#94a3b8" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary" style={{ padding: '0 1.75rem', fontSize: '1rem' }}>
              {isLoading ? 'Searching...' : 'Run Search'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Filter size={14} color="#60a5fa" />
              <span>Filter Case ID:</span>
              <select
                className="input-field"
                value={selectedCaseId}
                onChange={(e) => setSelectedCaseId(e.target.value)}
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem', width: 'auto' }}
              >
                <option value="">All My Cases</option>
                {caseIds.map((cid) => (
                  <option key={cid} value={cid!}>{cid}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Top K Chunks:</span>
              <select
                className="input-field"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem', width: 'auto' }}
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Error state */}
      {error && (
        <div className="glass-panel" style={{ padding: '1.5rem', borderColor: 'rgba(239, 68, 68, 0.4)', color: '#fca5a5', marginBottom: '2rem' }}>
          Error performing search: {(error as any).data?.detail || 'Failed to connect to backend RAG pipeline'}
        </div>
      )}

      {/* Results View */}
      {searchResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Generated Answer Card */}
          <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid #3b82f6' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.5rem', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.2)' }}>
                <Bot size={22} color="#60a5fa" />
              </div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Synthesized RAG Answer</h2>
            </div>
            <p style={{ lineHeight: 1.7, fontSize: '1.05rem', color: '#e2e8f0', whiteSpace: 'pre-line' }}>
              {searchResult.answer}
            </p>
          </div>

          {/* Retrieved Chunks Card */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <BookOpen size={20} color="#c084fc" />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Retrieved Context Chunks ({searchResult.hits.length})</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {searchResult.hits.map((hit, idx) => (
                <div key={hit.chunk_id} className="glass-panel" style={{ padding: '1.25rem', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', fontSize: '0.85rem' }}>
                    <span style={{ fontWeight: 600, color: '#60a5fa' }}>
                      [{idx + 1}] {hit.document_title}
                    </span>
                    <span className="badge badge-blue">
                      Score: {(hit.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p style={{ fontSize: '0.92rem', color: '#cbd5e1', lineHeight: 1.5, background: 'rgba(0, 0, 0, 0.2)', padding: '0.75rem', borderRadius: '6px' }}>
                    "{hit.content}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
