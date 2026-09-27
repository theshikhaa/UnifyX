import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, Eye, FileText, UploadCloud, CheckCircle2, AlertCircle } from 'lucide-react';
import { getSources, uploadSource, deleteSource } from '../services/api';
import SourceInspectModal from './SourceInspectModal';

export default function SourcesManager() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [sourceName, setSourceName] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Inspect modal state
  const [inspectSource, setInspectSource] = useState(null);

  const fetchSourcesList = async () => {
    setLoading(true);
    try {
      const data = await getSources();
      setSources(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load sources:", err);
      setError(err.message || "Failed to load data sources");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSourcesList();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (!sourceName) {
        // Auto derive name from file
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ");
        const formatted = nameWithoutExt.charAt(0).toUpperCase() + nameWithoutExt.slice(1);
        setSourceName(formatted);
      }
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || !sourceName.trim()) return;

    setUploading(true);
    try {
      await uploadSource(sourceName, 'csv', selectedFile);
      setShowUploadModal(false);
      setSourceName('');
      setSelectedFile(null);
      fetchSourcesList();
    } catch (err) {
      console.error("Upload error:", err);
      alert(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (sourceId, name) => {
    if (!window.confirm(`Are you sure you want to delete source "${name}"?`)) return;
    try {
      await deleteSource(sourceId);
      fetchSourcesList();
    } catch (err) {
      console.error("Delete error:", err);
      alert(`Failed to delete source: ${err.message}`);
    }
  };

  return (
    <div>
      {/* Top Action Bar */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Data Sources</h1>
          <p className="section-desc">
            Upload CSV files and SQL databases to inspect schema structures and detect column attributes.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowUploadModal(true)}>
          <Plus size={18} />
          Add Data Source
        </button>
      </div>

      {/* Sources Grid List */}
      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading data sources...
        </div>
      ) : error ? (
        <div className="error-box">{error}</div>
      ) : sources.length === 0 ? (
        <div className="empty-state">
          <Database size={48} color="var(--accent-purple)" style={{ marginBottom: '1rem', opacity: 0.6 }} />
          <h3>No Data Sources Added Yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', maxWidth: '450px' }}>
            Upload your dataset files (HR, Customer, Business, or Membership DBs) to start building canonical field mappings.
          </p>
          <button className="btn btn-primary" onClick={() => setShowUploadModal(true)}>
            <Plus size={18} /> Upload First Dataset
          </button>
        </div>
      ) : (
        <div className="grid-cards">
          {sources.map((src) => (
            <div key={src.id} className="card source-card">
              <div className="source-card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="source-icon">
                    <FileText size={20} color="var(--accent-cyan)" />
                  </div>
                  <div>
                    <h3 className="source-name">{src.source_name}</h3>
                    <span className="source-type">{src.source_type.toUpperCase()} • {src.file_name}</span>
                  </div>
                </div>
                <span className={`status-badge ${src.status}`}>
                  {src.status}
                </span>
              </div>

              {/* Detected Columns Pills */}
              <div style={{ margin: '1rem 0' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 600 }}>
                  DETECTED COLUMNS ({src.total_columns}):
                </div>
                <div className="pills-container">
                  {src.detected_columns.map((col, idx) => (
                    <span key={idx} className="col-pill">{col}</span>
                  ))}
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="source-card-footer">
                <button className="btn btn-secondary btn-sm" onClick={() => setInspectSource(src)}>
                  <Eye size={14} /> Inspect Schema
                </button>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(src.id, src.source_name)}>
                  <Trash2 size={14} /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Dataset Modal */}
      {showUploadModal && (
        <div className="modal-overlay">
          <div className="modal-container" style={{ maxWidth: '540px' }}>
            <div className="modal-header">
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Upload New Dataset</h2>
              <button className="icon-btn" onClick={() => setShowUploadModal(false)}>✕</button>
            </div>

            <form onSubmit={handleUploadSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Data Source Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Customer Database"
                    value={sourceName}
                    onChange={(e) => setSourceName(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group" style={{ marginTop: '1.25rem' }}>
                  <label className="form-label">Select CSV File</label>
                  <div className="file-dropzone">
                    <UploadCloud size={32} color="var(--accent-purple)" />
                    <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}>
                      {selectedFile ? selectedFile.name : "Click to select or drag CSV file"}
                    </p>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange}
                      required={!selectedFile}
                      style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
                    />
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowUploadModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={uploading || !selectedFile}>
                  {uploading ? 'Uploading & Inspecting...' : 'Upload Source'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Inspect Modal */}
      {inspectSource && (
        <SourceInspectModal
          sourceId={inspectSource.id}
          sourceName={inspectSource.source_name}
          onClose={() => setInspectSource(null)}
        />
      )}
    </div>
  );
}
