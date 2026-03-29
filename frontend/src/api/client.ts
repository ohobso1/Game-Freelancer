import * as C from './contracts'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const REQUEST_TIMEOUT = 15000 // 15 seconds

type RawProject = Omit<C.Project, 'id'> & { id?: string; _id?: string }
type RawParseResponse = {
  project_id: string
  requirements_id: string
  parsed_requirements: C.ParsedRequirements
}
type RawFreelancer = Omit<C.FreelancerProfile, 'id'> & { id?: string; _id?: string }

function toProject(raw: RawProject): C.Project {
  return {
    ...raw,
    id: raw.id ?? raw._id ?? '',
  }
}

function toFreelancer(raw: RawFreelancer): C.FreelancerProfile {
  return {
    ...raw,
    id: raw.id ?? raw._id ?? '',
  }
}

/** Fetch with timeout and error handling */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })

    if (!response.ok) {
      let detail = response.statusText || 'Request failed'
      try {
        const body = await response.json()
        if (body?.detail && typeof body.detail === 'string') {
          detail = body.detail
        }
      } catch {
        // Ignore JSON parse errors and keep default detail.
      }
      throw new Error(`${detail} (HTTP ${response.status})`)
    }

    return response
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.')
    }
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: unable to reach API server')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

/** Create a new project from prompt */
export async function createProject(
  title: string,
  raw_prompt: string
): Promise<C.Project> {
  const url = `${API_BASE_URL}/projects`
  const response = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, raw_prompt }),
  })

  const raw = (await response.json()) as RawProject
  return toProject(raw)
}

/** Parse a project's prompt with Gemini */
export async function parseProject(projectId: string): Promise<C.ParsedRequirements> {
  const url = `${API_BASE_URL}/parsing`
  const response = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId }),
  })

  const raw = (await response.json()) as RawParseResponse
  return raw.parsed_requirements
}

/** Generate matches for a project */
export async function createMatches(
  projectId: string,
  topN: number = 20
): Promise<C.MatchResponse> {
  const url = `${API_BASE_URL}/matching/${projectId}?top_n=${topN}`
  const response = await fetchWithTimeout(url, {
    method: 'POST',
  })

  return response.json()
}

/** Get latest matches for a project (cached) */
export async function getMatches(projectId: string): Promise<C.MatchResponse> {
  const url = `${API_BASE_URL}/matching/${projectId}`
  const response = await fetchWithTimeout(url, {
    method: 'GET',
  })

  return response.json()
}

/** Fetch a single freelancer profile by ID */
export async function getFreelancer(freelancerId: string): Promise<C.FreelancerProfile> {
  const url = `${API_BASE_URL}/freelancers/${freelancerId}`
  const response = await fetchWithTimeout(url, {
    method: 'GET',
  })

  const raw = (await response.json()) as RawFreelancer
  return toFreelancer(raw)
}
