# PR Analysis Orchestration Guide

## Overview

This document explains how the Quality Gate and Cognitive Scoring systems work together to provide automated PR analysis, tier assignment, and review orchestration. The system uses a two-stage approach: fast quality checks followed by sophisticated cognitive complexity analysis.

## System Architecture

```mermaid
graph TD
    A[PR Created/Updated] --> B[Quality Gate Analysis]
    B --> C{Blocking Issues?}
    C -->|Yes| D[❌ Stop Pipeline<br/>Add Comment<br/>Block PR]
    C -->|No| E[Cognitive Complexity Analysis]
    E --> F[Tier Assignment]
    F --> G[PR Labeling & Reviewer Assignment]
    G --> H[Security Tools Integration]
    H --> I[Complete Analysis]
    
    B --> J[quality-gate-results.json]
    J --> E
    E --> K[cognitive-analysis-results.json]
    K --> F
```

## Two-Stage Analysis Process

### Stage 1: Quality Gate Analysis (Fast Filter)

**Purpose**: Catch fundamental quality issues early and provide immediate feedback

**Script**: `.code-analysis/scripts/run_quality_gate.py`

**What it checks**:
- Security vulnerabilities (hardcoded secrets, SQL injection, unsafe eval)
- Critical code smells (unused imports, debug statements)
- Function complexity without documentation
- Missing error handling for external APIs

**Outputs**:
- `quality-gate-results.json` - Contains penalty scores and issue details
- Exit code 1 if blocking issues found (stops pipeline)
- GitHub PR comments with immediate feedback

### Stage 2: Cognitive Complexity Analysis (Sophisticated Assessment)

**Purpose**: Assess mental effort required to review and understand changes

**Script**: `.code-analysis/scripts/run_cognitive_analysis.py`

**What it analyzes**:
- Static code complexity (control structures, nesting, function length)
- Impact surface (file types, dependencies, external integrations)
- AI-powered comprehension difficulty assessment
- Quality penalty integration from Stage 1

**Outputs**:
- `cognitive-analysis-results.json` - Contains tier assignment and detailed scores
- GitHub Actions outputs for downstream workflow steps

## Integration Flow Details

### 1. Quality Gate Execution

```bash
# GitHub Actions step
- name: Run Quality Gate
  run: python .code-analysis/scripts/run_quality_gate.py
  env:
    CHANGED_FILES: ${{ steps.get-changed-files.outputs.all_changed_files }}
```

**Process**:
1. Reads changed files from environment variable
2. Filters for code files (.py, .js, .ts, etc.)
3. Performs static analysis on each file
4. Categorizes issues by severity (BLOCKING, WARNING, ADVISORY)
5. Calculates quality penalty score
6. Writes results to `quality-gate-results.json`
7. Exits with error code if blocking issues found

**Quality Gate Result Structure**:
```json
{
  "passed": true,
  "quality_score": 85,
  "quality_penalty": 10,
  "blocking_issues": [],
  "warning_issues": [
    {
      "level": "warning",
      "category": "Code Quality", 
      "message": "Debug print statement found",
      "file_path": "src/utils/helper.py",
      "line_number": 42,
      "suggestion": "Remove debug statements before production"
    }
  ],
  "advisory_issues": [...],
  "summary": "Quality gate passed with warnings (Score: 85/100)"
}
```

### 2. Cognitive Analysis Execution

```bash
# GitHub Actions step (runs only if Quality Gate passes)
- name: Run Cognitive Analysis
  run: python .code-analysis/scripts/run_cognitive_analysis.py
  env:
    CHANGED_FILES: ${{ steps.get-changed-files.outputs.all_changed_files }}
```

**Process**:
1. Reads quality penalty from `quality-gate-results.json`
2. Performs multi-dimensional cognitive analysis
3. Applies quality penalty to total score
4. Assigns review tier (0, 1, or 2)
5. Generates human-readable reasoning
6. Outputs results for GitHub Actions

**Cognitive Analysis Result Structure**:
```json
{
  "tier": 1,
  "total_score": 45,
  "static_score": 15,
  "impact_score": 8,
  "ai_score": 12,
  "quality_penalty": 10,
  "reasoning": "Requires human review: Quality penalty applied (+10)"
}
```

## Quality Penalty Integration

### How Quality Issues Affect Cognitive Scoring

The quality gate calculates penalties that are added to the cognitive score:

```python
# Quality penalty calculation in quality_gate.py
penalty = 0
penalty += len(blocking_issues) * 20  # 20 points per blocking issue
penalty += len(warning_issues) * 5   # 5 points per warning issue
penalty = min(penalty, 40)           # Capped at 40 points maximum

# Integration in cognitive analysis
total_score = static_score + impact_score + ai_score + quality_penalty
```

### Real-World Examples

#### Example 1: Clean Code (No Quality Issues)
```python
def format_currency(amount: float, currency_code: str = "USD") -> str:
    """Format a monetary amount with currency symbol."""
    currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = currency_symbols.get(currency_code, currency_code)
    return f"{symbol}{amount:,.2f}"
```

**Quality Gate Result**:
- Blocking: 0, Warning: 0, Advisory: 0
- Quality Penalty: 0

**Cognitive Analysis**:
- Static: 0, Impact: 2, AI: 0, Quality Penalty: 0
- **Total: 2 → Tier 0 (Auto-merge)**

#### Example 2: Code with Quality Issues
```python
def calculate_price(product, user):
    # TODO: Add proper error handling
    print(f"Calculating price for {product}")  # Debug statement
    
    if user.type == "premium":
        discount = 0.2
    else:
        discount = 0.0
        
    final_price = product.price * (1 - discount)
    return final_price
```

**Quality Gate Result**:
- Blocking: 0
- Warning: 2 (debug print, TODO without ticket)
- Quality Penalty: 10 (2 × 5 points)

**Cognitive Analysis**:
- Static: 8, Impact: 5, AI: 7, Quality Penalty: 10
- **Total: 30 → Tier 0 (but close to Tier 1 due to quality issues)**

#### Example 3: Security Vulnerability (Blocking)
```python
def connect_database():
    password = "admin123"  # Hardcoded secret
    return connect(f"mysql://user:{password}@localhost/db")
```

**Quality Gate Result**:
- Blocking: 1 (hardcoded secret)
- **Pipeline STOPS** - No cognitive analysis performed
- PR blocked until security issue resolved

## Tier Assignment Logic

The final tier is determined by the total cognitive score (including quality penalty):

| Total Score | Tier | Review Type | Automation |
|-------------|------|-------------|------------|
| **≤ 35** | **Tier 0** | Auto-merge | Merge on CI green, no human review |
| **36-65** | **Tier 1** | Standard Review | 1-2 reviewers, standard approval |
| **66+** | **Tier 2** | Expert Review | Senior/domain expert required |

### How Quality Issues Impact Tiers

Quality penalties can bump PRs to higher tiers, reflecting the additional cognitive load of reviewing code with quality issues:

```python
# Without quality issues
static=20 + impact=10 + ai=8 + quality=0 = 38 → Tier 1

# With quality issues  
static=20 + impact=10 + ai=8 + quality=15 = 53 → Tier 1 (more firmly)

# Significant quality issues
static=25 + impact=15 + ai=12 + quality=25 = 77 → Tier 2
```

## GitHub Actions Integration

### Workflow Configuration

```yaml
name: PR Analysis Pipeline

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr-analysis:
    runs-on: ubuntu-latest
    steps:
      # ... checkout and setup steps ...
      
      - name: Get Changed Files
        id: get-changed-files
        uses: tj-actions/changed-files@v37
        
      - name: Quality Gate Analysis
        id: quality-gate
        run: python .code-analysis/scripts/run_quality_gate.py
        env:
          CHANGED_FILES: ${{ steps.get-changed-files.outputs.all_changed_files }}
          
      - name: Cognitive Complexity Analysis
        id: cognitive-analysis
        if: steps.quality-gate.outcome == 'success'
        run: python .code-analysis/scripts/run_cognitive_analysis.py
        env:
          CHANGED_FILES: ${{ steps.get-changed-files.outputs.all_changed_files }}
          
      - name: Update PR Metadata
        if: steps.cognitive-analysis.outcome == 'success'
        run: python .code-analysis/scripts/update_pr_metadata.py
        env:
          PR_NUMBER: ${{ github.event.pull_request.number }}
          TIER: ${{ steps.cognitive-analysis.outputs.tier }}
```

### Output Files and Artifacts

The pipeline generates several output files:

1. **`quality-gate-results.json`** - Quality analysis results and penalties
2. **`cognitive-analysis-results.json`** - Cognitive scoring and tier assignment
3. **GitHub Actions outputs** - For downstream workflow consumption
4. **PR comments** - Immediate feedback to developers

## Benefits of Two-Stage Approach

### 1. **Early Feedback**
- Quality issues caught immediately
- Developers get instant feedback on obvious problems
- Reduces wasted CI/CD resources on problematic code

### 2. **Security First**
- Hardcoded secrets and vulnerabilities block pipeline
- No sophisticated analysis wasted on insecure code
- Security issues prioritized over complexity concerns

### 3. **Accurate Cognitive Assessment**
- Quality issues increase review difficulty
- Penalty system reflects real cognitive load
- Cleaner code gets appropriate (lower) tier assignment

### 4. **Resource Efficiency**
- Fast quality checks filter out obvious issues
- Expensive AI analysis only runs on quality-passing code
- Pipeline optimization through early termination

### 5. **Comprehensive Coverage**
- Quality Gate: Basic hygiene and security
- Cognitive Analysis: Sophistication and complexity
- Combined: Holistic assessment of review requirements

## Configuration and Customization

### Quality Gate Thresholds

Modify `.code-analysis/scoring/quality_gate.py` to adjust:
- Security pattern detection
- Code smell sensitivity
- Penalty point values
- Issue categorization rules

### Cognitive Scoring Weights

Modify `.code-analysis/scoring/cognitive_analyzer.py` constants:
- `TIER_0_THRESHOLD = 35` (auto-merge cutoff)
- `TIER_1_THRESHOLD = 65` (expert review cutoff)
- Individual scoring component weights

### Integration Points

The system integrates with:
- **SonarQube**: Additional code quality metrics
- **CodeQL/Semgrep**: Security vulnerability scanning  
- **GitHub**: PR comments, labels, reviewer assignment
- **Azure AI Foundry**: Advanced complexity assessment
- **Team workflows**: Notification routing, SLA tracking

## Monitoring and Continuous Improvement

### Feedback Loop

Track the effectiveness of the orchestration:
- **Quality Gate accuracy**: Are blocked PRs actually problematic?
- **Tier assignment precision**: Do assigned tiers match actual review complexity?
- **False positive rates**: Are legitimate changes incorrectly flagged?
- **Developer satisfaction**: Is feedback helpful and actionable?

### Tuning Recommendations

Regularly review and adjust:
1. **Quality penalty weights** based on team feedback
2. **Cognitive score thresholds** based on review time data
3. **Pattern detection rules** as codebase evolves
4. **Integration timing** to optimize CI/CD performance

This orchestrated approach ensures that code quality, security, and complexity are all considered in determining the appropriate level of review required for each pull request.
