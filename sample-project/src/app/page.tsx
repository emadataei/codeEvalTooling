// This file has intentional quality issues for testing
// TODO: Added test comment to trigger change detection 
// Additional comment to test quality gate comment updates
// Debug: Testing both quality gate AND cognitive analysis PR comments (debug-5)
import { useState } from 'react'

// Missing interface definition - should trigger type safety warning
function UserCard(props) {
  const [isLoading, setIsLoading] = useState(false)
  
  // Hardcoded API key - should trigger security blocking issue
  const API_KEY = "sk-1234567890abcdef-secret-key-hardcoded"
  
  // Function without proper error handling
  const fetchUserData = async (userId) => {
    const response = await fetch(`/api/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    })
    const data = await response.json()
    return data
  }
  
  // Debug statement that should be flagged
  console.log('UserCard props:', props)
  
  // Complex function that should trigger complexity warning
  const processUserPermissions = (user, permissions, roles, groups, settings) => {
    let result = {}
    if (user && user.id) {
      if (permissions && permissions.length > 0) {
        for (let i = 0; i < permissions.length; i++) {
          if (permissions[i].active) {
            if (roles && roles.includes(permissions[i].role)) {
              if (groups && groups.some(g => g.id === permissions[i].groupId)) {
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

export default UserCard
