import { Suspense, lazy } from 'react'
import { Navigate, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { StatCard, formatNumber } from './components/ui'
import { useDashboardData } from './hooks/useDashboardData'

const PatientSafetyRoute = lazy(() => import('./routes/PatientSafetyRoute'))
const PrescribingRoute = lazy(() => import('./routes/PrescribingRoute'))
const DoctorRiskRoute = lazy(() => import('./routes/DoctorRiskRoute'))
const ClusterRoute = lazy(() => import('./routes/ClusterRoute'))
const QualityRoute = lazy(() => import('./routes/QualityRoute'))

const NAV_ITEMS = [
  { path: '/patient-safety', label: 'Patient Safety Console' },
  { path: '/prescribing', label: 'Prescribing Simulator' },
  { path: '/doctor-risk', label: 'Doctor Risk Profile' },
  { path: '/cluster', label: 'Cluster Analytics' },
  { path: '/quality', label: 'Quality Monitor' },
]

function LoadingPanel() {
  return <div className="route-loading">Loading section...</div>
}

export default function App() {
  const location = useLocation()
  const dashboard = useDashboardData()
  const activeLabel = NAV_ITEMS.find((item) => item.path === location.pathname)?.label || NAV_ITEMS[0].label

  return (
    <div className="layout-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="eyebrow">VitalEdge+</span>
          <h1>Clinical allergy intelligence workspace</h1>
        </div>
        <div className={`status-pill ${dashboard.health.label === 'Online' ? 'ok' : 'bad'}`}>
          <span>API status: {dashboard.health.label}</span>
          <small>
            {dashboard.health.url} · {dashboard.health.detail}
          </small>
        </div>

        <nav className="nav-stack">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="app-shell">
        <header className="hero">
          <div>
            <span className="eyebrow">React operations console</span>
            <h2>{activeLabel}</h2>
            <p>Five-section clinical intelligence console powered by FastAPI endpoints.</p>
          </div>
        </header>

        {dashboard.error ? <div className="alert">API error: {dashboard.error}</div> : null}

        <section className="stats-grid">
          <StatCard
            label="Model F1"
            value={dashboard.summary.model ? formatNumber(dashboard.summary.model.Model_F1, 3) : '...'}
            hint="reaction-risk classifier"
          />
          <StatCard
            label="AUC-ROC"
            value={dashboard.summary.model ? formatNumber(dashboard.summary.model.Model_AUC_ROC, 3) : '...'}
            hint="overall ranking performance"
          />
          <StatCard
            label="Completeness"
            value={dashboard.summary.quality ? formatNumber(dashboard.summary.quality.Completeness_Score, 1) : '...'}
            hint="source table coverage"
          />
          <StatCard
            label="Patients loaded"
            value={String(dashboard.summary.patients.length || 0)}
            hint="intelligence profiles exposed via API"
          />
        </section>

        <Suspense fallback={<LoadingPanel />}>
          <Routes>
            <Route path="/" element={<Navigate to="/patient-safety" replace />} />
            <Route path="/patient-safety" element={<PatientSafetyRoute dashboard={dashboard} />} />
            <Route path="/prescribing" element={<PrescribingRoute dashboard={dashboard} />} />
            <Route path="/doctor-risk" element={<DoctorRiskRoute dashboard={dashboard} />} />
            <Route path="/cluster" element={<ClusterRoute dashboard={dashboard} />} />
            <Route path="/quality" element={<QualityRoute dashboard={dashboard} />} />
            <Route path="*" element={<Navigate to="/patient-safety" replace />} />
          </Routes>
        </Suspense>

        {dashboard.loading ? <div className="footer-note">Loading dashboard data from the API...</div> : null}
      </main>
    </div>
  )
}