import { useState, useCallback } from 'react'
import * as API from '../api/client'
import * as C from '../api/contracts'

type FlowState = 'idle' | 'creating' | 'parsing' | 'parsed' | 'matching' | 'results'

interface ProjectFlowState {
  flow: FlowState
  projectId?: string
  parsed?: C.ParsedRequirements
  matches?: C.MatchResponse
  freelancers: Record<string, C.FreelancerProfile>
  error?: string
  loading: boolean
}

interface ProjectFlowActions {
  startFlow: (title: string, prompt: string) => Promise<void>
  retryParsing: () => Promise<void>
  proceedToMatching: () => Promise<void>
  retryMatching: () => Promise<void>
  reset: () => void
  clearError: () => void
  fetchFreelancer: (id: string) => Promise<C.FreelancerProfile | undefined>
}

export function useProjectFlow(): ProjectFlowState & ProjectFlowActions {
  const [state, setState] = useState<ProjectFlowState>({
    flow: 'idle',
    freelancers: {},
    loading: false,
  })

  const setError = useCallback((error: string) => {
    setState((prev) => ({ ...prev, error }))
  }, [])

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: undefined }))
  }, [])

  const reset = useCallback(() => {
    setState({
      flow: 'idle',
      freelancers: {},
      loading: false,
    })
  }, [])

  const startFlow = useCallback(
    async (title: string, prompt: string) => {
      try {
        clearError()
        setState((prev) => ({ ...prev, flow: 'creating', loading: true }))

        const project = await API.createProject(title, prompt)
        setState((prev) => ({
          ...prev,
          projectId: project.id,
          flow: 'parsing',
        }))

        // Immediately parse the project
        const parsed = await API.parseProject(project.id)
        setState((prev) => ({
          ...prev,
          parsed,
          flow: 'parsed',
          loading: false,
        }))
      } catch (err) {
        const error = err instanceof Error ? err.message : 'Failed to parse prompt'
        setError(error)
        setState((prev) => ({ ...prev, flow: 'idle', loading: false }))
      }
    },
    [clearError, setError]
  )

  const retryParsing = useCallback(async () => {
    if (!state.projectId) return

    try {
      clearError()
      setState((prev) => ({ ...prev, flow: 'parsing', loading: true }))

      const parsed = await API.parseProject(state.projectId)
      setState((prev) => ({
        ...prev,
        parsed,
        flow: 'parsed',
        loading: false,
      }))
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to parse prompt'
      setError(error)
      setState((prev) => ({ ...prev, flow: 'parsed', loading: false }))
    }
  }, [state.projectId, clearError, setError])

  const proceedToMatching = useCallback(async () => {
    if (!state.projectId) return

    try {
      clearError()
      setState((prev) => ({ ...prev, flow: 'matching', loading: true }))

      const matches = await API.createMatches(state.projectId, 20)
      setState((prev) => ({
        ...prev,
        matches,
        flow: 'results',
        loading: false,
      }))
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to generate matches'
      setError(error)
      setState((prev) => ({ ...prev, flow: 'parsed', loading: false }))
    }
  }, [state.projectId, clearError, setError])

  const retryMatching = useCallback(async () => {
    if (!state.projectId) return

    try {
      clearError()
      setState((prev) => ({ ...prev, flow: 'matching', loading: true }))

      const matches = await API.createMatches(state.projectId, 20)
      setState((prev) => ({
        ...prev,
        matches,
        flow: 'results',
        loading: false,
      }))
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to generate matches'
      setError(error)
      setState((prev) => ({ ...prev, flow: 'parsed', loading: false }))
    }
  }, [state.projectId, clearError, setError])

  const fetchFreelancer = useCallback(
    async (id: string): Promise<C.FreelancerProfile | undefined> => {
      // Return cached if available
      if (state.freelancers[id]) {
        return state.freelancers[id]
      }

      try {
        const freelancer = await API.getFreelancer(id)
        setState((prev) => ({
          ...prev,
          freelancers: { ...prev.freelancers, [id]: freelancer },
        }))
        return freelancer
      } catch (err) {
        console.error(`Failed to fetch freelancer ${id}:`, err)
        return undefined
      }
    },
    [state.freelancers]
  )

  return {
    ...state,
    startFlow,
    retryParsing,
    proceedToMatching,
    retryMatching,
    reset,
    clearError,
    fetchFreelancer,
  }
}
