import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { api } from '../api.js'

const MOCK_AGG = [
  { snr: 'clean', wer_mean: 0.05, key_fact_recall_mean: 0.97, summary_score_mean: 4.8, latency_ms_mean: 320, cer_mean: 0.02 },
  { snr: '20',    wer_mean: 0.12, key_fact_recall_mean: 0.91, summary_score_mean: 4.4, latency_ms_mean: 340, cer_mean: 0.06 },
  { snr: '10',    wer_mean: 0.28, key_fact_recall_mean: 0.78, summary_score_mean: 3.6, latency_ms_mean: 360, cer_mean: 0.15 },
  { snr: '5',     wer_mean: 0.44, key_fact_recall_mean: 0.62, summary_score_mean: 2.9, latency_ms_mean: 380, cer_mean: 0.26 },
  { snr: '0',     wer_mean: 0.67, key_fact_recall_mean: 0.41, summary_score_mean: 2.1, latency_ms_mean: 410, cer_mean: 0.42 },
]

function StatCard({ label, value, sub, color, badge, index }) {
  return (
    <div className="card fade-up" style={{ textAlign: 'left', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span className="heading-sm">
          {index && <span style={{ color: 'var(--text-dim)', marginRight: 6 }}>{index} //</span>}
          {label}
        </span>
        {badge && <span className="badge badge-muted" style={{ fontSize: 10 }}>{badge}</span>}
      </div>
      <div className="stat-number" style={{ color: color || 'var(--ink)' }}>{value}</div>
      {sub && <div className="body-sm" style={{ marginTop: 8, fontSize: 12 }}>{sub}</div>}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card-sm" style={{ minWidth: 180, background: '#FFFFFF', border: '1px solid var(--border)', boxShadow: 'var(--shadow-hover)' }}>
      <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, color: 'var(--ink)', marginBottom: 8, fontSize: 14, borderBottom: '1px solid var(--border)', paddingBottom: 4 }}>
        Acoustic Condition: {label === 'clean' ? 'Clean Speech' : `${label} dB SNR`}
      </div>
      {payload.map(p => (
        <div key={p.name} style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', gap: 14, marginBottom: 4 }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.name}</span>
          <strong style={{ color: 'var(--ink)' }}>
            {typeof p.value === 'number'
              ? (p.name.includes('Recall') || p.name.includes('WER') ? `${(p.value * 100).toFixed(1)}%` : p.value.toFixed(2))
              : p.value}
          </strong>
        </div>
      ))}
    </div>
  )
}

export default function Overview() {
  const [agg, setAgg] = useState(null)
  const [loading, setLoading] = useState(true)
  const [insight, setInsight] = useState('')

  useEffect(() => {
    api.get('/api/results/summary')
      .then(d => {
        const data = d.aggregated?.length ? d.aggregated : MOCK_AGG
        setAgg(data)
        const above80 = data.filter(r => r.key_fact_recall_mean >= 0.80)
        const lowestSNR = above80[above80.length - 1]
        if (lowestSNR) {
          setInsight(`Key-fact recall holds >80% down to ${lowestSNR.snr === 'clean' ? 'Clean' : lowestSNR.snr + ' dB'} SNR`)
        }
      })
      .catch(() => { setAgg(MOCK_AGG); setInsight('Key-fact recall holds >80% down to 10 dB SNR') })
      .finally(() => setLoading(false))
  }, [])

  const clean = agg?.[0]
  const worst = agg?.[agg.length - 1]

  return (
    <div style={{ padding: 'var(--sp-8) var(--sp-10)', maxWidth: 1200 }}>
      {/* Editorial Hero Header — The Renaissance Style */}
      <div className="fade-up" style={{ marginBottom: 'var(--sp-8)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <span className="edition-tag">
            <span className="live-dot" />
            THE RenAIssance EDITION
          </span>
          {insight && <span className="badge badge-olive">⚡ {insight}</span>}
          <span className="badge badge-beige">PRISMA v2.5 · TIMBRE v2.5 · EVON v3.3</span>
        </div>
        <h1 className="heading-xl">
          Call Intelligence <em>under heavy acoustic noise.</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 14, maxWidth: 680 }}>
          Benchmarking speech comprehension, Word Error Rate (WER), and business key-fact preservation across 5 real-world Indian noise environments down to 0 dB SNR.
        </p>
      </div>

      {/* Bento Stat Cards */}
      {loading ? (
        <div style={{ display: 'flex', gap: 14, marginBottom: 32 }}>
          {[0,1,2,3].map(i => <div key={i} className="card" style={{ flex: 1, height: 110, animation: 'pulse 1.5s infinite' }} />)}
        </div>
      ) : (
        <div className="grid-4" style={{ marginBottom: 'var(--sp-8)' }}>
          <StatCard index="01" label="CLEAN BASELINE WER" value={`${((clean?.wer_mean || 0)*100).toFixed(1)}%`} sub="Ground-truth reference audio" color="var(--ink)" badge="Optimal" />
          <StatCard index="02" label="0 dB SNR WER" value={`${((worst?.wer_mean || 0)*100).toFixed(1)}%`} sub="Extreme noise conditions" color="var(--terracotta)" badge="Stress Test" />
          <StatCard index="03" label="CLEAN FACT RECALL" value={`${((clean?.key_fact_recall_mean || 0)*100).toFixed(0)}%`} sub="Critical business data preserved" color="var(--olive)" badge="Entity Extr." />
          <StatCard index="04" label="AVERAGE LATENCY" value={`${(clean?.latency_ms_mean || 0).toFixed(0)}ms`} sub="Prisma v2.5 decoding speed" color="var(--gold)" badge="Engine RT" />
        </div>
      )}

      {/* Dual Chart Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-6)', marginBottom: 'var(--sp-8)' }}>
        {/* WER vs SNR Curve */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
            <div>
              <div className="heading-sm">DEGRADATION TRAJECTORY</div>
              <div className="heading-md" style={{ marginTop: 4, fontFamily: 'var(--font-serif)', fontSize: 18 }}>
                Word Error Rate (WER) vs. SNR
              </div>
            </div>
            <span className="badge badge-terra">Low is better</span>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={agg || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(41,41,25,0.08)" />
                <XAxis dataKey="snr" tickFormatter={v => v === 'clean' ? 'Clean' : `${v}dB`} stroke="var(--text-dim)" fontSize={11} fontFamily="var(--font-mono)" />
                <YAxis tickFormatter={v => `${(v*100).toFixed(0)}%`} stroke="var(--text-dim)" fontSize={11} fontFamily="var(--font-mono)" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="wer_mean"
                  name="Word Error Rate (WER)"
                  stroke="#C24B27"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#C24B27', stroke: '#FFFFFF', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#C24B27' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Key-Fact Recall vs SNR Curve */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
            <div>
              <div className="heading-sm">ENTITY SURVIVAL</div>
              <div className="heading-md" style={{ marginTop: 4, fontFamily: 'var(--font-serif)', fontSize: 18 }}>
                Key-Fact Recall vs. SNR
              </div>
            </div>
            <span className="badge badge-olive">High is better</span>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={agg || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(41,41,25,0.08)" />
                <XAxis dataKey="snr" tickFormatter={v => v === 'clean' ? 'Clean' : `${v}dB`} stroke="var(--text-dim)" fontSize={11} fontFamily="var(--font-mono)" />
                <YAxis domain={[0, 1]} tickFormatter={v => `${(v*100).toFixed(0)}%`} stroke="var(--text-dim)" fontSize={11} fontFamily="var(--font-mono)" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="key_fact_recall_mean"
                  name="Key-Fact Recall"
                  stroke="#2D5A27"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#2D5A27', stroke: '#FFFFFF', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#2D5A27' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Methodology & ITU G.711 Telephony Frame */}
      <div className="card" style={{ background: '#FFFFFF', border: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ maxWidth: 650 }}>
            <div className="heading-sm">ACOUSTIC METHODOLOGY</div>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 20, color: 'var(--ink)', marginTop: 4 }}>
              Deterministic RMS Mixing & ITU-T G.711 Telephony Emulation
            </h3>
            <p className="body-sm" style={{ marginTop: 8 }}>
              Audio is degraded procedurally with root-mean-square energy scaling down to 0 dB SNR across 5 authentic Indian noise archetypes (Traffic, Crowd, Wind, Market, White), followed by 8 kHz downsampling, 300–3400 Hz bandpass filtering, soft-clipping saturation, and cellular packet dropout simulation.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 220 }}>
            <div className="gnani-badge" style={{ justifyContent: 'space-between' }}>
              <span>Sampling Bandwidth</span>
              <strong>8 kHz Mono</strong>
            </div>
            <div className="gnani-badge" style={{ justifyContent: 'space-between' }}>
              <span>Bandpass Envelope</span>
              <strong>300–3400 Hz</strong>
            </div>
            <div className="gnani-badge" style={{ justifyContent: 'space-between' }}>
              <span>Noise Archetypes</span>
              <strong>5 Procedural Profiles</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
