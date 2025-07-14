# Cognitive Score Calculation for PR Tiers

## Overview

Cognitive score determines the mental effort required to understand and safely approve a code change. This score automatically assigns PR tiers based on complexity, impact, and comprehension difficulty.

## Scoring Components

### 1. Static Code Analysis Score (0-40 points)
- **Cyclomatic Complexity**: McCabe complexity per function
- **Nesting Depth**: Max indentation levels
- **Function Length**: Lines per function
- **Dependency Coupling**: Cross-module dependencies
- **Code Duplication**: Repeated patterns

### 2. Impact Surface Score (0-30 points)
- **File Types**: Database schemas (+10), APIs (+8), configs (+6), tests (+2)
- **Blast Radius**: Number of dependent modules/services
- **External Integrations**: Third-party APIs, payment systems
- **Security Boundaries**: Authentication, authorization changes

### 3. AI Complexity Score (0-30 points)
- **Generation Confidence**: AI model uncertainty scores
- **Pattern Recognition**: How well code matches known patterns
- **Logic Density**: Complex business rules vs simple CRUD
- **Novel Implementations**: New algorithms or approaches

## Tier Assignment

| Cognitive Score | Tier | Auto-Actions |
|----------------|------|--------------|
| **0-25** | Tier 0 | Auto-merge on CI green |
| **26-65** | Tier 1 | Single reviewer, 12h SLA |
| **66-100** | Tier 2 | Domain expert review, 48h SLA |

## 🤖 AI Analysis Pipeline

### Pre-Analysis Checks
```yaml
static_analysis:
  - ESLint/Pylint complexity rules
  - SonarQube cognitive complexity
  - Dependency graph analysis
  - Security scanning (CodeQL, Semgrep)

ai_analysis:
  - Code comprehension difficulty (GPT-4 analysis)
  - Business logic complexity assessment
  - Anti-pattern detection
  - Documentation quality score
```

### Real-time Scoring
1. **Parse PR diff** → Extract changed files and lines
2. **Run static analysis** → Get complexity metrics
3. **AI code review** → Assess comprehension difficulty
4. **Calculate impact** → Analyze affected systems
5. **Generate score** → Weighted sum of all components
6. **Auto-tag PR** → Apply tier labels and assign reviewers

## Example Scoring

```javascript
// Example: Simple utility function
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}
```
**Score: 8** (Tier 0)
- Static: Low complexity (5)
- Impact: Utility function (2)
- AI: Standard pattern (1)

```javascript
// Example: Complex business logic
async function calculateDynamicPricing(user, product, marketConditions) {
  const basePrice = await getProductPrice(product.id);
  const userTier = await getUserPricingTier(user.id);
  const demandMultiplier = calculateDemandMultiplier(marketConditions);
  
  if (user.subscriptionType === 'premium') {
    return applyPremiumDiscount(basePrice * demandMultiplier, userTier);
  }
  
  return applyStandardPricing(basePrice, demandMultiplier, userTier);
}
```
**Score: 72** (Tier 2)
- Static: Multiple async calls, branching (25)
- Impact: Pricing logic affects revenue (22)
- AI: Business-critical algorithm (25)

## Integration Points

- **GitHub Actions**: Auto-scoring on PR creation
- **SonarQube**: Static analysis integration
- **Azure OpenAI / AI Foundry**: Code comprehension analysis
- **PR Templates**: Manual complexity hints from developers
- **Slack/Teams**: Notification routing based on tiers

## Continuous Improvement

- **Feedback Loop**: Track review time vs predicted complexity
- **Model Tuning**: Adjust weights based on actual review outcomes
- **Pattern Learning**: Build corpus of complexity examples
- **Team Calibration**: Regular scoring accuracy reviews
