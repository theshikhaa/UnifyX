import React, { useState, useEffect } from 'react';
import { X, Table, Eye, CheckCircle, FileText } from 'lucide-react';
import { getSourceDetail } from '../services/api';

export default function SourceInspectModal({ sourceId, sourceName, onClose }) {
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sourceId) return;
    setLoading(true);
    getSourceDetail(sourceId)
      .then((data) => {
        setSchema(data);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch schema detail:", err);
        setError(err.message || "Failed to load source schema details");
      })
      .finally(() => setLoading(false));
  }, [sourceId]);

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Table color="var(--accent-purple)" size={22} />
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: '700' }}>Schema Inspection</h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Source: {sourceName}</p>
            </div>
          </div>
          <button className="icon-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Modal Content */}
        <div className="modal-body">
          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Inspecting dataset structure & columns...
            </div>
          ) : error ? (
            <div className="error-box">{error}</div>
          ) : schema ? (
            <div>
              {/* Columns Overview */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 className="section-subtitle">
                  Detected Columns ({schema.total_columns})
                </h3>
                <div className="columns-grid">
                  {schema.columns.map((col, idx) => (
                    <div key={idx} className="column-card">
                      <div className="column-name">{col.column_name}</div>
                      <div className="column-type">{col.data_type}</div>
                      <div className="column-samples">
                        Sample: {col.sample_values.join(', ') || 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Data Table Preview */}
              <div>
                <h3 className="section-subtitle">Data Preview (Top Rows)</h3>
                <div className="table-responsive">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        {schema.columns.map((col, idx) => (
                          <th key={idx}>{col.column_name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {schema.sample_records.map((row, rIdx) => (
                        <tr key={rIdx}>
                          {schema.columns.map((col, cIdx) => (
                            <td key={cIdx}>
                              {row[col.column_name] !== undefined && row[col.column_name] !== null
                                ? String(row[col.column_name])
                                : <span style={{ color: 'var(--text-muted)', italic: 'true' }}>null</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
