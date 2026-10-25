import { useState, useEffect, useRef } from 'react'
import { api } from '../api.js'

const NOISE_TYPES_OPT = ['street', 'crowd', 'wind', 'white', 'market']
const SNR_OPTS = ['clean', '20', '10', '5', '0']

export default function RunPipeline() {
  const [config, setConfig] = useState({
    num_calls: 2,
    noise_types: ['street', 'crowd', 'wind', 'white', 'market'],
    snr_levels: ['clean', '20', '10', '5', '0'],
    dry_run: false,
  })
  const [runId, setRunId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [usage, setUsage] = useState(null)
  const pollRef = useRef(null)

  // Credit estimate calculation
  const estimatedCalls = config.num_calls * config.noise_types.length * config.snr_levels.length
  const ttsCredits = config.num_calls * 1
  const sttCredits = estimatedCalls
  const evonCredits = config.num_calls * 2
  const totalEst = config.dry_run ? 0 : (ttsCredits + sttCredits + evonCredits)

  useEffect(() => {
    api.get('/api/usage').then(setUsage).catch(() => {})
  }, [])

  const toggleNoise = (n) => setConfig(c => ({
    ...c,
    noise_types: c.noise_types.includes(n) ? c.noise_types.filter(x => x !== n) : [...c.noise_types, n]
  }))

  const toggleSNR = (s) => setConfig(c => ({
    ...c,
    snr_levels: c.snr_levels.includes(s) ? c.snr_levels.filter(x => x !== s) : [...c.snr_levels, s]
  }))

  const startRun = async () => {
    if (config.noise_types.length === 0 || config.snr_levels.length === 0) {
      alert('Please select at least one noise type and one SNR level.')
      return
    }
    try {
      const res = await api.post('/api/runs', config)
      setRunId(res.run_id)
      setProgress({ status: 'running', completed_steps: 0, total_steps: estimatedCalls, current_step: 'Queued…' })
      
      pollRef.current = setInterval(async () => {
        try {
          const p = await api.get(`/api/runs/${res.run_id}`)
          setProgress(p)
          if (p.status === 'done' || p.status === 'failed') {
            clearInterval(pollRef.current)
            api.get('/api/usage').then(setUsage).catch(() => {})
          }
        } catch {}
      }, 1500)
    } catch (e) {
      alert('Failed to start run: ' + e.message)
    }
  }

  useEffect(() => () => clearInterval(pollRef.current), [])

  const pct = progress?.total_steps
    ? Math.min(100, Math.round((progress.completed_steps / progress.total_steps) * 100))
    : 0

  return (
    <div style={{ padding: 'var(--sp-8) var(--sp-10)', maxWidth: 1000 }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span className="edition-tag">
            <span className="live-dot" />
            BENCHMARK ORCHESTRATOR
          </span>
          <span className="badge badge-beige">LIVE PIPELINE RUNNER</span>
        </div>
        <h1 className="heading-xl">
          Run <em>Pipeline</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 10 }}>
          Execute multi-condition synthetic Hinglish benchmark runs. Real-time credit metering and progress streaming.
        </p>
      </div>

      {/* Main Bento Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 'var(--sp-6)', marginBottom: 'var(--sp-6)' }}>
        {/* Left: Configuration Panel */}
        <div className="card fade-up">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-5)' }}>
            <h2 className="heading-md" style={{ fontFamily: 'var(--font-serif)', fontSize: 18 }}>Configuration Matrix</h2>
            <span className="badge badge-muted">CONFIG v1.0</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-4)', marginBottom: 20 }}>
            <div>
              <label className="heading-sm" style={{ display: 'block', marginBottom: 8 }}>Synthetic Calls</label>
              <input
                type="number" min={1} max={6} value={config.num_calls}
                onChange={e => setConfig(c => ({ ...c, num_calls: parseInt(e.target.value) || 1 }))}
                className="input" style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
              />
              <span className="body-sm" style={{ fontSize: 11, marginTop: 4, display: 'block' }}>1 to 6 base scenarios</span>
            </div>

            <div>
              <label className="heading-sm" style={{ display: 'block', marginBottom: 8 }}>Dry-Run Emulation</label>
              <div style={{ display: 'flex', alignItems: 'center', height: 42 }}>
                <label className="toggle-wrap">
                  <label className="toggle">
                    <input
                      type="checkbox" checked={config.dry_run}
                      onChange={e => setConfig(c => ({ ...c, dry_run: e.target.checked }))}
                    />
                    <span className="toggle-slider" />
                  </label>
                  <span className="body-sm" style={{ fontWeight: 600, color: config.dry_run ? 'var(--gold)' : 'var(--text-muted)' }}>
                    {config.dry_run ? 'Dry Run (0 Credits)' : 'Live Gnani API'}
                  </span>
                </label>
              </div>
            </div>
          </div>

          <div className="divider" />

          {/* Noise Types Selection */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <label className="heading-sm">Noise Environments</label>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{config.noise_types.length} selected</span>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {NOISE_TYPES_OPT.map(n => {
                const active = config.noise_types.includes(n)
                return (
                  <button
                    key={n} onClick={() => toggleNoise(n)}
                    className={`btn ${active ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 14px', fontSize: 12, textTransform: 'capitalize' }}
                  >
                    {active ? '✓ ' : ''}{n}
                  </button>
                )
              })}
            </div>
          </div>

          {/* SNR Levels Selection */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <label className="heading-sm">Signal-to-Noise Levels (SNR)</label>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{config.snr_levels.length} selected</span>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {SNR_OPTS.map(s => {
                const active = config.snr_levels.includes(s)
                return (
                  <button
                    key={s} onClick={() => toggleSNR(s)}
                    className={`btn ${active ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 14px', fontSize: 12, fontFamily: 'var(--font-mono)' }}
                  >
                    {active ? '✓ ' : ''}{s === 'clean' ? 'Clean' : `${s} dB`}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Right: Telemetry & Start Action */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          {/* Estimated Impact Card */}
          <div className="card fade-up">
            <span className="heading-sm" style={{ marginBottom: 12, display: 'block' }}>RESOURCE ESTIMATE</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <div className="body-sm">Total Audio Pipeline Variants</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: 34, fontWeight: 600, color: 'var(--ink)', letterSpacing: '-0.02em' }}>
                  {estimatedCalls} <span style={{ fontSize: 14, color: 'var(--text-muted)', fontWeight: 400 }}>variants</span>
                </div>
              </div>
              <div>
                <div className="body-sm">Estimated Gnani Credits</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: 34, fontWeight: 600, color: config.dry_run ? 'var(--gold)' : 'var(--ink)', letterSpacing: '-0.02em' }}>
                  {config.dry_run ? '0 (Dry Run)' : `~${totalEst}`} <span style={{ fontSize: 14, color: 'var(--text-muted)', fontWeight: 400 }}>credits</span>
                </div>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', background: 'var(--surface-warm)', padding: 12, borderRadius: 6, border: '1px solid var(--border)' }}>
                ℹ All requests pass through SHA-256 disk cache. Identical calls are billed exactly 0 credits.
              </div>
            </div>

            <button
              onClick={startRun}
              disabled={progress?.status === 'running' || config.noise_types.length === 0}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: 20, padding: '14px', fontSize: 14 }}
            >
              {progress?.status === 'running' ? (
                <><span className="spinner" style={{ width: 14, height: 14, borderTopColor: '#F7F7EE' }} /> Pipeline Executing…</>
              ) : (
                '▷ Launch Benchmark Suite'
              )}
            </button>
          </div>

          {/* Real-time Usage Meter */}
          {usage && (
            <div className="card-sm">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="heading-sm">SESSION CREDITS CONSUMED</span>
                <span style={{ fontWeight: 800, color: 'var(--gold)', fontFamily: 'var(--font-mono)' }}>
                  {usage.total_credits || 0}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Live Pipeline Execution Progress */}
      {progress && (
        <div className="card fade-up" style={{ borderLeft: progress.status === 'failed' ? '3px solid var(--terracotta)' : '3px solid var(--ink)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className={`badge ${progress.status === 'done' ? 'badge-olive' : progress.status === 'failed' ? 'badge-terra' : 'badge-beige'}`}>
                {progress.status.toUpperCase()}
              </span>
              <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--ink)' }}>{progress.current_step}</span>
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--ink)', fontWeight: 700 }}>
              {pct}% ({progress.completed_steps}/{progress.total_steps || estimatedCalls})
            </span>
          </div>

          <div className="progress-track">
            <div
              className={`progress-fill ${progress.status === 'failed' ? 'error' : ''}`}
              style={{ width: `${pct}%` }}
            />
          </div>

          {progress.status === 'done' && (
            <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, color: 'var(--olive)', fontWeight: 600 }}>
                ✓ Benchmark run finished successfully! Results are now visible on Overview and Call Explorer.
              </span>
              <a href="/" className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: 12 }}>
                View Dashboard →
              </a>
            </div>
          )}
          {progress.status === 'failed' && (
            <div style={{ marginTop: 12, fontSize: 13, color: 'var(--terracotta)' }}>
              Error: {progress.error}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
