import { useState } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Overview from './pages/Overview.jsx'
import CallExplorer from './pages/CallExplorer.jsx'
import NoiseBreakdown from './pages/NoiseBreakdown.jsx'
import RunPipeline from './pages/RunPipeline.jsx'
import UploadCall from './pages/UploadCall.jsx'

const NAV = [
  { to: '/',           label: 'Overview',        icon: '◎' },
  { to: '/explore',    label: 'Call Explorer',   icon: '⊞' },
  { to: '/breakdown',  label: 'Noise Breakdown', icon: '∿' },
  { to: '/run',        label: 'Run Pipeline',    icon: '▷' },
  { to: '/upload',     label: 'Upload Call',     icon: '↑' },
]

function Sidebar({ open, setOpen }) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      {/* Brand Header */}
      <div style={{ padding: '28px 24px 20px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10,
            background: 'linear-gradient(135deg, #00F5A0, #00D2FF)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18, fontWeight: 900, color: '#07080A',
            boxShadow: '0 0 20px rgba(0, 245, 160, 0.3)',
            flexShrink: 0,
          }}>N</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 16, color: '#FFFFFF', letterSpacing: '-0.03em' }}>
              NoiseProof
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className="live-dot" />
              <span>Winter '26 Edition</span>
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '20px 14px', flex: 1 }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 12, padding: '0 12px', fontFamily: 'var(--font-mono)' }}>
          EDITIONS EXPLORER
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
              padding: '11px 14px',
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: '-0.01em',
              color: isActive ? '#07080A' : 'var(--text-muted)',
              background: isActive ? 'var(--accent)' : 'transparent',
              boxShadow: isActive ? '0 0 20px rgba(0, 245, 160, 0.25)' : 'none',
              marginBottom: 4,
              transition: 'all 200ms cubic-bezier(0.16, 1, 0.3, 1)',
              textDecoration: 'none',
            })}
          >
            <span style={{ fontSize: 16, width: 20, textAlign: 'center' }}>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Gnani Models Status */}
      <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'var(--font-mono)' }}>
          Active Engine · Gnani AI
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {[
            { name: 'Prisma v2.5', role: 'STT Audio Engine' },
            { name: 'Timbre v2.5', role: 'Multi-Voice TTS' },
            { name: 'Evon v3.3', role: 'Reasoning & Eval' }
          ].map(m => (
            <div key={m.name} className="gnani-badge" style={{ width: '100%', justifyContent: 'space-between' }}>
              <span><strong>{m.name}</strong></span>
              <span style={{ fontSize: 10, opacity: 0.7 }}>{m.role}</span>
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
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
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
              SHOPIFY EDITIONS WINTER '26 THEME
            </span>
            <span style={{ color: 'var(--text-dim)' }}>|</span>
            <span style={{ color: 'var(--text-muted)' }}>Target Award: Noise Canceller (0 dB Robustness)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ color: 'var(--accent)' }}>GNANI VACHANA SUITE</span>
          </div>
        </div>

        {/* Mobile topbar */}
        <div className="topbar-mobile">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: 'none', border: 'none', color: '#FFFFFF', fontSize: 22, cursor: 'pointer' }}
          >☰</button>
          <span style={{ fontWeight: 800, color: 'var(--accent)', fontSize: 16 }}>NoiseProof</span>
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
