import * as C from '../../api/contracts'
import './ParsedRequirementsPanel.css'

interface ParsedRequirementsPanelProps {
  parsed: C.ParsedRequirements
  onProceed: () => Promise<void>
  loading: boolean
  onEdit: () => void
}

export function ParsedRequirementsPanel({
  parsed,
  onProceed,
  loading,
  onEdit,
}: ParsedRequirementsPanelProps) {
  return (
    <div className="parsed-panel">
      <div className="parsed-header">
        <h3>Parsed Requirements</h3>
        <p className="parsed-subtitle">
          Review the AI interpretation of your game project before finding matches
        </p>
      </div>

      <div className="parsed-content">
        {/* Roles Section */}
        <section className="parsed-section">
          <h4 className="parsed-section-title">Required Roles</h4>
          <div className="roles-grid">
            {parsed.roles && parsed.roles.length > 0 ? (
              parsed.roles.map((role, idx) => (
                <div key={idx} className="role-card">
                  <div className="role-name">{role.role_name}</div>
                  <div className="role-details">
                    <span className="role-count">{role.count}x</span>
                    <span className="role-seniority">{role.seniority}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="empty-text">No roles parsed</p>
            )}
          </div>
        </section>

        {/* Skills Section */}
        <section className="parsed-section">
          <h4 className="parsed-section-title">Required Skills</h4>
          <div className="skills-list">
            {parsed.required_skills && parsed.required_skills.length > 0 ? (
              parsed.required_skills.map((skill, idx) => (
                <span key={idx} className="skill-badge skill-required">
                  {skill}
                </span>
              ))
            ) : (
              <p className="empty-text">No required skills identified</p>
            )}
          </div>

          <h4 className="parsed-section-title">Nice-to-Have Skills</h4>
          <div className="skills-list">
            {parsed.optional_skills && parsed.optional_skills.length > 0 ? (
              parsed.optional_skills.map((skill, idx) => (
                <span key={idx} className="skill-badge skill-optional">
                  {skill}
                </span>
              ))
            ) : (
              <p className="empty-text">No optional skills identified</p>
            )}
          </div>
        </section>

        {/* Project Details Section */}
        <section className="parsed-section">
          <h4 className="parsed-section-title">Project Details</h4>
          <p className="empty-text" style={{ marginBottom: '1rem' }}>{parsed.project_summary}</p>
          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">Required Roles</span>
              <span className="detail-value">{parsed.roles.length}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Confidence</span>
              <span className="detail-value">
                {parsed.confidence != null ? `${Math.round(parsed.confidence * 100)}%` : 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Timeline</span>
              <span className="detail-value">
                {parsed.constraints?.timeline_weeks != null ? `${parsed.constraints.timeline_weeks} weeks` : 'Unspecified'}
              </span>
            </div>
            {parsed.constraints?.budget_max_usd != null && (
              <div className="detail-item">
                <span className="detail-label">Budget Max</span>
                <span className="detail-value">${parsed.constraints.budget_max_usd}</span>
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="parsed-actions">
        <button
          className="action-button edit-button"
          onClick={onEdit}
          disabled={loading}
        >
          Edit Project
        </button>
        <button
          className="action-button proceed-button"
          onClick={onProceed}
          disabled={loading}
        >
          {loading ? 'Finding Matches...' : 'Find Matching Freelancers'}
        </button>
      </div>
    </div>
  )
}
