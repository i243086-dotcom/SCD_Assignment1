import React from 'react'

type State = { hasError: boolean; message: string }

export class ErrorBoundary extends React.Component<React.PropsWithChildren, State> {
  state: State = { hasError: false, message: '' }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message }
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="shell">
          <section className="panel error-panel" role="alert">
            <h1>Something went wrong</h1>
            <p>{this.state.message}</p>
            <button onClick={() => window.location.reload()}>Reload</button>
          </section>
        </main>
      )
    }
    return this.props.children
  }
}
