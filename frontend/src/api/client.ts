import createClient from 'openapi-fetch'
import type { components, paths } from './schema'

export type Complaint = components['schemas']['ComplaintResponse']
export type ComplaintCreate = components['schemas']['ComplaintCreate']
export type ComplaintList = components['schemas']['ComplaintListResponse']
export type Stats = components['schemas']['StatsResponse']
export type StatusValue = components['schemas']['StatusUpdate']['status']

const client = createClient<paths>({ baseUrl: '' })

function errorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'detail' in error) {
    return String((error as { detail: unknown }).detail)
  }
  return 'Request failed'
}

export async function submitComplaint(payload: ComplaintCreate): Promise<Complaint> {
  const { data, error } = await client.POST('/api/complaints', { body: payload })
  if (error || !data) throw new Error(errorMessage(error))
  return data
}

export async function getComplaints(params: {
  category?: string
  priority?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<ComplaintList> {
  const { data, error } = await client.GET('/api/complaints', { params: { query: params } })
  if (error || !data) throw new Error(errorMessage(error))
  return data
}

export async function updateComplaintStatus(id: string, status: StatusValue): Promise<Complaint> {
  const { data, error } = await client.PATCH('/api/complaints/{complaint_id}/status', {
    params: { path: { complaint_id: id } },
    body: { status },
  })
  if (error || !data) throw new Error(errorMessage(error))
  return data
}

export async function getStats(): Promise<{ data: Stats; cache: 'HIT' | 'MISS' | 'UNKNOWN' }> {
  const { data, error, response } = await client.GET('/api/stats')
  if (error || !data) throw new Error(errorMessage(error))
  const header = response.headers.get('X-Cache')
  return { data, cache: header === 'HIT' || header === 'MISS' ? header : 'UNKNOWN' }
}
