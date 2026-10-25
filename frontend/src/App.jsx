import { useState } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Overview from './pages/Overview.jsx'
import CallExplorer from './pages/CallExplorer.jsx'
import NoiseBreakdown from './pages/NoiseBreakdown.jsx'
import RunPipeline from './pages/RunPipeline.jsx'
import UploadCall from './pages/UploadCall.jsx'

const NAV = [
  { to: '/',           label: 'Overview',        icon: '01' },
  { to: '/explore',    label: 'Call Explorer',   icon: '02' },
  { to: '/breakdown',  label: 'Noise Breakdown', icon: '03' },
  { to: '/run',        label: 'Run Pipeline',    icon: '04' },
  { to: '/upload',     label: 'Upload Call',     icon: '05' },
]

function Sidebar({ open, setOpen }) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      {/* Brand Header */}
      <div style={{ padding: '24px 22px 20px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="brand-crest">N</div>
          <div>
            <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, fontSize: 18, color: 'var(--ink)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              NoiseProof
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3, display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--font-mono)' }}>
              <span className="live-dot" />
              <span>Winter ’26 · RenAIssance</span>
            </div>
          </div>
        </div>
      </div>

      {/* Nav Section */}
      <nav style={{ padding: '20px 14px', flex: 1 }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 12, padding: '0 12px', fontFamily: 'var(--font-mono)' }}>
          EDITIONS CATALOGUE
        </div>
        {NAV.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            onClick={() => setOpen(false)}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 14px',
              borderRadius: 6,
              fontSize: 13,
              fontWeight: isActive ? 600 : 500,
              letterSpacing: '-0.01em',
              color: isActive ? '#F7F7EE' : 'var(--text-muted)',
              background: isActive ? 'var(--ink)' : 'transparent',
              marginBottom: 4,
              transition: 'all 180ms ease',
              textDecoration: 'none',
              border: isActive ? '1px solid var(--ink)' : '1px solid transparent',
              boxShadow: isActive ? '0 2px 6px rgba(41, 41, 25, 0.12)' : 'none',
            })}
          >
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              width: 18,
              textAlign: 'center',
              opacity: 0.65
            }}>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Gnani Vachana Suite Engine Badge */}
      <div style={{ padding: '18px 20px', borderTop: '1px solid var(--border)', background: 'rgba(255,255,255,0.45)' }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'var(--font-mono)' }}>
          Active Engine · Gnani AI
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {[
            { name: 'Prisma v2.5', role: 'STT Audio Engine' },
            { name: 'Timbre v2.5', role: 'Multi-Voice TTS' },
            { name: 'Evon v3.3', role: 'Reasoning & Eval' }
          ].map(m => (
            <div key={m.name} className="gnani-badge" style={{ width: '100%', justifyContent: 'space-between', padding: '5px 10px' }}>
              <span><strong>{m.name}</strong></span>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{m.role}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(41, 41, 25, 0.4)',
            zIndex: 99, backdropFilter: 'blur(4px)'
          }}
        />
      )}

      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />

      <div className="main-content">
        {/* Edition Top Header Banner */}
        <div className="edition-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <span className="edition-tag">
              <span className="live-dot" />
              THE RENAISSANCE EDITION · WINTER ’26
            </span>
            <span style={{ color: 'var(--border)' }}>|</span>
            <span style={{ color: 'var(--text-muted)' }}>Award Target: Noise Canceller (0 dB Tolerance)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span className="badge badge-beige">GNANI VACHANA SUITE</span>
          </div>
        </div>

        {/* Mobile topbar */}
        <div className="topbar-mobile">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: 'none', border: 'none', color: 'var(--ink)', fontSize: 22, cursor: 'pointer' }}
          >☰</button>
          <span style={{ fontFamily: 'var(--font-serif)', fontWeight: 700, color: 'var(--ink)', fontSize: 18 }}>NoiseProof</span>
        </div>

        <Routes>
          <Route path="/"          element={<Overview />} />
          <Route path="/explore"   element={<CallExplorer />} />
          <Route path="/breakdown" element={<NoiseBreakdown />} />
          <Route path="/run"       element={<RunPipeline />} />
          <Route path="/upload"    element={<UploadCall />} />
        </Routes>
      </div>
    </div>
  )
}
