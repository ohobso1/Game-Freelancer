
import * as C from '../../api/contracts'

/**
 * Group matches by role using a 3-layer fallback strategy:
 * 1. Match freelancer's role_tags_normalized with parsed roles
 * 2. Infer from matched skills overlap with required skills
 * 3. Default to "Other"
 */
export function groupMatchesByRole(
  matches: C.Match[],
  freelancers: Record<string, C.FreelancerProfile>,
  parsedRoles: C.ParsedRole[]
): C.RoleMatchGroup[] {
  const groupedByRole: Record<string, (C.FreelancerProfile & { score: number; rank: number })[]> = {}

  // Initialize groups for all parsed roles
  parsedRoles.forEach((role) => {
    groupedByRole[role.role_name] = []
  })
  groupedByRole['Other'] = []

  // Process each match
  matches.forEach((match) => {
    const freelancer = freelancers[match.freelancer_id]
    if (!freelancer) return

    const enriched = {
      ...freelancer,
      score: match.score,
      rank: match.rank,
    }

    // Layer 1: Use freelancer's role tags
    if (freelancer.role_tags_normalized && freelancer.role_tags_normalized.length > 0) {
      for (const tag of freelancer.role_tags_normalized) {
        // Check if this normalized tag matches any parsed role (case-insensitive)
        const matchedRole = parsedRoles.find((r) =>
          r.role_name.toLowerCase().includes(tag.toLowerCase()) ||
          tag.toLowerCase().includes(r.role_name.toLowerCase())
        )
        if (matchedRole) {
          groupedByRole[matchedRole.role_name].push(enriched)
          return
        }
      }
    }

    // Layer 2: Infer from skill overlap
    if (match.matched_required_skills && match.matched_required_skills.length > 0) {
      // Find which role has the most matching skills
      let bestRole: C.ParsedRole | undefined
      let bestMatchCount = 0

      parsedRoles.forEach((role) => {
        // This is a simple heuristic - count matching skills
        const matchCount = match.matched_required_skills.length
        if (matchCount > bestMatchCount) {
          bestMatchCount = matchCount
          bestRole = role
        }
      })

      if (bestRole) {
        groupedByRole[bestRole.role_name].push(enriched)
        return
      }
    }

    // Layer 3: Fallback to first required role or "Other"
    const firstRole = parsedRoles[0]
    if (firstRole && groupedByRole[firstRole.role_name].length < 10) {
      // Avoid overloading the first role
      groupedByRole[firstRole.role_name].push(enriched)
    } else {
      groupedByRole['Other'].push(enriched)
    }
  })

  // Convert to array and sort within each group
  const result: C.RoleMatchGroup[] = Object.entries(groupedByRole)
    .map(([roleName, freelancers]) => ({
      role_name: roleName,
      freelancers: freelancers.sort((a, b) => {
        // Sort by score descending, then by rank ascending
        if (b.score !== a.score) return b.score - a.score
        return a.rank - b.rank
      }),
    }))
    .filter((group) => group.freelancers.length > 0) // Remove empty groups

  return result
}

/**
 * Fetch freelancer details in batches with controlled concurrency
 */
export async function batchFetchFreelancers(
  freelancerIds: string[],
  fetchFn: (id: string) => Promise<C.FreelancerProfile | undefined>,
  batchSize: number = 6
): Promise<Record<string, C.FreelancerProfile>> {
  const results: Record<string, C.FreelancerProfile> = {}

  for (let i = 0; i < freelancerIds.length; i += batchSize) {
    const batch = freelancerIds.slice(i, i + batchSize)
    const batchResults = await Promise.all(batch.map(fetchFn))

    batchResults.forEach((freelancer) => {
      if (freelancer) {
        results[freelancer.id] = freelancer
      }
    })
  }

  return results
}
