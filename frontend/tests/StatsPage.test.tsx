import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { StatsPage } from '../src/pages/StatsPage'
import * as api from '../src/api/client'

vi.mock('../src/api/client', async () => {
  const actual = await vi.importActual<typeof import('../src/api/client')>('../src/api/client')
  return { ...actual, getStats: vi.fn() }
})

test('renders aggregate counts and X-Cache state', async () => {
  vi.mocked(api.getStats).mockResolvedValue({ data: { total: 3, by_category: { water: 2, roads: 1 }, by_priority: { high: 1, normal: 2 } }, cache: 'HIT' })
  render(<StatsPage />)
  expect(await screen.findByText('3')).toBeInTheDocument()
  expect(screen.getByText('HIT')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: /refresh stats/i }))
  expect(api.getStats).toHaveBeenCalledTimes(2)
})
