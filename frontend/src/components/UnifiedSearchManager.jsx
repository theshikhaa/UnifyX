import React, { useState } from 'react';
import { Search, ShieldCheck, Database, Layers, GitBranch, ChevronDown, ChevronUp, UserCheck, Sparkles, Mail, Phone, AtSign, CreditCard, MapPin, Building } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function UnifiedSearchManager({ onInspectEntity }) {
  const [query, setQuery] = useState('john@gmail.com');
  const [loading, setLoading] = useState(false);
  const [searchResult, setSearchResult] = useState(null);
  const [error, setError] = useState(null);
  const [expandedTraceability, setExpandedTraceability] = useState({});

  const executeSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/search`, {
        params: { q: q.trim() }
      });
      setSearchResult(response.data);
    } catch (err) {
      console.error("Search API error:", err);
      setError(err.response?.data?.detail || err.message || "Search failed.");
    } finally {
      setLoading(false);
    }
  };

  const handlePresetSearch = (preset) => {
    setQuery(preset);
    executeSearch(preset);
  };

  const toggleTraceability = (entityId) => {
    setExpandedTraceability((prev) => ({
      ...prev,
      [entityId]: !prev[entityId]
    }));
  };

  return (
    <div>
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Unified Repository Search</h1>
          <p className="section-desc">
            Search across all ingested datasets using any identifier (email, phone, username, member ID, or name) to discover progressively enriched Master Entities.
          </p>
        </div>
      </div>

      {/* Search Input Box */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
        <form onSubmit={(e) => { e.preventDefault(); executeSearch(); }}>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={20} color="var(--text-secondary)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.75rem', fontSize: '1rem' }}
                placeholder="Search by email, phone, username, member ID, or name..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              <Search size={16} />
              {loading ? 'Searching...' : 'Search Entity'}
            </button>
          </div>
        </form>

        {/* Preset Sample Search Pills */}
        <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600 }}>DEMO PRESETS:</span>
          <button className="col-pill" onClick={() => handlePresetSearch('john@gmail.com')}>john@gmail.com</button>
          <button className="col-pill" onClick={() => handlePresetSearch('9876543210')}>9876543210</button>
          <button className="col-pill" onClick={() => handlePresetSearch('johndoe')}>johndoe</button>
          <button className="col-pill" onClick={() => handlePresetSearch('sarah.c@cyberdyne.com')}>sarah.c@cyberdyne.com</button>
          <button className="col-pill" onClick={() => handlePresetSearch('robert@bruce.org')}>robert@bruce.org</button>
        </div>
      </div>

      {/* Error Output */}
      {error && <div className="error-box" style={{ marginBottom: '1.5rem' }}>{error}</div>}

      {/* Search Results */}
      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Executing Progressive Entity Enrichment BFS Search Engine...
        </div>
      ) : searchResult && searchResult.total_results === 0 ? (
        <div className="empty-state">
          <Search size={48} color="var(--accent-purple)" style={{ marginBottom: '1rem', opacity: 0.6 }} />
          <h3>No Matching Master Entities Found</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            No entities matched query "{searchResult.query}". Make sure you have uploaded and ingested datasets in the Ingestion tab.
          </p>
        </div>
      ) : searchResult ? (
        <div>
          <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Found {searchResult.total_results} Master Entity matching query "{searchResult.query}"
          </div>

          {searchResult.entities.map((entity) => (
            <div key={entity.entity_id} className="card master-entity-card" style={{ marginBottom: '1.5rem' }}>
              {/* Header */}
              <div className="entity-card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="entity-avatar">
                    <UserCheck size={24} color="var(--accent-emerald)" />
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="master-badge">MASTER ENTITY #{entity.entity_id.substring(0, 8).toUpperCase()}</span>
                      <span className="status-badge active">{entity.status}</span>
                    </div>
                    <h2 className="entity-name">{entity.name}</h2>
                  </div>
                </div>

                <div className="sources-count-pill">
                  <Database size={14} color="var(--accent-cyan)" />
                  <span>Matched {entity.matched_sources_count} Data Sources</span>
                </div>
              </div>

              {/* Progressive Enrichment Chain */}
              {entity.enrichment_chain && entity.enrichment_chain.length > 0 && (
                <div className="enrichment-chain-box">
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent-purple)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}>
                    <Sparkles size={14} /> PROGRESSIVE ENTITY ENRICHMENT CHAIN:
                  </div>
                  <div className="chain-items">
                    {entity.enrichment_chain.map((item, cIdx) => (
                      <span key={cIdx} className="chain-item">{item}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Consolidated Profile Grid */}
              <div className="profile-grid">
                <div className="profile-field">
                  <div className="field-label"><Mail size={14} /> Email Address</div>
                  <div className="field-value">{entity.email || <span className="null-val">N/A</span>}</div>
                </div>
                <div className="profile-field">
                  <div className="field-label"><Phone size={14} /> Mobile Phone</div>
                  <div className="field-value">{entity.phone || <span className="null-val">N/A</span>}</div>
                </div>
                <div className="profile-field">
                  <div className="field-label"><AtSign size={14} /> Username / Handle</div>
                  <div className="field-value">{entity.username || <span className="null-val">N/A</span>}</div>
                </div>
                <div className="profile-field">
                  <div className="field-label"><CreditCard size={14} /> Member / Account ID</div>
                  <div className="field-value">{entity.member_id || <span className="null-val">N/A</span>}</div>
                </div>
                <div className="profile-field">
                  <div className="field-label"><MapPin size={14} /> Residence Address</div>
                  <div className="field-value">{entity.address || <span className="null-val">N/A</span>}</div>
                </div>
                <div className="profile-field">
                  <div className="field-label"><Building size={14} /> Employer / Company</div>
                  <div className="field-value">{entity.company || <span className="null-val">N/A</span>}</div>
                </div>
              </div>

              {/* Source Traceability Accordion & Deep Inspection Button */}
              <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => toggleTraceability(entity.entity_id)}
                  style={{ flex: 1, justifyContent: 'space-between' }}
                >
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <GitBranch size={16} color="var(--accent-cyan)" />
                    View Traceability ({entity.source_traceability.length} Source Records Linked)
                  </span>
                  {expandedTraceability[entity.entity_id] ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {onInspectEntity && (
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => onInspectEntity(entity.entity_id)}
                    style={{ background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))' }}
                  >
                    <Sparkles size={14} /> Inspect Graph & Lineage
                  </button>
                )}
              </div>

              {/* Expanded Traceability Items */}
              {expandedTraceability[entity.entity_id] && (
                <div className="traceability-drawer">
                  {entity.source_traceability.map((trace, tIdx) => (
                    <div key={tIdx} className="trace-item">
                      <div className="trace-header">
                        <div>
                          <span className="trace-dbname">{trace.source_name}</span>
                          <span className="trace-meta"> (Table: {trace.table_name}, Row: {trace.row_identifier})</span>
                        </div>
                        <span className="trace-matchtype">{trace.match_type} ({(trace.confidence * 100).toFixed(0)}%)</span>
                      </div>

                      <div className="trace-data-grid">
                        <div>
                          <div className="trace-data-title">RAW SOURCE DATA (UN-MUTATED):</div>
                          <pre>{JSON.stringify(trace.raw_data, null, 2)}</pre>
                        </div>
                        <div>
                          <div className="trace-data-title">NORMALIZED CANONICAL FIELDS:</div>
                          <pre>{JSON.stringify(trace.normalized_data, null, 2)}</pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
