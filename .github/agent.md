# Agent Memory & Instructions

This file serves as persistent memory and instructions for AI agents working on this codebase. It learns and evolves based on our collaboration patterns and project-specific requirements.

## Project Context

**Repository**: codeEvalTooling  
**Owner**: emadataei  
**Primary Purpose**: PR analysis, visualization, and documentation automation  
**Current Branch**: feature/ui-backend-improvements  

### Technology Stack
- **Languages**: TypeScript, JavaScript, Python
- **Frameworks**: Next.js, React
- **CI/CD**: GitHub Actions
- **Analysis Tools**: ESLint, SonarQube, custom analysis scripts

## Established Patterns & Preferences

### Code Style & Standards
- **No emojis** in markdown files or code comments (per copilot-instructions.md)
- Follow TypeScript-first approach with proper typing
- Use semantic HTML and accessibility attributes
- Implement comprehensive error handling
- Prefer `const` over `let`, use early returns

### PR Review System
- **Reviewer-centric labeling** (not code category tags)
- **Single workflow** sets PR labels (code-quality-analysis.yml)
- **Labels focus on**: tier, complexity, score, size, merge readiness
- **Documentation**: Keep user-focused, not technical implementation details

### File Organization
```
.code-analysis/
├── scripts/          # Analysis and automation scripts
├── outputs/          # Generated reports and artifacts
docs/                 # User-facing documentation
.github/
├── workflows/        # CI/CD workflows
├── scripts/          # GitHub-specific automation
└── agent.md         # This file
```

### Workflow Patterns
- **PR comments replace** existing ones (don't create duplicates)
- **Fail fast** on errors in CI workflows
- **Base64 embedded images** in PR comments for reliability
- **Comprehensive artifact upload** for debugging

## Agent Learning History

### Session Insights
- User prefers practical, actionable documentation over technical implementation details
- Focus on reviewer experience and team efficiency
- Avoid redundant workflows - centralize similar functionality
- Documentation should answer "what do I do?" not "how does it work?"
- **CRITICAL**: The `auto-label-pr.js` file was accidentally emptied, losing all reviewer-centric labeling logic (restored 2025-07-25)

### Common Tasks
1. **PR Analysis Enhancement** - Improving visualization and documentation generation
2. **Workflow Optimization** - Streamlining CI/CD processes
3. **Documentation Refinement** - Making guides more user-friendly
4. **Error Handling** - Implementing robust error management

### Successful Patterns
- Incremental improvements with validation at each step
- User feedback integration and immediate adjustments
- Centralized configuration and logic where possible
- Clear separation of concerns between workflows

## Project-Specific Instructions

### When Working on PR Analysis
- Always check existing scripts before creating new ones
- Ensure error handling covers edge cases (missing files, network issues)
- Validate output size for GitHub comment limits
- Test with both small and large PRs

### When Modifying Workflows
- Only `code-quality-analysis.yml` should set PR labels
- Always include artifact upload for debugging
- Use consistent environment variable patterns
- Include status checks and validation steps

### When Creating Documentation
- Start with user needs, not technical details
- Use tables and quick references for complex information
- Include decision trees for complex processes
- Link related documents appropriately

## Current Focus Areas

### Active Features
- **PR Labeling System**: Reviewer-centric automated labels
- **Visual Analysis**: Dependency graphs, heatmaps, story arcs
- **Documentation Generation**: Smart suggestions and comprehensive reports

### Known Issues to Watch
- GitHub comment size limits with embedded images
- Multiple workflows potentially conflicting
- Documentation becoming too technical

### Improvement Opportunities
- Enhanced error recovery in analysis scripts
- Better integration between different analysis tools
- More sophisticated quality scoring algorithms

## Communication Patterns

### What Works Well
- Direct feedback on specific issues
- Iterative refinement with testing
- Clear requirements with context
- Focus on end-user experience

### User Preferences
- Practical over theoretical explanations
- Quick implementation over extensive planning
- User-centered design for all interfaces
- Minimal repetition of established patterns

## Agent Behavior Guidelines

### Do
- Reference this file for context and patterns
- Update this file with new learnings and patterns
- Follow established code and documentation standards
- Focus on reviewer and user experience
- Implement robust error handling

### Don't
- Add emojis to markdown or code
- Create duplicate functionality across workflows
- Make documentation overly technical
- Assume user context without checking this file
- Ignore established patterns without discussion

---

*This file is maintained by AI agents and updated based on collaboration patterns and project evolution.*

**Last Updated**: 2025-07-25  
**Version**: 1.0  
**Next Review**: When significant new patterns emerge
