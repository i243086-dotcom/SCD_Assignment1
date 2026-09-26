import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { App } from '../src/App'

vi.mock('../src/api/client', () => ({
  getComplaints: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 10 }),
  getStats: vi.fn().mockResolvedValue({ data: { total: 0, by_category: {}, by_priority: {} }, cache: 'MISS' }),
  submitComplaint: vi.fn(),
  updateComplaintStatus: vi.fn(),
}))

test('navigation switches between required views', async () => {
  render(<App />)
  expect(screen.getByText('Report a municipal issue')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
  expect(await screen.findByText('Complaint queue')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Stats' }))
  expect(await screen.findByText('Operational statistics')).toBeInTheDocument()
})
