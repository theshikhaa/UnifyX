import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Database, Server, Cpu, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
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
      {/* Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">ER</div>
            <div>
              <div className="brand-title">Multi-Database Entity Resolution</div>
              <div className="brand-subtitle">Unified Master Data Repository System</div>
            </div>
          </div>

          <div className="status-pill">
            <span className={`pulse-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span>API Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="container">
        {/* Hero Banner */}
        <section className="hero-card">
          <h1 className="hero-title">
            Phase 1 — <span className="gradient-text">Project Foundation</span>
          </h1>
          <p className="hero-description">
            Multi-Database Ingestion, Schema Mapping, Normalization & Progressive Entity Resolution Platform.
          </p>
          <div style={{ marginTop: '1rem' }}>
            <span className="tech-badge">React + Vite</span>
            <span className="tech-badge">FastAPI</span>
            <span className="tech-badge">PostgreSQL</span>
            <span className="tech-badge">Redis</span>
            <span className="tech-badge">SQLAlchemy</span>
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

        <div className="grid-cards">
          {/* FastAPI Card */}
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

          {/* Database Card */}
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

          {/* Redis Card */}
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

        {/* Diagnostic Response Output */}
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Raw API Health Payload:
          </h3>
          {error ? (
            <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fca5a5' }}>
              <strong>Connection Error:</strong> {error}. Make sure the FastAPI backend is running.
            </div>
          ) : (
            <pre>{JSON.stringify(health, null, 2)}</pre>
          )}
        </div>
      </main>
    </div>
  );
}
