import React, { useState, useEffect } from 'react';
import { Play, CheckCircle2, Database, ArrowRight, Layers, Sparkles, AlertCircle, RefreshCw, Cpu } from 'lucide-react';
import { getSources, approveMappings } from '../services/api';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ImportProcessingManager() {
  const [sources, setSources] = useState([]);
  const [selectedSourceId, setSelectedSourceId] = useState('');
  
  const [processing, setProcessing] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState(null);
  const [pipelineStep, setPipelineStep] = useState('idle'); // idle, cleaning, matching, enriching, completed

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const data = await getSources();
      setSources(data);
      if (data.length > 0 && !selectedSourceId) {
        setSelectedSourceId(data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch sources:", err);
      setError("Failed to load data sources.");
    }
  };

  const handleProcessSingle = async () => {
    if (!selectedSourceId) return;

    setProcessing(true);
    setError(null);
    setBatchResult(null);
    setPipelineStep('cleaning');

    try {
      setTimeout(() => setPipelineStep('matching'), 400);
      setTimeout(() => setPipelineStep('enriching'), 800);

      const response = await axios.post(`${API_BASE_URL}/api/v1/imports/${selectedSourceId}/process`);
      
      setBatchResult(response.data);
      setPipelineStep('completed');
      fetchSources();
    } catch (err) {
      console.error("Ingestion processing error:", err);
      setError(err.response?.data?.detail || err.message || "Ingestion processing failed.");
      setPipelineStep('idle');
    } finally {
      setProcessing(false);
    }
  };

  const handleProcessAllDemoDatasets = async () => {
    setProcessing(true);
    setError(null);
    setBatchResult(null);

    try {
      // Fetch fresh sources list
      const currentSources = await getSources();
      if (currentSources.length === 0) {
        throw new Error("No datasets uploaded yet. Please upload datasets in the Data Sources tab first.");
      }

      let totalProc = 0;
      let totalMatched = 0;
      let totalNew = 0;

      for (let i = 0; i < currentSources.length; i++) {
        const src = currentSources[i];
        setPipelineStep(`Processing dataset ${i + 1} of ${currentSources.length}: ${src.source_name}...`);
        
        // Ensure default mappings are approved if needed
        try {
          const mapRes = await axios.get(`${API_BASE_URL}/api/v1/mappings/${src.id}`);
          const proposals = mapRes.data.proposals || [];
          const updates = proposals.map((p) => ({
            raw_column_name: p.raw_column_name,
            canonical_field: p.suggested_canonical_field || "ignore",
            is_approved: True
          }));
          await axios.post(`${API_BASE_URL}/api/v1/mappings/${src.id}/approve`, updates);
        } catch (e) {
          // ignore mapping prep error
        }

        const res = await axios.post(`${API_BASE_URL}/api/v1/imports/${src.id}/process`);
        totalProc += res.data.processed_records;
        totalMatched += res.data.matched_records;
        totalNew += res.data.new_entities;
      }

      setBatchResult({
        message: `Successfully processed all ${currentSources.length} datasets!`,
        total_records: totalProc,
        processed_records: totalProc,
        matched_records: totalMatched,
        new_entities: totalNew,
        status: "completed"
      });

      setPipelineStep('completed');
      fetchSources();
    } catch (err) {
      console.error("Process all error:", err);
      setError(err.message || "Failed to process datasets.");
      setPipelineStep('idle');
    } finally {
      setProcessing(false);
    }
  };

  const currentSource = sources.find((s) => s.id === selectedSourceId);

  return (
    <div>
      {/* Top Header */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Ingestion & Matching Pipeline</h1>
          <p className="section-desc">
            Clean raw data, normalize identifiers, match records against existing Master Entities, and perform progressive entity enrichment.
          </p>
        </div>
      </div>

      {/* Selector & Control Panel */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Database size={20} color="var(--accent-purple)" />
            <label className="form-label" style={{ margin: 0, fontWeight: 700 }}>
              Dataset to Process:
            </label>
            <select
              className="form-input"
              style={{ minWidth: '260px' }}
              value={selectedSourceId}
              onChange={(e) => setSelectedSourceId(e.target.value)}
              disabled={processing || sources.length === 0}
            >
              {sources.length === 0 ? (
                <option value="">No Sources Available</option>
              ) : (
                sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.source_name} ({s.status})
                  </option>
                ))
              )}
            </select>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleProcessSingle}
              disabled={processing || !selectedSourceId}
            >
              <Play size={16} />
              {processing ? 'Processing Ingestion...' : 'Run Pipeline for Selected Dataset'}
            </button>
          </div>
        </div>
      </div>

      {/* Visual Pipeline Stage Indicator */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="section-subtitle">Execution Pipeline Lifecycle</h3>
        <div className="pipeline-steps">
          <div className={`pipeline-step ${pipelineStep !== 'idle' ? 'completed' : ''}`}>
            <span className="step-num">1</span> Upload & Inspect
          </div>
          <ArrowRight size={14} color="var(--text-muted)" />
          <div className={`pipeline-step ${pipelineStep !== 'idle' ? 'completed' : ''}`}>
            <span className="step-num">2</span> Field Mapping
          </div>
          <ArrowRight size={14} color="var(--text-muted)" />
          <div className={`pipeline-step ${['cleaning', 'matching', 'enriching', 'completed'].includes(pipelineStep) ? 'active' : ''}`}>
            <span className="step-num">3</span> Data Cleaning
          </div>
          <ArrowRight size={14} color="var(--text-muted)" />
          <div className={`pipeline-step ${['matching', 'enriching', 'completed'].includes(pipelineStep) ? 'active' : ''}`}>
            <span className="step-num">4</span> Exact Matching
          </div>
          <ArrowRight size={14} color="var(--text-muted)" />
          <div className={`pipeline-step ${['enriching', 'completed'].includes(pipelineStep) ? 'active' : ''}`}>
            <span className="step-num">5</span> Enrich Master Entities
          </div>
        </div>
      </div>

      {/* Error & Batch Result Display */}
      {error && <div className="error-box" style={{ marginBottom: '1.5rem' }}>{error}</div>}

      {batchResult && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-emerald)', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <CheckCircle2 size={24} color="var(--accent-emerald)" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Processing Batch Completed</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{batchResult.message}</p>
            </div>
          </div>

          <div className="grid-cards" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
            <div className="stat-subcard">
              <div className="stat-label">Total Records</div>
              <div className="stat-val">{batchResult.total_records}</div>
            </div>
            <div className="stat-subcard">
              <div className="stat-label">Matched to Existing Entities</div>
              <div className="stat-val" style={{ color: 'var(--accent-cyan)' }}>{batchResult.matched_records}</div>
            </div>
            <div className="stat-subcard">
              <div className="stat-label">New Master Entities Created</div>
              <div className="stat-val" style={{ color: 'var(--accent-emerald)' }}>{batchResult.new_entities}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
