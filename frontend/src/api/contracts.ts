/** Backend TypeScript interfaces mirroring API response schemas */

export interface Project {
  id: string
  title: string
  raw_prompt: string
  status: string
  created_at: string
  updated_at: string
}

export interface ParsedRole {
  role_name: string
  count: number
  seniority: 'junior' | 'mid' | 'senior' | 'lead' | 'unspecified'
  must_have_skills: string[]
  nice_to_have_skills: string[]
}

export interface ParsedConstraints {
  budget_min_usd: number | null
  budget_max_usd: number | null
  timeline_weeks: number | null
  timezone_overlap_required: boolean | null
}

export interface ParsedRequirements {
  project_summary: string
  roles: ParsedRole[]
  required_skills: string[]
  optional_skills: string[]
  constraints: ParsedConstraints | null
  confidence: number | null
}

export interface Match {
  freelancer_id: string
  matched_required_skills: string[]
  matched_optional_skills: string[]
  score: number
  rank: number
}

export interface FreelancerProfile {
  id: string
  display_name: string
  headline: string
  skills: string[]
  skills_normalized: string[]
  role_tags: string[]
  role_tags_normalized: string[]
  seniority: string
  hourly_rate_usd: number
  availability_hours_per_week: number
  timezone: string
  portfolio_links: string[]
  created_at: string
  updated_at: string
}

export interface MatchResponse {
  project_id: string
  match_set_id: string
  generated_at?: string
  total_candidates_scanned?: number
  matches: Match[]
}

/** API Error contract */
export interface APIError {
  detail: string
  status?: number
}

/** Grouped matches for UI display */
export interface RoleMatchGroup {
  role_name: string
  freelancers: (FreelancerProfile & { score: number; rank: number })[]
}
