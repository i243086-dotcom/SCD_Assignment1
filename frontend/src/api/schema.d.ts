/**
 * OpenAPI client surface for CivicPulse.
 * Regenerate from the running backend with: npm run api:generate
 */
export interface paths {
  '/api/complaints': {
    get: operations['listComplaints']
    post: operations['createComplaint']
  }
  '/api/complaints/{complaint_id}': {
    get: operations['getComplaint']
  }
  '/api/complaints/{complaint_id}/status': {
    patch: operations['updateStatus']
  }
  '/api/stats': { get: operations['getStats'] }
  '/api/meta/providers': { get: operations['providerMeta'] }
}

export interface components {
  schemas: {
    ComplaintCreate: { text: string; location: string; reporter_contact?: string | null }
    ComplaintResponse: {
      id: string
      text: string
      location: string
      reporter_contact: string | null
      category: 'water' | 'electricity' | 'sanitation' | 'roads' | 'streetlights' | 'other'
      priority: 'high' | 'normal' | 'low'
      status: 'open' | 'in_progress' | 'resolved' | 'rejected'
      ai_summary: string | null
      triaged_by: string
      triage_latency_ms: number
      created_at: string
      updated_at: string
      allowed_transitions: Array<'open' | 'in_progress' | 'resolved' | 'rejected'>
    }
    ComplaintListResponse: {
      items: components['schemas']['ComplaintResponse'][]
      total: number
      page: number
      page_size: number
    }
    StatsResponse: {
      by_category: Record<string, number>
      by_priority: Record<string, number>
      total: number
    }
    StatusUpdate: { status: 'open' | 'in_progress' | 'resolved' | 'rejected' }
    ProviderMetaResponse: {
      active_provider: string
      outcomes: Array<{ provider: string; latency_ms: number; fallback: boolean; error_class?: string | null }>
    }
  }
}

export interface operations {
  createComplaint: {
    requestBody: { content: { 'application/json': components['schemas']['ComplaintCreate'] } }
    responses: { 201: { content: { 'application/json': components['schemas']['ComplaintResponse'] } } }
  }
  listComplaints: {
    parameters: { query?: { category?: string; priority?: string; status?: string; page?: number; page_size?: number } }
    responses: { 200: { content: { 'application/json': components['schemas']['ComplaintListResponse'] } } }
  }
  getComplaint: {
    parameters: { path: { complaint_id: string } }
    responses: { 200: { content: { 'application/json': components['schemas']['ComplaintResponse'] } } }
  }
  updateStatus: {
    parameters: { path: { complaint_id: string } }
    requestBody: { content: { 'application/json': components['schemas']['StatusUpdate'] } }
    responses: { 200: { content: { 'application/json': components['schemas']['ComplaintResponse'] } } }
  }
  getStats: { responses: { 200: { content: { 'application/json': components['schemas']['StatsResponse'] } } } }
  providerMeta: { responses: { 200: { content: { 'application/json': components['schemas']['ProviderMetaResponse'] } } } }
}
