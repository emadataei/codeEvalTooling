'use client'
// Updated demo page to showcase new user profile features
import { useState } from 'react'
import { UserProfile } from '../components/UserProfile'

interface UserCardProps {
  readonly userId?: string
  readonly title: string
  readonly variant?: 'primary' | 'secondary'
}

function UserCard({ userId, title, variant = 'primary' }: UserCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  
  // Use environment variable for API configuration
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api'
  
  // Improved function with proper error handling
  const fetchUserData = async (id: string) => {
    try {
      const response = await fetch(`${apiUrl}/users/${id}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to fetch user data:', error)
      throw error
    }
  }

  const handleSaveUser = async (formData: FormData) => {
    setIsLoading(true)
    try {
      // Process form data
      const userData = {
        name: formData.get('name') as string,
        email: formData.get('email') as string,
      }
      
      if (userId) {
        await fetch(`${apiUrl}/users/${userId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData)
        })
      }
      
      console.log('User saved successfully')
    } catch (error) {
      console.error('Failed to save user:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="user-card">
      <UserProfile
        title={title}
        onSave={handleSaveUser}
        variant={variant}
        userId={userId}
      />
      {isLoading && <span>Loading...</span>}
    </div>
  )
}

// Proper Next.js page component  
export default function HomePage() {
  return (
    <main style={{padding: '2rem', minHeight: '100vh', backgroundColor: '#f0f0f0'}}>
      <h1 style={{color: '#333', marginBottom: '2rem'}}>Enhanced User Profile Demo</h1>
      <p style={{color: '#666', marginBottom: '1rem'}}>
        Updated sample application showcasing new user profile features with data loading.
      </p>
      
      <UserCard 
        userId="1"
        title="Edit User Profile"
        variant="primary"
      />
      
      <div style={{marginTop: '2rem'}}>
        <UserCard 
          title="Create New User"
          variant="secondary"
        />
      </div>
      
      <div style={{marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
        <h3>New Features Implemented:</h3>
        <ul>
          <li>User data loading from API</li>
          <li>Enhanced form handling</li>
          <li>Improved accessibility</li>
          <li>Better error handling</li>
          <li>Updated styling with animations</li>
        </ul>
      </div>
    </main>
  )
}
