import { FormEvent, useState } from 'react'
import { submitComplaint, type Complaint } from '../api/client'
import { Badge } from '../components/Badge'

export function SubmitPage() {
  const [text, setText] = useState('')
  const [location, setLocation] = useState('')
  const [contact, setContact] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Complaint | null>(null)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setResult(null)
    if (text.trim().length < 10) return setError('Complaint text must be at least 10 characters.')
    if (location.trim().length < 3) return setError('Location must be at least 3 characters.')
    setLoading(true)
    try {
      const created = await submitComplaint({
        text: text.trim(),
        location: location.trim(),
        reporter_contact: contact.trim() || null,
      })
      setResult(created)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid two-col">
      <section className="panel">
        <div className="section-heading">
          <div><p className="eyebrow">Citizen intake</p><h2>Report a municipal issue</h2></div>
        </div>
        <form onSubmit={onSubmit} className="form-stack">
          <label>Complaint
            <textarea value={text} onChange={(e) => setText(e.target.value)} minLength={10} maxLength={2000} rows={7} placeholder="e.g. Burst water main flooding Street 12 since fajr..." />
            <small>{text.length}/2000</small>
          </label>
          <label>Location
            <input value={location} onChange={(e) => setLocation(e.target.value)} minLength={3} maxLength={200} placeholder="Street / area / city" />
          </label>
          <label>Contact <span className="muted">(optional)</span>
            <input value={contact} onChange={(e) => setContact(e.target.value)} maxLength={200} placeholder="Phone or email" />
          </label>
          {error && <div className="alert" role="alert">{error}</div>}
          <button className="primary" disabled={loading}>{loading ? 'AI triage in progress…' : 'Submit complaint'}</button>
          {loading && <p className="muted" aria-live="polite">The triage provider can take several seconds. Your complaint will still be accepted if the external AI fails.</p>}
        </form>
      </section>

      <section className="panel result-panel">
        <p className="eyebrow">Triage result</p>
        {!result ? <div className="empty-state">Submit a complaint to see category, priority, summary and provider.</div> : (
          <div className="result-card" data-testid="triage-result">
            <div className="result-row"><span>Category</span><Badge>{result.category}</Badge></div>
            <div className="result-row"><span>Priority</span><Badge tone={result.priority === 'high' ? 'high' : result.priority === 'low' ? 'ok' : 'warn'}>{result.priority}</Badge></div>
            <div className="summary-box"><span>AI summary</span><strong>{result.ai_summary}</strong></div>
            <div className="result-row"><span>Provider</span><code>{result.triaged_by}</code></div>
            <div className="result-row"><span>Latency</span><span>{result.triage_latency_ms} ms</span></div>
          </div>
        )}
      </section>
    </div>
  )
}
