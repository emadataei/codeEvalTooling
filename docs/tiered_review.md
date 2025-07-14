# AI Code Review Workflow

This repository supports a modern, AI-assisted code development workflow. To ensure **code quality** and **review velocity**, we follow a **Tiered Code Review System**.

---

## 🚦 Tiered Code Review System

| Tier | Description | Review Method |
|------|-------------|----------------|
| **Tier 0** | Automated checks on AI-generated code | ✅ Linting, formatting, type-checking, unit tests, security scans |
| **Tier 1** | Simple, isolated changes (e.g., docs, config tweaks, scoped functions) | ✅ Auto-approve or fast-track with minimal review |
| **Tier 2** | Complex, architectural, or business logic changes | ✅ Full manual review, discussion, and validation |

---

## ✅ Automated Review Checks (Tier 0)

Every PR must pass the following automated gates:

- ✅ Code format (Prettier, Black, etc.)
- ✅ Linting & static analysis (ESLint, PyLint, SonarQube)
- ✅ Type safety (TypeScript, MyPy, etc.)
- ✅ Unit test coverage & success
- ✅ Security scanning (Bandit, Trivy, etc.)

---

## 🤖 AI Guidelines for PRs

All AI-generated code **must** include:

- 📄 A description of what was implemented and why
- 🔍 Edge cases considered
- 🧪 Tests created or assumptions made

*Example prompt:*
> "Generate a PR-ready code block with a one-line summary, implementation breakdown, and test description."

---

## 🔍 Human Review Guidelines

Focus human attention on:

- ⚠️ Business-critical logic
- 🔐 Security and infrastructure changes
- 🔄 External dependencies or API contracts
- 🤝 Cross-team integrations

---

## 🧠 AI Review Assistants (Optional)

We support AI reviewer agents that:

- Summarize diffs by behavior, not just lines
- Suggest improvements based on prior codebase patterns
- Flag missing tests or anti-patterns

You’ll see these comments automatically when submitting a PR.

---

## 🚀 Review Acceleration Tips

- ✅ Keep PRs small and focused
- ✅ Use clear commit messages and PR descriptions
- ✅ Tag reviewers by ownership and risk area
- ✅ Let automation handle the easy stuff—focus humans on the hard parts

---

## 📈 Metrics We Track

To continuously improve, we track:

- ⏱️ Code-to-PR-to-merge time
- 📉 Auto-reject rate from Tier 0
- ✅ PRs approved without human touch
- 🧪 Test coverage & AI hallucination incidents

---

## 📬 Feedback

Spotted an issue or want to improve the workflow? Please open a PR or reach out to the #ai-dev-workflow Slack channel.

---
