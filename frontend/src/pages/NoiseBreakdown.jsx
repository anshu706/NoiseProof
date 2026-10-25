import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { api } from '../api.js'

const MOCK_BY_NOISE = [
  { noise_type: 'street', wer_mean: 0.32, key_fact_recall_mean: 0.72, summary_score_mean: 3.4 },
  { noise_type: 'crowd',  wer_mean: 0.38, key_fact_recall_mean: 0.68, summary_score_mean: 3.1 },
  { noise_type: 'wind',   wer_mean: 0.22, key_fact_recall_mean: 0.81, summary_score_mean: 3.8 },
  { noise_type: 'white',  wer_mean: 0.41, key_fact_recall_mean: 0.64, summary_score_mean: 2.9 },
  { noise_type: 'market', wer_mean: 0.45, key_fact_recall_mean: 0.59, summary_score_mean: 2.7 },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card-sm" style={{ minWidth: 170, background: 'rgba(12, 15, 20, 0.95)', border: '1px solid rgba(255,255,255,0.15)', boxShadow: '0 8px 30px rgba(0,0,0,0.6)' }}>
      <div style={{ fontWeight: 700, color: '#FFFFFF', marginBottom: 6, textTransform: 'capitalize', fontSize: 13, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 4 }}>
        {label} noise
      </div>
      {payload.map(p => (
        <div key={p.name} style={{ fontSize: 12, color: '#D5DAE5', display: 'flex', justifyContent: 'space-between', gap: 14, marginBottom: 4 }}>
          <span style={{ color: p.fill, fontWeight: 500 }}>{p.name}</span>
          <strong style={{ color: '#FFFFFF' }}>{typeof p.value === 'number' ? (p.value * 100).toFixed(1) + '%' : p.value}</strong>
        </div>
      ))}
    </div>
  )
}

export default function NoiseBreakdown() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/api/results/summary')
      .then(d => {
        if (!d.eval?.length) { setData(MOCK_BY_NOISE); return }
        const groups = {}
        d.eval.forEach(r => {
          if (!groups[r.noise_type]) groups[r.noise_type] = { noise_type: r.noise_type, wers: [], recalls: [], scores: [] }
          groups[r.noise_type].wers.push(r.wer)
          groups[r.noise_type].recalls.push(r.key_fact_recall)
          groups[r.noise_type].scores.push(r.summary_score)
        })
        const agg = Object.values(groups).map(g => ({
          noise_type: g.noise_type,
          wer_mean: g.wers.reduce((a,b) => a+b,0) / g.wers.length,
          key_fact_recall_mean: g.recalls.reduce((a,b) => a+b,0) / g.recalls.length,
          summary_score_mean: g.scores.reduce((a,b) => a+b,0) / g.scores.length,
        }))
        setData(agg)
      })
      .catch(() => setData(MOCK_BY_NOISE))
  }, [])

  const worst = data ? [...data].sort((a,b) => b.wer_mean - a.wer_mean)[0] : null
  const best  = data ? [...data].sort((a,b) => a.wer_mean - b.wer_mean)[0] : null

  return (
    <div style={{ padding: 'var(--sp-8) var(--sp-10)', maxWidth: 1100 }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <span className="edition-tag">
            <span className="live-dot" />
            ACOUSTIC PROFILE ANALYSIS
          </span>
          <span className="badge badge-beige">5 NOISE ARCHETYPES</span>
        </div>
        <h1 className="heading-xl">
          Noise <em>Breakdown</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 8 }}>
          Pinpointing model degradation across street traffic, crowd chatter, wind turbulence, white noise, and bustling Indian bazaars.
        </p>
      </div>

      {worst && (
        <div style={{ display: 'flex', gap: 'var(--sp-4)', marginBottom: 'var(--sp-6)', flexWrap: 'wrap' }}>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--terracotta-lt)' }}>
            <span className="heading-sm">HARDEST NOISE TYPE</span>
            <div style={{ fontSize: 26, fontWeight: 800, color: 'var(--terracotta-lt)', marginTop: 6, textTransform: 'capitalize' }}>
              {worst.noise_type}
            </div>
            <div className="body-sm" style={{ marginTop: 4 }}>Average WER: {(worst.wer_mean*100).toFixed(1)}%</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--accent)' }}>
            <span className="heading-sm">MOST RESILIENT TYPE</span>
            <div style={{ fontSize: 26, fontWeight: 800, color: 'var(--accent)', marginTop: 6, textTransform: 'capitalize' }}>
              {best.noise_type}
            </div>
            <div className="body-sm" style={{ marginTop: 4 }}>Lowest WER: {(best.wer_mean*100).toFixed(1)}%</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--accent-cyan)' }}>
            <span className="heading-sm">BEST KEY-FACT RETENTION</span>
            {(() => {
              const b = data ? [...data].sort((a,b) => b.key_fact_recall_mean - a.key_fact_recall_mean)[0] : null
              return b ? (
                <>
                  <div style={{ fontSize: 26, fontWeight: 800, color: 'var(--accent-cyan)', marginTop: 6, textTransform: 'capitalize' }}>
                    {b.noise_type}
                  </div>
                  <div className="body-sm" style={{ marginTop: 4 }}>Recall: {(b.key_fact_recall_mean*100).toFixed(1)}%</div>
                </>
              ) : null
            })()}
          </div>
        </div>
      )}

      {data && (
        <>
          {/* WER Bar Chart */}
          <div className="card fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-5)' }}>
              <div>
                <h2 className="heading-md">Word Error Rate by Noise Classification</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Lower bar indicates higher speech transcription accuracy</div>
              </div>
              <span className="badge badge-terra">ERROR RATE</span>
            </div>
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="noise_type" stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, textTransform: 'capitalize' }} />
                <YAxis stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="wer_mean" name="WER" fill="var(--terracotta-lt)" radius={[6,6,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Key-Fact Recall & Summary Score */}
          <div className="card fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-5)' }}>
              <div>
                <h2 className="heading-md">Key-Fact Recall vs. Reasoning Summary Fidelity</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Higher score represents complete extraction of loan numbers, amounts, and dates</div>
              </div>
              <span className="badge badge-olive">RECALL METRICS</span>
            </div>
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="noise_type" stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, textTransform: 'capitalize' }} />
                <YAxis stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }} domain={[0, 1]} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="key_fact_recall_mean" name="Key-Fact Recall" fill="var(--accent)" radius={[6,6,0,0]} />
                <Bar dataKey={(d) => d.summary_score_mean / 5} name="Summary Score" fill="var(--accent-cyan)" radius={[6,6,0,0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="body-sm" style={{ marginTop: 12, textAlign: 'center', color: 'var(--text-muted)' }}>
              Green bars: Entity recall (%) · Cyan bars: Evon summary evaluation score normalised (out of 5.0)
            </p>
          </div>

          {/* Detailed Table */}
          <div className="card fade-up">
            <h2 className="heading-md" style={{ marginBottom: 'var(--sp-4)' }}>Acoustic Stress Matrix</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    {['Noise Environment','WER ↓','Key-Fact Recall ↑','Summary Score ↑','Resilience Assessment'].map(h => (
                      <th key={h} style={{ padding: '12px 14px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[...data].sort((a,b) => a.wer_mean - b.wer_mean).map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '14px', textTransform: 'capitalize', fontWeight: 700, color: '#FFFFFF' }}>
                        {row.noise_type}
                      </td>
                      <td style={{ padding: '14px', color: row.wer_mean > 0.4 ? 'var(--terracotta-lt)' : '#FFFFFF', fontWeight: 600 }}>
                        {(row.wer_mean*100).toFixed(1)}%
                      </td>
                      <td style={{ padding: '14px', color: row.key_fact_recall_mean >= 0.7 ? 'var(--accent)' : 'var(--terracotta-lt)', fontWeight: 600 }}>
                        {(row.key_fact_recall_mean*100).toFixed(1)}%
                      </td>
                      <td style={{ padding: '14px', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                        {row.summary_score_mean.toFixed(1)} / 5.0
                      </td>
                      <td style={{ padding: '14px' }}>
                        <span className={`badge ${row.wer_mean < 0.3 ? 'badge-olive' : row.wer_mean < 0.42 ? 'badge-beige' : 'badge-terra'}`}>
                          {row.wer_mean < 0.3 ? 'High Robustness' : row.wer_mean < 0.42 ? 'Moderate Noise Impact' : 'Severe Masking'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
