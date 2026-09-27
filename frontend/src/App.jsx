import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Database, Server, Cpu, RefreshCw, CheckCircle2, AlertCircle, LayoutDashboard, GitMerge, PlayCircle } from 'lucide-react';
import SourcesManager from './components/SourcesManager';
import FieldMappingManager from './components/FieldMappingManager';
import ImportProcessingManager from './components/ImportProcessingManager';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('processing'); // Default to processing for Phase 8-10 demo
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setHealth(response.data);
    } catch (err) {
      console.error("Failed to connect to backend API:", err);
      setError(err.message || "Unable to connect to backend server");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const isConnected = health && health.api === 'connected';

  return (
    <div>
      {/* Header with Navigation */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">ER</div>
            <div>
              <div className="brand-title">Multi-Database Entity Resolution</div>
              <div className="brand-subtitle">Unified Master Data Repository System</div>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <LayoutDashboard size={16} />
              Dashboard
            </button>
            <button
              className={`nav-tab ${activeTab === 'sources' ? 'active' : ''}`}
              onClick={() => setActiveTab('sources')}
            >
              <Database size={16} />
              Data Sources
            </button>
            <button
              className={`nav-tab ${activeTab === 'mappings' ? 'active' : ''}`}
              onClick={() => setActiveTab('mappings')}
            >
              <GitMerge size={16} />
              Field Mapping
            </button>
            <button
              className={`nav-tab ${activeTab === 'processing' ? 'active' : ''}`}
              onClick={() => setActiveTab('processing')}
            >
              <PlayCircle size={16} />
              Ingestion & Processing
            </button>
          </nav>



          <div className="status-pill">
            <span className={`pulse-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span>API Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="container">
        {activeTab === 'sources' && <SourcesManager />}
        {activeTab === 'mappings' && <FieldMappingManager />}
        {activeTab === 'processing' && <ImportProcessingManager />}

        {activeTab === 'dashboard' && (


          <div>
            <section className="hero-card">
              <h1 className="hero-title">
                Phase 4 — <span className="gradient-text">Source Management</span>
              </h1>
              <p className="hero-description">
                Upload CSV datasets, view metadata, inspect detected schema columns, and prepare datasets for matching and enrichment.
              </p>
              <div style={{ marginTop: '1rem' }}>
                <span className="tech-badge">FastAPI Ingestion Engine</span>
                <span className="tech-badge">Pandas Chunk Inspection</span>
                <span className="tech-badge">PostgreSQL Metadata</span>
              </div>
            </section>

            {/* Health Check Grid */}
            <div style={{ marginTop: '2.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2>System Services Health</h2>
              <button className="btn btn-primary" onClick={fetchHealth} disabled={loading}>
                <RefreshCw className={loading ? 'spin' : ''} size={16} />
                {loading ? 'Checking...' : 'Refresh Status'}
              </button>
            </div>

            <div className="grid-cards" style={{ marginTop: '1rem' }}>
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <Server color="var(--accent-blue)" size={24} />
                  {isConnected ? <CheckCircle2 color="var(--accent-emerald)" size={20} /> : <AlertCircle color="var(--accent-rose)" size={20} />}
                </div>
                <div className="card-title">Backend API (FastAPI)</div>
                <div className="card-value">{health?.api === 'connected' ? 'Connected' : 'Offline'}</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                  URL: {API_BASE_URL}
                </p>
              </div>

              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <Database color="var(--accent-purple)" size={24} />
                  {health?.database === 'connected' ? <CheckCircle2 color="var(--accent-emerald)" size={20} /> : <AlertCircle color="var(--accent-amber)" size={20} />}
                </div>
                <div className="card-title">PostgreSQL Database</div>
                <div className="card-value" style={{ fontSize: '1.25rem' }}>
                  {health?.database === 'connected' ? 'Connected' : (health?.database || 'Checking...')}
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                  Entity Storage & Source Traceability
                </p>
              </div>

              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <Cpu color="var(--accent-cyan)" size={24} />
                  {health?.redis === 'connected' ? <CheckCircle2 color="var(--accent-emerald)" size={20} /> : <AlertCircle color="var(--accent-amber)" size={20} />}
                </div>
                <div className="card-title">Redis Cache & Queue</div>
                <div className="card-value" style={{ fontSize: '1.25rem' }}>
                  {health?.redis === 'connected' ? 'Connected' : (health?.redis || 'Checking...')}
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                  Background Processing & Search Cache
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

