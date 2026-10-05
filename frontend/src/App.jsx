import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, Database, Server, Cpu, RefreshCw, CheckCircle2, 
  AlertCircle, LayoutDashboard, GitMerge, PlayCircle, Search, Users,
  Sparkles, Layers, ShieldCheck, ChevronRight
} from 'lucide-react';
import SourcesManager from './components/SourcesManager';
import FieldMappingManager from './components/FieldMappingManager';
import ImportProcessingManager from './components/ImportProcessingManager';
import UnifiedSearchManager from './components/UnifiedSearchManager';
import StatisticsManager from './components/StatisticsManager';
import EntitiesRepositoryManager from './components/EntitiesRepositoryManager';
import EntityDetailModal from './components/EntityDetailModal';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('search'); // Default to Unified Search
  const [health, setHealth] = useState(null);
  const [selectedEntityId, setSelectedEntityId] = useState(null);

  const fetchHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setHealth(response.data);
    } catch (err) {
      console.error("Health check error:", err);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const isConnected = health && health.api === 'connected';

  const tabTitles = {
    dashboard: "Analytics & System Dashboard",
    sources: "Multi-Database Source Management",
    mappings: "Canonical Field Mapping Engine",
    processing: "Batch Ingestion & Resolution Pipeline",
    search: "Unified Progressive Entity Search Engine",
    entities: "Master Entity Repository & Traceability"
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="app-sidebar">
        {/* Brand Logo Header */}
        <div className="sidebar-brand">
          <div className="brand-icon">ER</div>
          <div>
            <div className="brand-title">Entity Resolution</div>
            <div className="brand-subtitle">Unified Repository</div>
          </div>
        </div>

        {/* Sidebar Nav Items */}
        <div className="sidebar-nav-container">
          <div className="nav-group-title">PLATFORM CORE</div>
          <nav className="sidebar-nav">
            <button
              className={`sidebar-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard & Stats</span>
            </button>
            <button
              className={`sidebar-nav-item ${activeTab === 'sources' ? 'active' : ''}`}
              onClick={() => setActiveTab('sources')}
            >
              <Database size={18} />
              <span>Data Sources</span>
            </button>
            <button
              className={`sidebar-nav-item ${activeTab === 'mappings' ? 'active' : ''}`}
              onClick={() => setActiveTab('mappings')}
            >
              <GitMerge size={18} />
              <span>Field Mapping</span>
            </button>
            <button
              className={`sidebar-nav-item ${activeTab === 'processing' ? 'active' : ''}`}
              onClick={() => setActiveTab('processing')}
            >
              <PlayCircle size={18} />
              <span>Ingestion Pipeline</span>
            </button>
          </nav>

          <div className="nav-group-title" style={{ marginTop: '1.5rem' }}>RESOLUTION ENGINE</div>
          <nav className="sidebar-nav">
            <button
              className={`sidebar-nav-item ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={18} />
              <span>Unified Search</span>
              <span className="nav-badge">Core</span>
            </button>
            <button
              className={`sidebar-nav-item ${activeTab === 'entities' ? 'active' : ''}`}
              onClick={() => setActiveTab('entities')}
            >
              <Users size={18} />
              <span>Master Entities</span>
            </button>
          </nav>
        </div>

        {/* Bottom Health Status Footer */}
        <div className="sidebar-footer">
          <div className="health-card">
            <div className="health-header">
              <span className={`pulse-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
              <span className="health-status-text">
                {isConnected ? 'API Connected' : 'API Offline'}
              </span>
            </div>
            <div className="health-details">
              <div>DB: <strong>{health?.database === 'connected' ? 'PostgreSQL' : 'Connecting'}</strong></div>
              <div>Cache: <strong>{health?.redis === 'connected' ? 'Redis OK' : 'Cache'}</strong></div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="app-main-content">
        {/* Top Header Bar */}
        <header className="main-topbar">
          <div className="topbar-breadcrumb">
            <span style={{ color: 'var(--text-secondary)' }}>Resolution System</span>
            <ChevronRight size={14} color="var(--text-muted)" />
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{tabTitles[activeTab]}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span className="status-pill">
              <Sparkles size={14} color="var(--accent-purple)" />
              <span>Progressive Enrichment Active</span>
            </span>
          </div>
        </header>

        {/* Dynamic Page Views */}
        <main className="content-container">
          {activeTab === 'dashboard' && (
            <StatisticsManager 
              onNavigateToUpload={() => setActiveTab('sources')}
              onNavigateToProcessing={() => setActiveTab('processing')}
            />
          )}
          {activeTab === 'sources' && <SourcesManager />}
          {activeTab === 'mappings' && <FieldMappingManager />}
          {activeTab === 'processing' && <ImportProcessingManager />}
          {activeTab === 'search' && (
            <UnifiedSearchManager 
              onInspectEntity={(id) => setSelectedEntityId(id)}
            />
          )}
          {activeTab === 'entities' && (
            <EntitiesRepositoryManager 
              onInspectEntity={(id) => setSelectedEntityId(id)}
            />
          )}
        </main>
      </div>

      {/* Deep Inspection Entity Detail Modal */}
      {selectedEntityId && (
        <EntityDetailModal 
          entityId={selectedEntityId}
          onClose={() => setSelectedEntityId(null)}
        />
      )}
    </div>
  );
}
