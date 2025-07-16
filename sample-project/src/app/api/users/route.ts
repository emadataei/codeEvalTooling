// API route with security and quality issues for testing
import { NextRequest, NextResponse } from 'next/server'

// Missing proper validation - should trigger warnings
export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const userId = searchParams.get('id')
  
  // SQL injection vulnerability - should trigger blocking issue
  const query = `SELECT * FROM users WHERE id = '${userId}'`
  
  try {
    // Simulated database query (this would be vulnerable in real code)
    const user = await executeQuery(query)
    
    // Missing error handling for specific cases
    return NextResponse.json({ user })
  } catch (error) {
    // Generic error handling - should suggest improvement
    return NextResponse.json({ error: 'Something went wrong' })
  }
}

// Missing proper types and validation
export async function POST(request) {
  const body = await request.json()
  
  // No input validation - should trigger security warning
  const newUser = {
    name: body.name,
    email: body.email,
    password: body.password // Storing plain text password - security issue
  }
  
  // Hardcoded database connection - should be flagged
  const dbUrl = "postgresql://user:password123@localhost:5432/mydb"
  
  console.log('Creating user with DB:', dbUrl) // Debug log in production
  
  return NextResponse.json({ message: 'User created', user: newUser })
}

// Simulate database function (would normally be imported)
async function executeQuery(query) {
  // This is just a placeholder for testing
  return { id: 1, name: 'Test User', email: 'test@example.com' }
}
