'use client'
// This file has intentional quality issues for testing
// TODO: Added test comment to trigger change detection 
// Additional comment to test quality gate comment updates
// Debug: Fixed label conflicts - only update_pr_metadata.py sets labels (debug-9)
import { useState } from 'react'

// Missing interface definition - should trigger type safety warning
function UserCard(props: any) {
  const [isLoading, setIsLoading] = useState(false)
  
  // Hardcoded API key - should trigger security blocking issue
  const API_KEY = "sk-1234567890abcdef-secret-key-hardcoded"
  
  // Function without proper error handling
  const fetchUserData = async (userId: any) => {
    const response = await fetch(`/api/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    })
    const data = await response.json()
    return data
  }
  
  // Debug statement that should be flagged
  console.log('UserCard props:', props)
  
  // Complex function that should trigger complexity warning
  const processUserPermissions = (user: any, permissions: any, roles: any, groups: any, settings: any) => {
    let result: any = {}
    if (user && user.id) {
      if (permissions && permissions.length > 0) {
        for (let i = 0; i < permissions.length; i++) {
          if (permissions[i].active) {
            if (roles && roles.includes(permissions[i].role)) {
              if (groups && groups.some((g: any) => g.id === permissions[i].groupId)) {
                if (settings && settings.allowPermissionOverride) {
                  result[permissions[i].name] = true
                } else {
                  result[permissions[i].name] = permissions[i].defaultValue
                }
              }
            }
          }
        }
      }
    }
    return result
  }
  
  return (
    <div className="user-card">
      <h2>{props.name}</h2>
      <p>{props.email}</p>
      {isLoading && <span>Loading...</span>}
    </div>
  )
}

// Proper Next.js page component
export default function HomePage() {
  return (
    <main style={{padding: '2rem', minHeight: '100vh', backgroundColor: '#f0f0f0'}}>
      <h1 style={{color: '#333', marginBottom: '2rem'}}>Code Evaluation Demo</h1>
      <p style={{color: '#666', marginBottom: '1rem'}}>This is a sample Next.js application for testing UI changes.</p>
      <UserCard 
        name="John Doe" 
        email="john.doe@example.com" 
      />
      <div style={{marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px'}}>
        <h3>Features to test:</h3>
        <ul>
          <li>Visual diff detection</li>
          <li>Component changes</li>
          <li>Style modifications</li>
          <li>Layout updates</li>
        </ul>
      </div>
    </main>
  )
}
