import { useEffect, useState } from 'react'
import * as C from '../../api/contracts'
import { groupMatchesByRole, batchFetchFreelancers } from './grouping'
import './RoleGroupedMatches.css'

interface RoleGroupedMatchesProps {
  matches: C.MatchResponse
  freelancers: Record<string, C.FreelancerProfile>
  parsedRoles: C.ParsedRole[]
  fetchFreelancer: (id: string) => Promise<C.FreelancerProfile | undefined>
  onStartNew: () => void
}

export function RoleGroupedMatches({
  matches,
  freelancers,
  parsedRoles,
  fetchFreelancer,
  onStartNew,
}: RoleGroupedMatchesProps) {
  const [groups, setGroups] = useState<C.RoleMatchGroup[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadMatches() {
      try {
        setLoading(true)

        // Get all freelancer IDs that need to be fetched
        const freelancerIds = matches.matches
          .map((m) => m.freelancer_id)
          .filter((id) => !freelancers[id])

        // Batch fetch missing freelancers
        if (freelancerIds.length > 0) {
          await batchFetchFreelancers(freelancerIds, fetchFreelancer, 6)
        }

        // Group by role
        const grouped = groupMatchesByRole(matches.matches, freelancers, parsedRoles)
        setGroups(grouped)
      } catch (err) {
        console.error('Failed to load matches:', err)
      } finally {
        setLoading(false)
      }
    }

    loadMatches()
  }, [matches, freelancers, parsedRoles, fetchFreelancer])

  if (loading) {
    return (
      <div className="matches-loading">
        <div className="spinner"></div>
        <p>Loading freelancer profiles...</p>
      </div>
    )
  }

  if (!groups || groups.length === 0) {
    return (
      <div className="matches-empty">
        <p>No matching freelancers found. Try adjusting your requirements.</p>
        <button onClick={onStartNew} className="action-button">
          Start New Search
        </button>
      </div>
    )
  }

  const totalMatches = groups.reduce((sum, g) => sum + g.freelancers.length, 0)

  return (
    <div className="role-grouped-matches">
      <div className="matches-header">
        <h3>Found {totalMatches} Matching Freelancers</h3>
        <p>Organized by required role</p>
      </div>

      <div className="role-columns-grid">
        {groups.map((group) => (
          <div key={group.role_name} className="role-column">
            <div className="role-column-header">
              <h4>{group.role_name}</h4>
              <span className="role-count">{group.freelancers.length}</span>
            </div>

            <div className="freelancer-list">
              {group.freelancers.map((freelancer) => (
                <div key={freelancer.id} className="freelancer-card">
                  <div className="freelancer-name">{freelancer.display_name}</div>

                  <div className="freelancer-meta">
                    <span className="meta-item">
                      <span className="meta-label">Experience</span>
                      <span className="meta-value">{freelancer.seniority}</span>
                    </span>
                    <span className="meta-item">
                      <span className="meta-label">Rate</span>
                      <span className="meta-value">${freelancer.hourly_rate_usd}/hr</span>
                    </span>
                  </div>

                  <div className="freelancer-skills">
                    {freelancer.skills_normalized.slice(0, 3).map((skill) => (
                      <span key={skill} className="skill-tag">
                        {skill}
                      </span>
                    ))}
                    {freelancer.skills_normalized.length > 3 && (
                      <span className="skill-tag skill-more">
                        +{freelancer.skills_normalized.length - 3}
                      </span>
                    )}
                  </div>

                  <div className="freelancer-score">
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${freelancer.score * 100}%` }} />
                    </div>
                    <span className="score-text">{(freelancer.score * 100).toFixed(0)}% match</span>
                  </div>

                  <div className="freelancer-footer">
                    <span className="timezone">{freelancer.timezone}</span>
                    <span className="seniority">{freelancer.availability_hours_per_week}h/week</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="matches-footer">
        <button onClick={onStartNew} className="action-button">
          Search Again
        </button>
      </div>
    </div>
  )
}
