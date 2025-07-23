// This component follows the Copilot instructions correctly
import { useState, useEffect } from 'react'

interface UserProfileProps {
  readonly title: string
  readonly onSave: (data: FormData) => void
  readonly variant?: 'primary' | 'secondary'
  readonly userId?: string
}

/**
 * UserProfile component for displaying and editing user information
 * @param title - The title to display
 * @param onSave - Callback function when saving user data
 * @param variant - Visual style variant
 * @param userId - Optional user ID for loading existing data
 * @returns JSX element for user profile
 */
export function UserProfile({ title, onSave, variant = 'primary', userId }: UserProfileProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userData, setUserData] = useState<{name: string; email: string} | null>(null)

  // Load user data if userId is provided
  useEffect(() => {
    if (userId) {
      const loadUserData = async () => {
        try {
          // Simulate API call
          const response = await fetch(`/api/users/${userId}`)
          const data = await response.json()
          setUserData(data)
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to load user data'
          setError(errorMessage)
        }
      }
      loadUserData()
    }
  }, [userId])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData(event.currentTarget)
      await Promise.resolve(onSave(formData))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className={`user-profile user-profile--${variant}`}>
      <h2>{title}</h2>
      <form onSubmit={handleSubmit} aria-label="User profile form">
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input 
            id="name"
            name="name"
            type="text"
            required
            defaultValue={userData?.name || ''}
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
            defaultValue={userData?.email || ''}
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
    </main>
  )
}
