# 🧠 AI-Era Code Review Strategy

## Hypothesis

> In the modern world of AI-assisted development, **code generation is fast and easy**. However, **human comprehension of that code is the bottleneck**. To sustain quality and velocity, human review effort must be allocated based on **risk, impact, and clarity** — not volume.

---

## 🚦 Tiered Code Review Framework

We use a **tiered code review system** to manage the high volume of AI-generated code, reduce code-to-merge time, and maintain engineering quality.

| Tier | Description | Who Reviews | Criteria |
|------|-------------|-------------|----------|
| **Tier 0** | 🔄 **Automated Approval** | No humans | - Trivial changes (formatting, comments)<br>- Auto-generated types/docs/tests<br>- CI green light |
| **Tier 1** | 👀 **Light Review** | One engineer | - Scoped, well-tested changes<br>- Minor features or tweaks<br>- Clear AI rationale in PR |
| **Tier 2** | 🔎 **Deep Review** | One or more domain experts | - Business logic<br>- Security, data access<br>- Infra/schema/migrations<br>- Unclear or critical AI-generated code |

---

## 🔧 Review Criteria Rubric

| Attribute | Tier 0 | Tier 1 | Tier 2 |
|-----------|--------|--------|--------|
| **Lines of Code (LOC)** | < 30 | < 200 | > 200 or cross-module |
| **Test Coverage** | Not required | Required | Required + test plan |
| **Impact Surface** | None or internal-only | Minor known modules | External APIs, DB, shared infra |
| **AI Involvement** | Fully deterministic | Includes PR summary | Requires deeper human validation |
| **Rollback Risk** | No impact | Easy to revert | Difficult or high-risk |

---

## 🛠 Tooling & Automation

- ✅ **CI Enforced Checks**: Lint, type safety, tests (Tier 0)
- 🤖 **AI Classification**: PRs must declare if AI-generated
- 📝 **Structured PR Template**: Captures purpose, test strategy, AI rationale
- 🏷 **PR Labeling**: Automatically assigned via GitHub Actions (`tier:0-auto`, `tier:1-quick`, `tier:2-deep`)
- ⏱ **Review SLAs**:
  - Tier 0: Merge on green
  - Tier 1: Review within 12 hours
  - Tier 2: Review within 24–48 hours

---

## 📈 Philosophy

- 🧠 **Code clarity > cleverness**  
- ⚖️ **Comprehension scales with risk, not volume**  
- 💬 **AI should explain itself** — every agentic change must come with intent and rationale  
- 🧪 **Automate what’s predictable, review what’s impactful**  

---

## 📚 Related

- `REVIEW_GUIDELINES.md`: In-depth examples and edge case policies
- `PR_TEMPLATE.md`: Standard format to ensure clarity and tier classification
- `.github/workflows/`: Automation for review flow

---

*This repo reflects our evolving approach to building in the age of autonomous agents. We welcome contributions to improve both the code and the process.*
