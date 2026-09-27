import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { SubmitPage } from '../src/pages/SubmitPage'
import * as api from '../src/api/client'

vi.mock('../src/api/client', async () => {
  const actual = await vi.importActual<typeof import('../src/api/client')>('../src/api/client')
  return { ...actual, submitComplaint: vi.fn() }
})

const created = {
  id: '11111111-1111-1111-1111-111111111111', text: 'Burst water main flooding the road.', location: 'Street 12', reporter_contact: null,
  category: 'water' as const, priority: 'high' as const, status: 'open' as const, ai_summary: 'Burst water main flooding the road.',
  triaged_by: 'simulated', triage_latency_ms: 22, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), allowed_transitions: ['in_progress' as const, 'rejected' as const]
}

test('client-side validation blocks too-short complaint', async () => {
  render(<SubmitPage />)
  fireEvent.change(screen.getByLabelText(/complaint/i), { target: { value: 'short' } })
  fireEvent.change(screen.getByLabelText('Location'), { target: { value: 'Peshawar' } })
  fireEvent.click(screen.getByRole('button', { name: /submit complaint/i }))
  expect(await screen.findByRole('alert')).toHaveTextContent('at least 10 characters')
  expect(api.submitComplaint).not.toHaveBeenCalled()
})

test('shows honest loading state and renders triage result', async () => {
  let resolve!: (value: typeof created) => void
  vi.mocked(api.submitComplaint).mockImplementation(() => new Promise((r) => { resolve = r }))
  render(<SubmitPage />)
  fireEvent.change(screen.getByLabelText(/complaint/i), { target: { value: created.text } })
  fireEvent.change(screen.getByLabelText('Location'), { target: { value: created.location } })
  fireEvent.click(screen.getByRole('button', { name: /submit complaint/i }))
  expect(screen.getByRole('button', { name: /ai triage in progress/i })).toBeDisabled()
  expect(screen.getByText(/can take several seconds/i)).toBeInTheDocument()
  resolve(created)
  await waitFor(() => expect(screen.getByTestId('triage-result')).toBeInTheDocument())
  expect(screen.getByText('water')).toBeInTheDocument()
  expect(screen.getByText('simulated')).toBeInTheDocument()
})
