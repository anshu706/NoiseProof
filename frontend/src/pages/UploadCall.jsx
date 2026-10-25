import { useState, useRef } from 'react'
import { api } from '../api.js'

export default function UploadCall() {
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    const allowed = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/m4a', 'audio/aac', 'audio/x-m4a']
    if (!allowed.includes(f.type) && !f.name.match(/\.(wav|mp3|ogg|flac|m4a|aac)$/i)) {
      setError('Unsupported file type. Please upload WAV, MP3, OGG, FLAC, or M4A.')
      return
    }
    setFile(f)
    setResult(null)
    setError(null)
  }

  const analyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const r = await api.upload('/api/analyze', fd)
      if (r.detail) throw new Error(r.detail)
      setResult(r)
    } catch (e) {
      setError(e.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 'var(--sp-8) var(--sp-10)', maxWidth: 900 }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 'var(--sp-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span className="edition-tag">
            <span className="live-dot" />
            ON-DEMAND AUDIO INFERENCE
          </span>
          <span className="badge badge-beige">LIVE STT + SUMMARY</span>
        </div>
        <h1 className="heading-xl">
          Upload <em>Custom Call</em>
        </h1>
        <p className="body-md" style={{ color: 'var(--text-muted)', marginTop: 10 }}>
          Drop any real-world noisy telephonic audio recording for instant live speech-to-text decoding and reasoning summarisation.
        </p>
      </div>

      {/* Upload Zone */}
      <div
        className={`upload-zone fade-up ${dragging ? 'drag-over' : ''}`}
        style={{ marginBottom: 'var(--sp-5)' }}
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
      >
        <div style={{
          width: 54, height: 54, borderRadius: '50%',
          background: 'var(--surface-warm)',
          border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 22, margin: '0 auto 16px', color: 'var(--ink)'
        }}>
          🎙
        </div>
        <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, color: 'var(--ink)', fontSize: 20, marginBottom: 6 }}>
          {file ? file.name : 'Drop audio recording here or click to browse'}
        </div>
        <div className="body-sm" style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
          WAV · MP3 · OGG · FLAC · M4A · AAC (Auto-converted to 16 kHz mono)
        </div>
        <input
          ref={inputRef} type="file" accept="audio/*" style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />
      </div>

      {/* File Action Bar */}
      {file && !result && (
        <div className="card-sm fade-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-6)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 20 }}>📁</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--ink)' }}>{file.name}</div>
              <div className="body-sm" style={{ fontSize: 12 }}>{(file.size / 1024 / 1024).toFixed(2)} MB</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-secondary" onClick={() => { setFile(null); setError(null) }}>
              Clear
            </button>
            <button className="btn btn-primary" onClick={analyze} disabled={loading}>
              {loading ? <><span className="spinner" style={{ width: 14, height: 14, borderTopColor: '#F7F7EE' }} /> Processing…</> : '⚡ Run Gnani Inference'}
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="card fade-up" style={{ borderLeft: '3px solid var(--terracotta)', marginBottom: 'var(--sp-5)', background: 'var(--terracotta-bg)' }}>
          <div style={{ color: 'var(--terracotta)', fontSize: 14, fontWeight: 600 }}>
            ⚠ {error}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card fade-up" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: 'var(--sp-12)' }}>
          <div className="spinner" style={{ width: 40, height: 40, borderWidth: 3, borderTopColor: 'var(--ink)' }} />
          <div style={{ fontFamily: 'var(--font-serif)', color: 'var(--ink)', fontWeight: 600, fontSize: 18 }}>
            Decoding with Gnani Prisma v2.5…
          </div>
          <div className="body-sm" style={{ color: 'var(--text-muted)' }}>
            Filtering background noise and executing Evon reasoning pass
          </div>
        </div>
      )}

      {/* Analysis Result */}
      {result && (
        <div className="fade-up">
          {/* Quick Stats Grid */}
          <div className="grid-3" style={{ marginBottom: 'var(--sp-5)' }}>
            <div className="card" style={{ textAlign: 'center' }}>
              <span className="heading-sm">STT LATENCY</span>
              <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, color: 'var(--gold)', fontSize: 32, marginTop: 4 }}>
                {result.latency_ms.toFixed(0)} <span style={{ fontSize: 14, fontWeight: 400 }}>ms</span>
              </div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <span className="heading-sm">WORD COUNT</span>
              <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, color: 'var(--ink)', fontSize: 32, marginTop: 4 }}>
                {result.word_count} <span style={{ fontSize: 14, fontWeight: 400, color: 'var(--text-muted)' }}>words</span>
              </div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <span className="heading-sm">CUSTOMER SENTIMENT</span>
              <div style={{
                fontFamily: 'var(--font-serif)', fontWeight: 600, fontSize: 26, marginTop: 6,
                color: result.sentiment === 'positive' ? 'var(--olive)' : result.sentiment === 'negative' ? 'var(--terracotta)' : 'var(--ink)'
              }}>
                {result.sentiment === 'positive' ? '● Positive' : result.sentiment === 'negative' ? '● Negative' : '● Neutral'}
              </div>
            </div>
          </div>

          {/* Transcript Card */}
          <div className="card" style={{ marginBottom: 'var(--sp-5)', borderLeft: '3px solid var(--ink)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h2 className="heading-md" style={{ fontFamily: 'var(--font-serif)', fontSize: 18 }}>📝 Speech-to-Text Transcript</h2>
              <span className="badge badge-olive">Gnani Prisma v2.5</span>
            </div>
            <div style={{ fontSize: 14, lineHeight: 1.85, color: 'var(--text)', whiteSpace: 'pre-wrap', maxHeight: 300, overflowY: 'auto' }}>
              {result.transcript || 'No transcript generated.'}
            </div>
          </div>

          {/* Reasoning Summary Card */}
          <div className="card" style={{ marginBottom: 'var(--sp-5)', borderLeft: '3px solid var(--gold)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h2 className="heading-md" style={{ fontFamily: 'var(--font-serif)', fontSize: 18 }}>🧠 Intelligence Summary</h2>
              <span className="badge badge-beige">Gnani Evon v3.3</span>
            </div>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: 'var(--text)' }}>
              {result.summary || 'Summary unavailable.'}
            </p>
          </div>

          {/* Action Items & Key Facts */}
          <div className="grid-2" style={{ marginBottom: 'var(--sp-6)' }}>
            <div className="card">
              <div className="heading-sm" style={{ marginBottom: 12 }}>ACTION ITEMS EXTRACTED</div>
              {result.action_items?.length ? (
                <ul style={{ paddingLeft: 18 }}>
                  {result.action_items.map((a, i) => (
                    <li key={i} style={{ fontSize: 13, color: 'var(--text)', marginBottom: 8, lineHeight: 1.6 }}>{a}</li>
                  ))}
                </ul>
              ) : (
                <p className="body-sm">No action items identified.</p>
              )}
            </div>

            <div className="card">
              <div className="heading-sm" style={{ marginBottom: 12 }}>KEY FACTS & IDENTIFIERS</div>
              {result.key_facts?.length ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.key_facts.map((fact, i) => (
                    <span key={i} className="badge badge-muted" style={{ padding: '4px 10px', fontSize: 12 }}>
                      {fact}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="body-sm">No specific key facts captured.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
