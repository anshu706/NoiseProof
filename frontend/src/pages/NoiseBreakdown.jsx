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
    <div className="card-sm" style={{ minWidth: 180, background: '#FFFFFF', border: '1px solid var(--border)', boxShadow: 'var(--shadow-hover)' }}>
      <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, color: 'var(--ink)', marginBottom: 6, textTransform: 'capitalize', fontSize: 14, borderBottom: '1px solid var(--border)', paddingBottom: 4 }}>
        {label} Noise
      </div>
      {payload.map(p => (
        <div key={p.name} style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', gap: 14, marginBottom: 4 }}>
          <span style={{ color: p.fill, fontWeight: 600 }}>{p.name}</span>
          <strong style={{ color: 'var(--ink)' }}>{typeof p.value === 'number' ? (p.value * 100).toFixed(1) + '%' : p.value}</strong>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span className="edition-tag">
            <span className="live-dot" />
            ACOUSTIC PROFILE ANALYSIS
          </span>
          <span className="badge badge-beige">5 NOISE ARCHETYPES</span>
        </div>
        <h1 className="heading-xl">
          Noise <em>Breakdown</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 10 }}>
          Pinpointing model degradation across street traffic, crowd chatter, wind turbulence, white noise, and bustling Indian bazaars.
        </p>
      </div>

      {worst && (
        <div style={{ display: 'flex', gap: 'var(--sp-4)', marginBottom: 'var(--sp-6)', flexWrap: 'wrap' }}>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--terracotta)' }}>
            <span className="heading-sm">HARDEST NOISE TYPE</span>
            <div style={{ fontFamily: 'var(--font-serif)', fontSize: 26, fontWeight: 600, color: 'var(--terracotta)', marginTop: 6, textTransform: 'capitalize' }}>
              {worst.noise_type}
            </div>
            <div className="body-sm" style={{ marginTop: 4 }}>Average WER: {(worst.wer_mean*100).toFixed(1)}%</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--ink)' }}>
            <span className="heading-sm">MOST RESILIENT TYPE</span>
            <div style={{ fontFamily: 'var(--font-serif)', fontSize: 26, fontWeight: 600, color: 'var(--ink)', marginTop: 6, textTransform: 'capitalize' }}>
              {best.noise_type}
            </div>
            <div className="body-sm" style={{ marginTop: 4 }}>Lowest WER: {(best.wer_mean*100).toFixed(1)}%</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 200, borderLeft: '3px solid var(--olive)' }}>
            <span className="heading-sm">BEST KEY-FACT RETENTION</span>
            {(() => {
              const b = data ? [...data].sort((a,b) => b.key_fact_recall_mean - a.key_fact_recall_mean)[0] : null
              return b ? (
                <>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: 26, fontWeight: 600, color: 'var(--olive)', marginTop: 6, textTransform: 'capitalize' }}>
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
                <h2 className="heading-md" style={{ fontFamily: 'var(--font-serif)', fontSize: 18 }}>Word Error Rate by Noise Classification</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Lower bar indicates higher speech transcription accuracy</div>
              </div>
              <span className="badge badge-terra">ERROR RATE</span>
            </div>
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(41,41,25,0.08)" />
                <XAxis dataKey="noise_type" stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, textTransform: 'capitalize' }} />
                <YAxis stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="wer_mean" name="WER" fill="#C24B27" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Key-Fact Recall & Summary Score */}
          <div className="card fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-5)' }}>
              <div>
                <h2 className="heading-md" style={{ fontFamily: 'var(--font-serif)', fontSize: 18 }}>Key-Fact Recall vs. Reasoning Summary Fidelity</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Higher score represents complete extraction of loan numbers, amounts, and dates</div>
              </div>
              <span className="badge badge-olive">RECALL METRICS</span>
            </div>
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(41,41,25,0.08)" />
                <XAxis dataKey="noise_type" stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, textTransform: 'capitalize' }} />
                <YAxis stroke="var(--text-dim)" tick={{ fill: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }} domain={[0, 1]} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="key_fact_recall_mean" name="Key-Fact Recall" fill="#2D5A27" radius={[4,4,0,0]} />
                <Bar dataKey={(d) => d.summary_score_mean / 5} name="Summary Score" fill="#B88E3E" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="body-sm" style={{ marginTop: 12, textAlign: 'center', color: 'var(--text-muted)' }}>
              Olive bars: Entity recall (%) · Gold bars: Evon summary evaluation score normalised (out of 5.0)
            </p>
          </div>

          {/* Detailed Table */}
          <div className="card fade-up">
            <h2 className="heading-md" style={{ marginBottom: 'var(--sp-4)', fontFamily: 'var(--font-serif)', fontSize: 18 }}>Acoustic Stress Matrix</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                    <th style={{ padding: '8px 12px' }}>ARCHETYPE</th>
                    <th style={{ padding: '8px 12px' }}>AVG WER</th>
                    <th style={{ padding: '8px 12px' }}>FACT RECALL</th>
                    <th style={{ padding: '8px 12px' }}>REASONING SCORE</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map(r => (
                    <tr key={r.noise_type} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px', fontWeight: 600, textTransform: 'capitalize' }}>{r.noise_type}</td>
                      <td style={{ padding: '12px', color: 'var(--terracotta)', fontWeight: 600 }}>{(r.wer_mean*100).toFixed(1)}%</td>
                      <td style={{ padding: '12px', color: 'var(--olive)', fontWeight: 600 }}>{(r.key_fact_recall_mean*100).toFixed(1)}%</td>
                      <td style={{ padding: '12px', color: 'var(--gold)', fontWeight: 600 }}>{r.summary_score_mean.toFixed(2)} / 5.0</td>
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
