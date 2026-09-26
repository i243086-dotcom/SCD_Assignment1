import { expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '../src/components/ErrorBoundary'

function Broken(): JSX.Element { throw new Error('render exploded') }

test('error boundary renders a recovery surface', () => {
  const spy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
  render(<ErrorBoundary><Broken /></ErrorBoundary>)
  expect(screen.getByRole('alert')).toHaveTextContent('render exploded')
  spy.mockRestore()
})
