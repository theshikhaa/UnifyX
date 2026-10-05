import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  X, Database, GitBranch, AlertTriangle, ShieldCheck, 
  Layers, Clock, ArrowRight, User, Mail, Phone, AtSign, 
  Building, MapPin, CheckCircle2, RefreshCw
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EntityDetailModal({ entityId, onClose }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!entityId) return;
    fetchEntityDetail();
  }, [entityId]);

  const fetchEntityDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/v1/entities/${entityId}`);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching entity detail:", err);
      setError(err.response?.data?.detail || "Failed to load entity details");
    } finally {
      setLoading(false);
    }
  };

  if (!entityId) return null;

  const profile = data?.canonical_profile || {};

  return (
    <div className="modal-backdrop">
      <div className="modal-container entity-detail-modal">
        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="entity-avatar">
              {(profile.name || profile.email || 'E')[0].toUpperCase()}
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
                {profile.name || 'Unified Master Entity'}
              </h2>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.2rem' }}>
                <code>ID: {entityId}</code>
                <span className="badge badge-success">ACTIVE</span>
                <span>• {data?.source_traceability?.length || 0} Linked Sources</span>
              </div>
            </div>
          </div>
          <button className="icon-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="modal-tabs">
          <button 
            className={`modal-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <User size={15} /> Overview Profile
          </button>
          <button 
            className={`modal-tab ${activeTab === 'traceability' ? 'active' : ''}`}
            onClick={() => setActiveTab('traceability')}
          >
            <Database size={15} /> Source Traceability ({data?.source_traceability?.length || 0})
          </button>
          <button 
            className={`modal-tab ${activeTab === 'conflicts' ? 'active' : ''}`}
            onClick={() => setActiveTab('conflicts')}
          >
            <AlertTriangle size={15} /> 
            Conflicts ({data?.attribute_conflicts?.length || 0})
          </button>
          <button 
            className={`modal-tab ${activeTab === 'graph' ? 'active' : ''}`}
            onClick={() => setActiveTab('graph')}
          >
            <GitBranch size={15} /> Relationship Graph
          </button>
          <button 
            className={`modal-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <Clock size={15} /> Audit History
          </button>
        </div>

        {/* Modal Content */}
        <div className="modal-body">
          {loading && (
            <div className="loading-state" style={{ padding: '3rem 0' }}>
              <RefreshCw className="spin" size={28} color="var(--accent-purple)" />
              <p>Fetching master entity lineage and progressive links...</p>
            </div>
          )}

          {error && (
            <div className="error-state" style={{ padding: '2rem 0' }}>
              <AlertTriangle size={32} color="var(--accent-rose)" />
              <p>{error}</p>
              <button className="btn btn-secondary" onClick={fetchEntityDetail}>Retry</button>
            </div>
          )}

          {!loading && !error && data && (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div>
                  <div className="attribute-grid">
                    <div className="attribute-card">
                      <div className="attr-label"><User size={14} /> Full Name</div>
                      <div className="attr-val">{profile.name || 'Not Available'}</div>
                    </div>
                    <div className="attribute-card">
                      <div className="attr-label"><Mail size={14} /> Primary Email</div>
                      <div className="attr-val">{profile.email ? <code>{profile.email}</code> : 'Not Available'}</div>
                    </div>
                    <div className="attribute-card">
                      <div className="attr-label"><Phone size={14} /> Mobile / Contact</div>
                      <div className="attr-val">{profile.phone ? <code>{profile.phone}</code> : 'Not Available'}</div>
                    </div>
                    <div className="attribute-card">
                      <div className="attr-label"><AtSign size={14} /> Username</div>
                      <div className="attr-val">{profile.username ? <code>@{profile.username}</code> : 'Not Available'}</div>
                    </div>
                    <div className="attribute-card">
                      <div className="attr-label"><Building size={14} /> Company / Organization</div>
                      <div className="attr-val">{profile.company || 'Not Available'}</div>
                    </div>
                    <div className="attribute-card">
                      <div className="attr-label"><MapPin size={14} /> Address / City</div>
                      <div className="attr-val">{profile.address || 'Not Available'}</div>
                    </div>
                  </div>

                  {/* Discovered Identifiers */}
                  <div style={{ marginTop: '1.5rem' }}>
                    <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Discovered Identifiers (BFS Queue Keys)
                    </h4>
                    <div className="identifier-chips">
                      {data.identifiers.map((id, idx) => (
                        <div key={idx} className="identifier-chip">
                          <span className="id-type">{id.type}</span>
                          <span className="id-val">{id.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: SOURCE TRACEABILITY */}
              {activeTab === 'traceability' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {data.source_traceability.map((item, idx) => (
                    <div key={idx} className="traceability-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span className="source-tag">{item.source_name}</span>
                          <span className="badge badge-info">{item.source_type}</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            Table: <code>{item.record.table_name}</code> | Row #{item.record.row_identifier}
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span className="badge badge-success">Match: {item.match_type}</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                            {Math.round(item.confidence * 100)}% Confidence
                          </span>
                        </div>
                      </div>

                      {/* Raw vs Normalized Data comparison */}
                      <div className="code-comparison-grid">
                        <div>
                          <div className="code-title">Original Raw Record</div>
                          <pre className="code-block">{JSON.stringify(item.record.raw_data, null, 2)}</pre>
                        </div>
                        <div>
                          <div className="code-title">Normalized Attributes</div>
                          <pre className="code-block">{JSON.stringify(item.record.normalized_data, null, 2)}</pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 3: CONFLICTS */}
              {activeTab === 'conflicts' && (
                <div>
                  {data.attribute_conflicts.length === 0 ? (
                    <div className="empty-state" style={{ padding: '2rem 0' }}>
                      <ShieldCheck size={40} color="var(--accent-emerald)" />
                      <h3>No Attribute Conflicts Detected</h3>
                      <p>All ingested data sources are perfectly harmonized for this entity.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {data.attribute_conflicts.map((conflict, idx) => (
                        <div key={idx} className="conflict-card">
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--accent-amber)' }}>
                            <AlertTriangle size={18} />
                            <strong>Conflicting Field: <code>{conflict.attribute_name}</code></strong>
                          </div>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                            {conflict.values.map((val, vIdx) => (
                              <div key={vIdx} className="conflict-value-box">
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Option {vIdx + 1}</div>
                                <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', margin: '0.2rem 0' }}>
                                  "{val.normalized_value}"
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                  Raw: {val.raw_value}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 4: RELATIONSHIP GRAPH */}
              {activeTab === 'graph' && (
                <div>
                  <div className="graph-container-box">
                    <div className="graph-legend">
                      <span className="legend-item"><span className="dot dot-master"></span> Master Entity</span>
                      <span className="legend-item"><span className="dot dot-source"></span> Data Source</span>
                      <span className="legend-item"><span className="dot dot-identifier"></span> Identifier</span>
                    </div>

                    <div className="graph-visual-nodes">
                      {/* Master Node */}
                      <div className="graph-node node-master">
                        <User size={20} />
                        <div>
                          <strong>{profile.name || 'Master Entity'}</strong>
                          <div style={{ fontSize: '0.7rem' }}>ID: #{entityId.slice(0, 8)}</div>
                        </div>
                      </div>

                      {/* Connection Lines & Children */}
                      <div className="graph-branches">
                        {data.relationship_graph.nodes
                          .filter(n => n.type !== 'master')
                          .map((node, idx) => (
                            <div key={idx} className={`graph-node node-${node.type}`}>
                              {node.type === 'source' ? <Database size={14} /> : <Layers size={14} />}
                              <span>{node.label}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: AUDIT HISTORY */}
              {activeTab === 'history' && (
                <div className="timeline-container">
                  {data.audit_history.map((evt, idx) => (
                    <div key={idx} className="timeline-item">
                      <div className="timeline-dot"></div>
                      <div className="timeline-content">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <strong style={{ color: 'var(--accent-cyan)' }}>{evt.action}</strong>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {new Date(evt.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          {evt.detail}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
