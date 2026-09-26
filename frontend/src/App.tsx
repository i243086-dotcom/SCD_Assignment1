import { useState } from 'react'
import { DashboardPage } from './pages/DashboardPage'
import { StatsPage } from './pages/StatsPage'
import { SubmitPage } from './pages/SubmitPage'

type View = 'submit' | 'dashboard' | 'stats'

export function App() {
  const [view, setView] = useState<View>('submit')
  return (
    <>
      <header className="topbar">
        <div className="brand"><div className="brand-mark">CP</div><div><strong>CivicPulse</strong><small>Municipal Operations</small></div></div>
        <nav aria-label="Primary">
          {(['submit', 'dashboard', 'stats'] as View[]).map((item) => <button key={item} className={view === item ? 'active' : ''} onClick={() => setView(item)}>{item[0].toUpperCase() + item.slice(1)}</button>)}
        </nav>
      </header>
      <main className="shell">
        <section className="hero"><div><p className="eyebrow">Complaint intelligence platform</p><h1>From free text to an actionable queue.</h1><p>Replaceable AI triage, durable operations, observable infrastructure.</p></div><div className="live-dot"><span /> System UI</div></section>
        {view === 'submit' && <SubmitPage />}
        {view === 'dashboard' && <DashboardPage />}
        {view === 'stats' && <StatsPage />}
      </main>
    </>
  )
}
