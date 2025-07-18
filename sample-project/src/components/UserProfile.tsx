// This component follows the Copilot instructions correctly
import { useState } from 'react'

interface UserProfileProps {
  readonly title: string
  readonly onSave: (data: FormData) => void
  readonly variant?: 'primary' | 'secondary'
}

/**
 * UserProfile component for displaying and editing user information
 * @param title - The title to display
 * @param onSave - Callback function when saving user data
 * @param variant - Visual style variant
 * @returns JSX element for user profile
 */
export function UserProfile({ title, onSave, variant = 'primary' }: UserProfileProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData(event.currentTarget)
      await onSave(formData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`user-profile user-profile--${variant}`} role="main">
      <h2>{title}</h2>
      <form onSubmit={handleSubmit} aria-label="User profile form">
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input 
            id="name"
            name="name"
            type="text"
            required
            aria-describedby="name-help"
          />
          <div id="name-help" className="help-text">
            Enter your full name
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input 
            id="email"
            name="email"
            type="email"
            required
            aria-describedby="email-help"
          />
          <div id="email-help" className="help-text">
            Enter a valid email address
          </div>
        </div>

        {error && (
          <div className="error-message" role="alert" aria-live="polite">
            {error}
          </div>
        )}

        <button 
          type="submit" 
          disabled={isLoading}
          aria-label={isLoading ? 'Saving...' : 'Save profile'}
        >
          {isLoading ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}
