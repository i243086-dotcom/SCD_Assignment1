import { useEffect, useState } from 'react'
import { getStats, type Stats } from '../api/client'
import { Badge } from '../components/Badge'

export function StatsPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [cache, setCache] = useState<'HIT' | 'MISS' | 'UNKNOWN'>('UNKNOWN')
  const [error, setError] = useState('')

  async function load() {
    try {
      const response = await getStats()
      setStats(response.data)
      setCache(response.cache)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats')
    }
  }

  useEffect(() => { void load() }, [])

  return (
    <section className="panel">
      <div className="section-heading">
        <div><p className="eyebrow">Live aggregates</p><h2>Operational statistics</h2></div>
        <div className="cache-chip">X-Cache <Badge tone={cache === 'HIT' ? 'ok' : cache === 'MISS' ? 'warn' : 'neutral'}>{cache}</Badge></div>
      </div>
      {error && <div className="alert" role="alert">{error}</div>}
      {!stats ? <div className="empty-state">Loading statistics…</div> : (
        <>
          <div className="metric"><span>Total complaints</span><strong>{stats.total}</strong></div>
          <div className="stats-grid">
            <div><h3>By category</h3>{Object.entries(stats.by_category).map(([name, value]) => <div className="bar-row" key={name}><span>{name}</span><b>{value}</b></div>)}</div>
            <div><h3>By priority</h3>{Object.entries(stats.by_priority).map(([name, value]) => <div className="bar-row" key={name}><span>{name}</span><b>{value}</b></div>)}</div>
          </div>
          <button onClick={() => void load()}>Refresh stats</button>
        </>
      )}
    </section>
  )
}
