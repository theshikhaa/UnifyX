import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Search, RefreshCw, ChevronRight, Database, Mail, Phone, AtSign, Building, Sparkles } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EntitiesRepositoryManager({ onInspectEntity }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  const fetchEntities = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/v1/entities`, {
        params: { page, limit: 15, search: searchTerm || undefined }
      });
      setEntities(res.data.entities || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Error fetching entities list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, [page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchEntities();
  };

  return (
    <div>
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Master Entity Repository</h1>
          <p className="section-desc">
            Browse and inspect all unified master entities created across your multi-database ingestion pipeline.
          </p>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} color="var(--text-secondary)" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input 
              type="text"
              className="form-input"
              style={{ width: '100%', paddingLeft: '2.5rem' }}
              placeholder="Filter master entities by name, email, phone, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-secondary">
            <Search size={16} /> Filter
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => { setSearchTerm(''); setPage(1); fetchEntities(); }}>
            <RefreshCw size={16} /> Reset
          </button>
        </form>
      </div>

      {/* Table / List */}
      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <RefreshCw className="spin" size={24} style={{ marginBottom: '0.5rem' }} />
          <div>Loading master entities repository...</div>
        </div>
      ) : entities.length === 0 ? (
        <div className="empty-state">
          <Users size={40} color="var(--text-secondary)" />
          <h3>No Master Entities Found</h3>
          <p>Process your ingested data sources in the Ingestion tab to generate unified master entities.</p>
        </div>
      ) : (
        <div className="panel-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 className="panel-title" style={{ margin: 0 }}>
              <Users size={18} color="var(--accent-emerald)" />
              Unified Master Entities ({total} Total)
            </h3>
          </div>

          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Master Entity Name</th>
                  <th>Primary Identifiers</th>
                  <th>Linked Sources</th>
                  <th>Updated At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {entities.map((item) => {
                  const prof = item.canonical_profile || {};
                  return (
                    <tr key={item.id}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div className="entity-avatar-sm">
                            {(prof.name || prof.email || 'E')[0].toUpperCase()}
                          </div>
                          <div>
                            <strong style={{ color: 'var(--text-primary)', display: 'block' }}>
                              {prof.name || 'Master Entity'}
                            </strong>
                            <code style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                              ID: #{item.id.slice(0, 8)}
                            </code>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                          {prof.email && <span><Mail size={12} /> {prof.email}</span>}
                          {prof.phone && <span><Phone size={12} /> {prof.phone}</span>}
                          {prof.username && <span><AtSign size={12} /> @{prof.username}</span>}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-info">
                          <Database size={12} /> {item.matched_sources_count} Sources
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {new Date(item.updated_at).toLocaleString()}
                      </td>
                      <td>
                        <button 
                          className="btn btn-secondary btn-sm"
                          onClick={() => onInspectEntity(item.id)}
                        >
                          <Sparkles size={14} color="var(--accent-purple)" /> Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
