export function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'neutral' | 'high' | 'ok' | 'warn' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}
