import { useCallback, useEffect, useState } from 'react'
import { getComplaints, updateComplaintStatus, type Complaint, type StatusValue } from '../api/client'
import { Badge } from '../components/Badge'

const categories = ['', 'water', 'electricity', 'sanitation', 'roads', 'streetlights', 'other']
const priorities = ['', 'high', 'normal', 'low']
const statuses = ['', 'open', 'in_progress', 'resolved', 'rejected']

export function DashboardPage() {
  const [items, setItems] = useState<Complaint[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [priority, setPriority] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const pageSize = 10

  const load = useCallback(async () => {
    setError('')
    try {
      const data = await getComplaints({ category: category || undefined, priority: priority || undefined, status: status || undefined, page, page_size: pageSize })
      setItems(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load complaints')
    }
  }, [category, priority, status, page])

  useEffect(() => { void load() }, [load])

  async function advance(item: Complaint, next: StatusValue) {
    try {
      await updateComplaintStatus(item.id, next)
      await load()
    } catch (err) {
      // The API client's Error preserves the backend's detail, including 409 transition text.
      setError(err instanceof Error ? err.message : 'Status update failed')
    }
  }

  const pages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <section className="panel">
      <div className="section-heading"><div><p className="eyebrow">Operations</p><h2>Complaint queue</h2></div><Badge>{total} total</Badge></div>
      <div className="filters">
        <label>Category<select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1) }}>{categories.map((v) => <option key={v} value={v}>{v || 'All'}</option>)}</select></label>
        <label>Priority<select value={priority} onChange={(e) => { setPriority(e.target.value); setPage(1) }}>{priorities.map((v) => <option key={v} value={v}>{v || 'All'}</option>)}</select></label>
        <label>Status<select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }}>{statuses.map((v) => <option key={v} value={v}>{v || 'All'}</option>)}</select></label>
      </div>
      {error && <div className="alert" role="alert">{error}</div>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>Issue</th><th>Location</th><th>Category</th><th>Priority</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.ai_summary || item.text}</strong><small className="table-id">{item.id.slice(0, 8)}</small></td>
                <td>{item.location}</td>
                <td><Badge>{item.category}</Badge></td>
                <td><Badge tone={item.priority === 'high' ? 'high' : item.priority === 'low' ? 'ok' : 'warn'}>{item.priority}</Badge></td>
                <td>{item.status}</td>
                <td className="actions">
                  {item.allowed_transitions.map((next) => <button key={next} onClick={() => void advance(item, next)}>{next.replace('_', ' ')}</button>)}
                  {!item.allowed_transitions.length && <span className="muted">Terminal</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pagination"><button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button><span>Page {page} of {pages}</span><button disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next</button></div>
    </section>
  )
}
