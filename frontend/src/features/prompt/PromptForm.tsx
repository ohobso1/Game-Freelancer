import { useState } from 'react'
import './PromptForm.css'

interface PromptFormProps {
  onSubmit: (title: string, prompt: string) => Promise<void>
  loading: boolean
}

export function PromptForm({ onSubmit, loading }: PromptFormProps) {
  const [title, setTitle] = useState('')
  const [prompt, setPrompt] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !prompt.trim()) return

    try {
      await onSubmit(title, prompt)
      // Reset form on success
      setTitle('')
      setPrompt('')
    } catch {
      // Error already handled by parent
    }
  }

  return (
    <form className="prompt-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="title">Game Title or Project Name</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Space Adventure, Puzzle Quest"
          disabled={loading}
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="prompt">Describe Your Game Idea</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your game concept, genre, gameplay mechanics, art style, multiplayer features, etc. The more details, the better matches we can find!"
          disabled={loading}
          rows={8}
          className="form-textarea"
        />
        <small className="form-hint">
          Provide as much detail as possible about your game vision, team composition needs, and timeline.
        </small>
      </div>

      <button
        type="submit"
        disabled={!title.trim() || !prompt.trim() || loading}
        className="submit-button"
      >
        {loading ? 'Processing...' : 'Analyze & Find Freelancers'}
      </button>
    </form>
  )
}
