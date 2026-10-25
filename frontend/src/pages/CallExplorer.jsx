import { useEffect, useState } from 'react'
import { api, audioUrl } from '../api.js'

function WordDiff({ reference, hypothesis }) {
  if (!reference || !hypothesis) {
    return <p className="body-sm" style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>No transcript available for this condition.</p>
  }

  const refWords = reference.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(Boolean)
  const hypWords = hypothesis.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(Boolean)
  const refSet = new Set(refWords)

  return (
    <div style={{ lineHeight: 1.85, fontSize: 13, fontFamily: 'var(--font)' }}>
      {hypWords.map((w, i) => {
        const isMatch = refSet.has(w)
        return (
          <span
            key={i}
            className={`diff-word ${isMatch ? 'diff-ok' : 'diff-wrong'}`}
            title={isMatch ? 'Accurate match' : 'Deviation / Misrecognition under noise'}
          >
            {w}{' '}
          </span>
        )
      })}
    </div>
  )
}

export default function CallExplorer() {
  const [calls, setCalls] = useState([])
  const [selectedCall, setSelectedCall] = useState(null)
  const [callDetail, setCallDetail] = useState(null)
  const [noiseType, setNoiseType] = useState('street')
  const [snr, setSnr] = useState('20')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/api/calls').then(res => {
      setCalls(res)
      if (res.length > 0 && !selectedCall) {
        setSelectedCall(res[0].call_id)
      }
    }).catch(() => {
      setCalls([{ call_id: 'call_001', scenario: 'Loan EMI reminder – customer missed payment', turns: 8, outcome: 'Acknowledged payment' }])
      setSelectedCall('call_001')
    })
  }, [])

  useEffect(() => {
    if (!selectedCall) return
    setLoading(true)
    api.get(`/api/calls/${selectedCall}`)
      .then(setCallDetail)
      .catch(() => setCallDetail(null))
      .finally(() => setLoading(false))
  }, [selectedCall])

  const transcript = callDetail?.transcripts?.find(
    t => t.noise_type === noiseType && String(t.snr) === String(snr)
  )
  const refText = callDetail?.reference_transcript || ''

  const NOISE_TYPES = ['street', 'crowd', 'wind', 'white', 'market']
  const SNR_LEVELS = ['clean', '20', '10', '5', '0']

  return (
    <div style={{ padding: 'var(--sp-8) var(--sp-10)', maxWidth: 1200 }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span className="edition-tag">
            <span className="live-dot" />
            AUDIO INSPECTION CONSOLE
          </span>
          <span className="badge badge-beige">PRISMA v2.5 DECODER</span>
        </div>
        <h1 className="heading-xl">
          Call <em>Explorer</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 10 }}>
          Side-by-side A/B waveform listening between clean synthetic master audio and telephone-degraded noise variants with word-level error highlighting.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '290px 1fr', gap: 'var(--sp-6)' }}>
        {/* Left Column – Call Selector & Controls */}
        <div>
          {/* Calls List */}
          <div className="card" style={{ marginBottom: 'var(--sp-4)' }}>
            <div className="heading-sm" style={{ marginBottom: 14 }}>01 // GENERATED CALLS</div>
            {calls.length === 0 && (
              <p className="body-sm" style={{ color: 'var(--text-muted)' }}>
                No calls generated yet. Launch a benchmark from the Run Pipeline page.
              </p>
            )}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {calls.map(c => {
                const isSel = selectedCall === c.call_id
                return (
                  <button
                    key={c.call_id}
                    onClick={() => setSelectedCall(c.call_id)}
                    style={{
                      display: 'block', width: '100%', textAlign: 'left', padding: '12px 14px',
                      borderRadius: 8, border: isSel ? '1px solid var(--ink)' : '1px solid var(--border)',
                      cursor: 'pointer',
                      background: isSel ? 'var(--surface-warm)' : '#FFFFFF',
                      boxShadow: isSel ? 'var(--shadow-sm)' : 'none',
                      color: 'var(--ink)', fontFamily: 'var(--font)', transition: 'all 180ms ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, fontSize: 13, color: isSel ? 'var(--ink)' : 'var(--text-muted)' }}>{c.call_id}</span>
                      <span className="badge badge-muted" style={{ fontSize: 10 }}>{c.turns || 8} turns</span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {c.scenario || 'Customer call scenario'}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Condition Matrix Selectors */}
          {selectedCall && (
            <div className="card">
              <div className="heading-sm" style={{ marginBottom: 10 }}>02 // BACKGROUND NOISE</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 18 }}>
                {NOISE_TYPES.map(n => (
                  <button
                    key={n}
                    onClick={() => setNoiseType(n)}
                    className={`btn ${noiseType === n ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', fontSize: 12, textTransform: 'capitalize' }}
                  >
                    {n}
                  </button>
                ))}
              </div>

              <div className="heading-sm" style={{ marginBottom: 10 }}>03 // SIGNAL-TO-NOISE RATIO</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {SNR_LEVELS.map(s => (
                  <button
                    key={s}
                    onClick={() => setSnr(s)}
                    className={`btn ${String(snr) === String(s) ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', fontSize: 12, fontFamily: 'var(--font-mono)' }}
                  >
                    {s === 'clean' ? 'Clean' : `${s} dB`}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column – Audio Players & Side-by-Side Transcripts */}
        <div>
          {!selectedCall && (
            <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 320, color: 'var(--text-muted)' }}>
              Select a call to begin side-by-side inspection
            </div>
          )}

          {loading && (
            <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 320 }}>
              <div className="spinner" />
            </div>
          )}

          {callDetail && !loading && (
            <div className="fade-up">
              {/* Dual Audio Players */}
              <div className="grid-2" style={{ marginBottom: 'var(--sp-4)' }}>
                {/* Clean Audio Player */}
                <div className="card" style={{ borderLeft: '3px solid var(--ink)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <div className="heading-sm" style={{ color: 'var(--ink)' }}>🎙 Clean Master Recording</div>
                    <span className="badge badge-olive">Timbre v2.5 · 22 kHz</span>
                  </div>
                  {callDetail.clean_audio_url ? (
                    <audio controls src={audioUrl(callDetail.clean_audio_url)} style={{ marginTop: 6 }} />
                  ) : (
                    <p className="body-sm">Audio pending generation.</p>
                  )}
                </div>

                {/* Noisy Audio Player */}
                <div className="card" style={{ borderLeft: '3px solid var(--terracotta)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <div className="heading-sm" style={{ color: 'var(--terracotta)' }}>
                      📡 Noisy Simulation ({noiseType} @ {snr === 'clean' ? 'Clean' : `${snr} dB`})
                    </div>
                    <span className="badge badge-terra">Telephone Band (8 kHz)</span>
                  </div>
                  {(() => {
                    const noisyUrl = callDetail.noisy_variants?.find(v => v.includes(`${noiseType}_${snr}`))
                    return noisyUrl ? (
                      <audio controls src={audioUrl(noisyUrl)} style={{ marginTop: 6 }} />
                    ) : (
                      <p className="body-sm" style={{ color: 'var(--text-muted)', marginTop: 8 }}>
                        Variant not pre-baked. Run pipeline with this condition to listen.
                      </p>
                    )
                  })()}
                </div>
              </div>

              {/* Transcripts Comparison */}
              <div className="grid-2" style={{ marginBottom: 'var(--sp-4)' }}>
                {/* Ground Truth Reference */}
                <div className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <span className="heading-sm">📄 Ground Truth Reference</span>
                    <span className="badge badge-muted">Exact Script</span>
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.85, maxHeight: 280, overflowY: 'auto', paddingRight: 6 }}>
                    {refText || 'No reference text available.'}
                  </div>
                </div>

                {/* STT Output with Word Diff */}
                <div className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <div className="heading-sm" style={{ color: 'var(--ink)' }}>🤖 Prisma v2.5 STT Transcript</div>
                    <span className="badge badge-olive">Live Decoder</span>
                  </div>
                  <div style={{ maxHeight: 280, overflowY: 'auto', paddingRight: 6 }}>
                    {transcript ? (
                      <WordDiff reference={refText} hypothesis={transcript.transcript} />
                    ) : (
                      <p className="body-sm" style={{ color: 'var(--text-muted)' }}>
                        No transcript recorded for {noiseType} @ {snr} dB.
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Call Script Dialogue Turns */}
              {callDetail.script?.script && (
                <div className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                    <span className="heading-sm">📞 Full Hinglish Dialogue Dialogue Breakdown</span>
                    <span className="badge badge-muted">{callDetail.script.script.length} Alternating Turns</span>
                  </div>
                  <div style={{ maxHeight: 260, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8, paddingRight: 6 }}>
                    {callDetail.script.script.map((turn, i) => {
                      const isAgent = turn.speaker === 'agent'
                      return (
                        <div
                          key={i}
                          style={{
                            display: 'flex', gap: 12, alignItems: 'flex-start',
                            padding: '10px 14px', borderRadius: 6,
                            background: isAgent ? 'var(--surface-warm)' : '#FFFFFF',
                            border: '1px solid var(--border)',
                            borderLeft: `3px solid ${isAgent ? 'var(--ink)' : 'var(--gold)'}`,
                          }}
                        >
                          <span style={{
                            fontSize: 11, fontWeight: 700,
                            color: isAgent ? 'var(--ink)' : 'var(--gold)',
                            width: 70, flexShrink: 0, paddingTop: 2,
                            textTransform: 'uppercase', fontFamily: 'var(--font-mono)'
                          }}>
                            {turn.speaker}
                          </span>
                          <span style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6 }}>{turn.text}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
