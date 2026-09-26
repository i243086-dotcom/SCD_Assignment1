import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { DashboardPage } from '../src/pages/DashboardPage'
import * as api from '../src/api/client'

vi.mock('../src/api/client', async () => {
  const actual = await vi.importActual<typeof import('../src/api/client')>('../src/api/client')
  return { ...actual, getComplaints: vi.fn(), updateComplaintStatus: vi.fn() }
})

const item = {
  id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', text: 'Road broken near school gate.', location: 'Mardan', reporter_contact: null,
  category: 'roads' as const, priority: 'high' as const, status: 'open' as const, ai_summary: 'Road broken near school gate.', triaged_by: 'rules',
  triage_latency_ms: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), allowed_transitions: ['in_progress' as const, 'rejected' as const]
}

test('loads paginated queue and sends selected filters', async () => {
  vi.mocked(api.getComplaints).mockResolvedValue({ items: [item], total: 1, page: 1, page_size: 10 })
  render(<DashboardPage />)
  expect(await screen.findByText('Road broken near school gate.')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Category'), { target: { value: 'roads' } })
  await waitFor(() => expect(api.getComplaints).toHaveBeenLastCalledWith(expect.objectContaining({ category: 'roads', page: 1 })))
})

test('surfaces backend transition error verbatim', async () => {
  vi.mocked(api.getComplaints).mockResolvedValue({ items: [item], total: 1, page: 1, page_size: 10 })
  vi.mocked(api.updateComplaintStatus).mockRejectedValue(new Error('Invalid status transition: open -> resolved'))
  render(<DashboardPage />)
  const button = await screen.findByRole('button', { name: 'in progress' })
  fireEvent.click(button)
  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid status transition: open -> resolved')
})
