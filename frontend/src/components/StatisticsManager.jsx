import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Database, Users, GitMerge, CheckCircle2, AlertCircle, 
  RefreshCw, TrendingUp, Layers, PlayCircle, ShieldCheck
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function StatisticsManager({ onNavigateToUpload, onNavigateToProcessing }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/v1/statistics`);
      setStats(res.data);
    } catch (err) {
      console.error("Error fetching system stats:", err);
      setError("Failed to load real-time processing statistics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div>
      {/* Hero Header */}
      <section className="hero-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="hero-title">
              Unified Data & <span className="gradient-text">Resolution Dashboard</span>
            </h1>
            <p className="hero-description">
              Real-time monitoring of multi-database ingestion, progressive entity resolution metrics, match rates, and dataset contributions.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-secondary" onClick={fetchStats} disabled={loading}>
              <RefreshCw className={loading ? 'spin' : ''} size={16} /> Refresh
            </button>
            <button className="btn btn-primary" onClick={onNavigateToUpload}>
              <Database size={16} /> Upload New Dataset
            </button>
          </div>
        </div>
      </section>

      {/* KPI Cards Grid */}
      <div className="grid-cards" style={{ marginBottom: '2.5rem' }}>
        <div className="stat-card">
          <div className="stat-header">
            <Database color="var(--accent-purple)" size={22} />
            <span className="stat-label">Total Data Sources</span>
          </div>
          <div className="stat-number">{stats?.total_sources || 0}</div>
          <div className="stat-subtext">Uploaded CSV & Database Schemas</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Layers color="var(--accent-blue)" size={22} />
            <span className="stat-label">Raw Records Ingested</span>
          </div>
          <div className="stat-number">{(stats?.processed_records || 0).toLocaleString()}</div>
          <div className="stat-subtext">Normalized & Field Mapped</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Users color="var(--accent-emerald)" size={22} />
            <span className="stat-label">Unified Master Entities</span>
          </div>
          <div className="stat-number">{(stats?.total_master_entities || 0).toLocaleString()}</div>
          <div className="stat-subtext">Zero Duplicate Entities</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <TrendingUp color="var(--accent-cyan)" size={22} />
            <span className="stat-label">Overall Match Rate</span>
          </div>
          <div className="stat-number" style={{ color: 'var(--accent-cyan)' }}>
            {stats?.match_rate_percentage || 0}%
          </div>
          <div className="stat-subtext">{stats?.matched_records || 0} Cross-Source Matches</div>
        </div>
      </div>

      {/* Progress & Resolution Breakdown */}
      <div className="panel-box" style={{ marginBottom: '2rem' }}>
        <h3 className="panel-title">
          <GitMerge size={18} color="var(--accent-purple)" />
          Entity Match & Resolution Pipeline Efficiency
        </h3>

        <div style={{ margin: '1.25rem 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
            <span>Cross-Dataset Match Rate ({stats?.matched_records || 0} Matched vs {stats?.new_entities || 0} New Master Entities)</span>
            <strong>{stats?.match_rate_percentage || 0}% Efficiency</strong>
          </div>
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${Math.min(stats?.match_rate_percentage || 0, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Datasets Contribution Breakdown Table */}
      <div className="panel-box">
        <h3 className="panel-title">
          <Database size={18} color="var(--accent-cyan)" />
          Ingested Data Sources & Contributions
        </h3>

        {(!stats?.sources_breakdown || stats.sources_breakdown.length === 0) ? (
          <div className="empty-state">
            <Database size={40} color="var(--text-secondary)" />
            <h3>No Datasets Uploaded Yet</h3>
            <p>Upload demo datasets to see source breakdown and Progressive Entity Resolution stats.</p>
            <button className="btn btn-primary" onClick={onNavigateToUpload} style={{ marginTop: '1rem' }}>
              Upload Demo CSV Datasets
            </button>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Dataset Name</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Raw Records</th>
                  <th>Matched Records</th>
                  <th>New Entities</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.sources_breakdown.map((src, idx) => (
                  <tr key={idx}>
                    <td>
                      <strong style={{ color: 'var(--text-primary)' }}>{src.source_name}</strong>
                    </td>
                    <td>
                      <span className="badge badge-info">{src.source_type}</span>
                    </td>
                    <td>
                      <span className={`badge ${src.status === 'processed' ? 'badge-success' : 'badge-warning'}`}>
                        {src.status}
                      </span>
                    </td>
                    <td><code>{src.total_records}</code></td>
                    <td style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>{src.matched_records}</td>
                    <td style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{src.new_entities}</td>
                    <td>
                      <button className="btn-icon-text" onClick={onNavigateToProcessing}>
                        <PlayCircle size={14} /> Process
                      </button>
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
}
