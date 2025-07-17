# AI-Era Code Review System

> **Transform your code review process for the age of AI-generated code**

## The Problem

In the AI era, code generation is no longer the bottleneck — human comprehension is.
To sustain velocity and quality at scale, we must minimize unnecessary human review effort by aligning review depth with code risk, clarity, and impact.
A tiered review model, combined with AI-assisted code analysis and structured tagging, enables us to triage changes efficiently, focus human review only where it matters most, and reduce the code-to-approval cycle time without compromising software integrity.

## The Solution

An intelligent, tiered review system that:
- **Automatically analyzes** code complexity and risk
- **Routes changes** to appropriate reviewers based on difficulty
- **Eliminates review bottlenecks** for simple changes
- **Ensures expert attention** for complex, critical code

## Key Features

### Cognitive Complexity Analysis
- Multi-dimensional scoring (static analysis + AI assessment)
- Risk-based tier assignment (0-2)
- Quality gate with blocking issue detection

### Automatic Team Assignment
- Smart routing based on code complexity
- Configurable team assignments
- Escalation for security/critical changes

### Velocity Improvements
- **Tier 0**: Auto-merge for simple changes
- **Tier 1**: Single reviewer for standard changes
- **Tier 2**: Expert review for complex changes

### Rich Feedback
- Detailed PR comments with complexity breakdown
- Actionable quality improvement suggestions
- Clear review process guidance

## Quick Start

1. **Set up AI provider** (Azure AI Foundry or OpenAI)
4. **Enable workflows** - they run automatically on PRs

See [Setup Guide](docs/SETUP_GUIDE.md) for detailed instructions.

## 📖 Documentation

- **[Cognitive Review System](docs/COGNITIVE_REVIEW_SYSTEM.md)** - Complete system overview with hypothesis and benefits
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Quick implementation instructions
- **[AI Provider Setup](docs/ai_provider_setup.md)** - Detailed AI configuration

## Results

### Velocity
- **60-80% reduction** in review time for simple changes
- **Clear SLAs** for each complexity tier
- **Parallel processing** for complex changes

### Quality
- **Automated quality gates** catch issues before human review
- **Expert involvement** for high-risk changes
- **Consistent standards** across all contributions

### Developer Experience
- **Predictable process** with clear expectations
- **Reduced frustration** from waiting on trivial changes
- **Focused attention** on work that matters

---