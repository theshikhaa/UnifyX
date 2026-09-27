import React, { useState, useEffect } from 'react';
import { GitMerge, CheckCircle2, ArrowRight, ShieldCheck, Sparkles, RefreshCw, AlertCircle, Database } from 'lucide-react';
import { getSources, getCanonicalFields, getSourceMappings, approveMappings } from '../services/api';

export default function FieldMappingManager() {
  const [sources, setSources] = useState([]);
  const [selectedSourceId, setSelectedSourceId] = useState('');
  const [canonicalFields, setCanonicalFields] = useState([]);
  
  const [mappingOverview, setMappingOverview] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    loadSourcesAndCanonicalFields();
  }, []);

  const loadSourcesAndCanonicalFields = async () => {
    try {
      const [srcList, fields] = await Promise.all([
        getSources(),
        getCanonicalFields()
      ]);
      setSources(srcList);
      setCanonicalFields(fields);

      if (srcList.length > 0 && !selectedSourceId) {
        setSelectedSourceId(srcList[0].id);
      }
    } catch (err) {
      console.error("Failed to load mapping initialization data:", err);
      setError("Failed to load data sources or canonical fields.");
    }
  };

  useEffect(() => {
    if (!selectedSourceId) return;
    fetchMappingProposals(selectedSourceId);
  }, [selectedSourceId]);

  const fetchMappingProposals = async (sourceId) => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const data = await getSourceMappings(sourceId);
      setMappingOverview(data);
      setProposals(data.proposals || []);
    } catch (err) {
      console.error("Failed to load mappings:", err);
      setError(err.message || "Failed to load field mapping proposals.");
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (rawCol, newCanonical) => {
    setProposals((prev) =>
      prev.map((p) =>
        p.raw_column_name === rawCol
          ? { ...p, suggested_canonical_field: newCanonical, is_approved: true }
          : p
      )
    );
  };

  const handleApprovalToggle = (rawCol) => {
    setProposals((prev) =>
      prev.map((p) =>
        p.raw_column_name === rawCol ? { ...p, is_approved: !p.is_approved } : p
      )
    );
  };

  const handleApproveAllSubmit = async () => {
    if (!selectedSourceId) return;

    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    const updatesPayload = proposals.map((p) => ({
      raw_column_name: p.raw_column_name,
      canonical_field: p.suggested_canonical_field || "ignore",
      is_approved: true,
    }));

    try {
      const updatedOverview = await approveMappings(selectedSourceId, updatesPayload);
      setMappingOverview(updatedOverview);
      setProposals(updatedOverview.proposals || []);
      setSuccessMessage("Column mappings successfully approved and saved! Source status updated to MAPPED.");
      
      // Refresh sources list status
      const srcList = await getSources();
      setSources(srcList);
    } catch (err) {
      console.error("Failed to save mappings:", err);
      setError(err.message || "Failed to approve column mappings.");
    } finally {
      setSaving(false);
    }
  };

  const currentSource = sources.find((s) => s.id === selectedSourceId);

  return (
    <div>
      {/* Top Header */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Automatic Field Mapping</h1>
          <p className="section-desc">
            Map heterogeneous dataset columns (`email_id`, `contact_no`, `full_name`) to standardized system canonical fields.
          </p>
        </div>
      </div>

      {/* Source Selector Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Database size={20} color="var(--accent-purple)" />
            <label className="form-label" style={{ margin: 0, fontWeight: 700 }}>
              Select Data Source:
            </label>
            <select
              className="form-input"
              style={{ minWidth: '260px' }}
              value={selectedSourceId}
              onChange={(e) => setSelectedSourceId(e.target.value)}
              disabled={sources.length === 0}
            >
              {sources.length === 0 ? (
                <option value="">No Data Sources Uploaded Yet</option>
              ) : (
                sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.source_name} ({s.file_name})
                  </option>
                ))
              )}
            </select>
          </div>

          {currentSource && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span className="source-type">{currentSource.source_type.toUpperCase()}</span>
              <span className={`status-badge ${currentSource.status}`}>
                {currentSource.status}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts */}
      {error && <div className="error-box" style={{ marginBottom: '1.5rem' }}>{error}</div>}
      {successMessage && (
        <div className="success-box" style={{ marginBottom: '1.5rem' }}>
          <CheckCircle2 size={18} color="var(--accent-emerald)" />
          {successMessage}
        </div>
      )}

      {/* Mapping Body */}
      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Analyzing column structure & executing rule + AI pattern matching engines...
        </div>
      ) : sources.length === 0 ? (
        <div className="empty-state">
          <GitMerge size={48} color="var(--accent-purple)" style={{ marginBottom: '1rem', opacity: 0.6 }} />
          <h3>No Data Source Selected</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Please upload a CSV data source in the Data Sources tab first.</p>
        </div>
      ) : (
        <div>
          {/* Proposals Table */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div className="table-responsive">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Source Column</th>
                    <th>Sample Data Values</th>
                    <th>Suggested Canonical Field</th>
                    <th>Confidence</th>
                    <th>Matching Reason / Strategy</th>
                    <th style={{ textAlign: 'center' }}>Approve</th>
                  </tr>
                </thead>
                <tbody>
                  {proposals.map((prop, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                        {prop.raw_column_name}
                      </td>
                      <td>
                        <span className="sample-text">
                          {prop.sample_values.slice(0, 2).join(', ') || 'N/A'}
                        </span>
                      </td>
                      <td>
                        <select
                          className="form-input"
                          style={{ padding: '0.4rem 0.65rem', fontSize: '0.85rem' }}
                          value={prop.suggested_canonical_field || "ignore"}
                          onChange={(e) => handleFieldChange(prop.raw_column_name, e.target.value)}
                        >
                          {canonicalFields.map((field) => (
                            <option key={field} value={field}>
                              {field === 'ignore' ? '🚫 Ignore Column' : `📌 ${field}`}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span
                          className="confidence-badge"
                          style={{
                            background:
                              prop.confidence >= 0.95
                                ? 'rgba(16, 185, 129, 0.15)'
                                : 'rgba(245, 158, 11, 0.15)',
                            color:
                              prop.confidence >= 0.95
                                ? 'var(--accent-emerald)'
                                : 'var(--accent-amber)',
                          }}
                        >
                          {Math.round(prop.confidence * 100)}%
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {prop.mapping_type === 'ai' ? (
                          <span style={{ color: 'var(--accent-purple)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                            <Sparkles size={13} /> {prop.reason}
                          </span>
                        ) : (
                          <span>{prop.reason}</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <input
                          type="checkbox"
                          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                          checked={prop.is_approved}
                          onChange={() => handleApprovalToggle(prop.raw_column_name)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Action Footer */}
          <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {proposals.filter((p) => p.is_approved).length} of {proposals.length} columns approved.
            </div>

            <button
              className="btn btn-primary"
              onClick={handleApproveAllSubmit}
              disabled={saving || proposals.length === 0}
            >
              <ShieldCheck size={18} />
              {saving ? 'Saving Mappings...' : 'Approve Field Mappings'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
