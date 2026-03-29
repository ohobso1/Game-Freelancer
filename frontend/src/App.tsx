import './App.css'
import { useProjectFlow } from './hooks/useProjectFlow'
import { PromptForm } from './features/prompt/PromptForm'
import { ParsedRequirementsPanel } from './features/parsed/ParsedRequirementsPanel'
import { RoleGroupedMatches } from './features/matches/RoleGroupedMatches'

function App() {
  const flow = useProjectFlow()

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Game Freelancer Matcher</h1>
        <p>Find the perfect team for your game idea</p>
      </header>

      <main className="app-main">
        {flow.error && (
          <div className="error-banner">
            <p>{flow.error}</p>
            <button onClick={() => flow.clearError()}>Dismiss</button>
          </div>
        )}

        {flow.loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {!flow.loading && (
          <>
            {/* Step 1: Prompt Input */}
            {flow.flow === 'idle' || flow.flow === 'creating' ? (
              <section id="prompt-section">
                <h2>Step 1: Describe Your Game</h2>
                <PromptForm
                  onSubmit={flow.startFlow}
                  loading={flow.loading}
                />
              </section>
            ) : null}

            {/* Step 2: Parsed Requirements Verification */}
            {flow.parsed && (flow.flow === 'parsed' || flow.flow === 'matching' || flow.flow === 'results') ? (
              <section id="parsed-section">
                <h2>Step 2: Verify Requirements</h2>
                <ParsedRequirementsPanel
                  parsed={flow.parsed}
                  onProceed={flow.proceedToMatching}
                  loading={flow.flow === 'matching'}
                  onEdit={flow.reset}
                />
              </section>
            ) : null}

            {/* Step 3: Matched Freelancers */}
            {flow.matches && flow.flow === 'results' ? (
              <section id="matches-section">
                <h2>Step 3: Your Matched Freelancers</h2>
                <RoleGroupedMatches
                  matches={flow.matches}
                  freelancers={flow.freelancers}
                  parsedRoles={flow.parsed?.roles ?? []}
                  fetchFreelancer={flow.fetchFreelancer}
                  onStartNew={flow.reset}
                />
              </section>
            ) : null}
          </>
        )}
      </main>
    </div>
  )
}

export default App
