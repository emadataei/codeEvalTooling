# Sample Next.js Project

This is a sample Next.js + TypeScript project designed to test the code quality gate system.

## Purpose

This project contains intentional code quality issues to demonstrate:

- **Security Issues**: Hardcoded secrets, SQL injection vulnerabilities
- **Type Safety Issues**: Missing TypeScript annotations, `any` types
- **Code Quality Issues**: Complex functions, missing error handling
- **Best Practice Violations**: Debug logs, unused imports
- **Good Examples**: Components that follow Copilot instructions

## Files Overview

- `src/app/page.tsx` - Contains multiple quality issues for testing
- `src/app/api/users/route.ts` - API route with security vulnerabilities
- `src/components/UserProfile.tsx` - Example of good code following standards
- `src/app/layout.tsx` - Basic layout with some TypeScript issues

## Testing the Quality Gate

This project is designed to trigger various levels of quality gate responses:

1. **Blocking Issues**: Security vulnerabilities that prevent merge
2. **Warning Issues**: Quality improvements that should be addressed
3. **Advisory Issues**: Suggestions for better code

The quality gate should detect and report these issues with actionable suggestions based on the project's Copilot instructions.
