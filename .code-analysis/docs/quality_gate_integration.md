# Quality Gate Integration Guide

## Overview

The Quality Gate is a **prerequisite step** that runs before cognitive scoring in the CI/CD pipeline. It ensures fundamental code quality standards are met before consuming resources on more expensive analyses. **Now enhanced with AI-powered analysis capabilities.**

## Integration Flow

```
PR Created/Updated
       ↓
   Quality Gate Analysis ← RUNS FIRST (Static + AI Analysis)
       ↓
   BLOCKING Issues? → STOP (PR blocked, add comment)
       ↓ No blocking issues
   Cognitive Complexity Analysis ← Uses quality penalty
       ↓
   Tier Assignment (0, 1, 2)
       ↓
   Security Tools (SonarQube, CodeQL, etc.)
```

## Analysis Types

### **Static Analysis** (Always Enabled)
- Pattern-based security vulnerability detection
- Code smell identification using regex patterns
- Function complexity analysis
- Documentation quality checks

### **AI-Powered Analysis** (Optional, Enhanced)
- **Business logic flaw detection**
- **Complex security vulnerabilities** that patterns might miss
- **Architecture and maintainability concerns**
- **Context-dependent anti-pattern recognition**
- **Performance issue identification**
- **Advanced code quality assessment**

## Quality Gate Categories

### **BLOCKING Issues** (Stops Pipeline)
- **Security vulnerabilities** (hardcoded secrets, SQL injection, unsafe eval)
- **Critical code smells** (unused imports, unreachable code)
- **Missing error handling** for external APIs
- **AI-detected critical flaws** (business logic errors, severe security issues)

### **WARNING Issues** (Quality Penalty)
- **Complex functions** without documentation
- **Debug statements** (print, console.log)
- **TODO/FIXME** without ticket references
- **AI-detected quality concerns** (maintainability issues, minor security concerns)

### **ADVISORY Issues** (Suggestions Only)
- **Missing type hints/annotations**
- **Code duplication** opportunities
- **Performance optimizations**
- **AI-suggested improvements** (best practices, code clarity)

## Integration with Cognitive Scoring

### Quality Penalty System
```python
# Quality penalties are added to cognitive score
cognitive_score = static_score + impact_score + ai_score + quality_penalty

# This can bump a PR to a higher tier
if cognitive_score <= 25: tier = 0  # Auto-merge
elif cognitive_score <= 65: tier = 1  # Light review  
else: tier = 2  # Deep review
```

### Example Scenarios

#### Scenario 1: Poor Quality Code
```
Quality Gate Result: FAILED (45/100)
- 1 blocking issue (hardcoded secret)
- 3 warning issues (debug prints, TODO comments)
→ Pipeline STOPS, PR blocked until fixed
```

#### Scenario 2: Low Quality but No Blockers
```
Quality Gate Result: PASSED (70/100) 
- 0 blocking issues
- 4 warning issues (missing docs, debug statements)
- Quality penalty: +10 points
→ Cognitive scoring proceeds with penalty
→ Likely bumped from Tier 1 to Tier 2
```

#### Scenario 3: High Quality Code
```
Quality Gate Result: PASSED (98/100)
- 0 blocking issues  
- 0 warning issues
- Quality penalty: +0 points
→ Cognitive scoring with no penalty
→ Natural tier assignment
```

## GitHub Actions Integration

### Workflow Dependencies
```yaml
jobs:
  quality-gate:
    # Runs first, analyzes all changed files
    
  cognitive-scoring:
    needs: quality-gate
    if: needs.quality-gate.outputs.quality-passed == 'true'
    # Only runs if quality gate passes
    
  sonarqube:
    needs: quality-gate
    if: needs.quality-gate.outputs.blocking-issues == '0'
    # Runs even with warnings, but not with blockers
```

### PR Comments
The integration automatically adds comments to PRs:

```markdown
## Quality Gate FAILED

**Score:** 45/100
**Summary:** Quality gate FAILED (Score: 45/100) - 1 blocking issue must be fixed

### BLOCKING Issues (Must Fix)

- **Security**: Potential hardcoded secret detected
  - Location: `src/bad_module.py:7`
  - Suggestion: Use environment variables or secure vault for secrets

**Cognitive Analysis Blocked** - Fix blocking issues before proceeding.
```

## Benefits

### 1. **Early Feedback**
- Developers get immediate feedback on basic quality issues
- No need to wait for expensive security scans to find obvious problems

### 2. **Resource Optimization**
- Expensive AI analysis only runs on quality code
- Security tools don't waste time on code that won't merge anyway

### 3. **Tiered Penalties**
- Quality issues appropriately increase review requirements
- Poor quality code automatically gets more scrutiny

### 4. **Educational**
- Clear explanations help developers learn best practices
- Actionable suggestions for improvement

## Configuration

### Customizing Quality Standards

Edit `.code-analysis/scoring/quality_gate.py` to adjust:

```python
# Security patterns
self.security_patterns = {
    'hardcoded_secrets': [...],  # Add more patterns
    'sql_injection': [...],
    'unsafe_eval': [...]
}

# File impact weights  
self.file_impact_weights = {
    'migration': 10,  # Database migrations
    'schema': 10,     # Schema changes
    'api': 8,         # API endpoints
    'security': 8,    # Security code
    'payment': 9,     # Payment logic
    'test': 2,        # Test files
    'doc': 1          # Documentation
}
```

### AI Configuration

The quality gate can be enhanced with AI analysis. Configure these environment variables:

```bash
# AI Configuration (same as cognitive analysis)
AI_FOUNDRY_ENDPOINT=https://your-ai-foundry.com
AI_FOUNDRY_TOKEN=your-token
AI_FOUNDRY_MODEL=gpt-4o

# Quality Gate AI Settings
QUALITY_GATE_AI_ENABLED=true  # Set to 'false' to disable AI analysis
```

### GitHub Actions Configuration

```yaml
- name: Run Quality Gate with AI
  run: python .code-analysis/scripts/run_quality_gate.py
  env:
    CHANGED_FILES: ${{ steps.get-changed-files.outputs.all_changed_files }}
    AI_FOUNDRY_ENDPOINT: ${{ secrets.AI_FOUNDRY_ENDPOINT }}
    AI_FOUNDRY_TOKEN: ${{ secrets.AI_FOUNDRY_TOKEN }}
    AI_FOUNDRY_MODEL: ${{ secrets.AI_FOUNDRY_MODEL }}
    QUALITY_GATE_AI_ENABLED: 'true'
```

### Performance Considerations

**AI Analysis Impact:**
- **Execution time**: Adds 2-5 seconds per PR (depending on code size)
- **API costs**: Approximately $0.01-0.05 per PR analysis
- **Accuracy**: Significantly improves detection of complex issues

**When to use AI Analysis:**
- ✅ **Production code** - Critical systems, business logic
- ✅ **Security-sensitive** changes - Authentication, authorization, payments
- ✅ **Complex PRs** - Large changes, multiple files, algorithmic code
- ❌ **Documentation** changes - Minimal code impact
- ❌ **Simple fixes** - Typos, formatting, minor updates

### Environment Variables

For cognitive analysis (optional):
```bash
AI_FOUNDRY_ENDPOINT=https://your-ai-foundry.com
AI_FOUNDRY_TOKEN=your-token
AI_FOUNDRY_MODEL=gpt-4o
```

## How AI Analysis Works

### Passing Changes to AI

The quality gate prepares all PR changes for AI analysis in a structured format:

```python
def _prepare_code_for_ai(self, pr_files: List[Dict]) -> str:
    """Prepare code changes for AI analysis with context."""
    changes = []
    
    for file_info in pr_files:
        file_path = file_info['path']
        content = file_info['content']
        language = file_info.get('language', 'unknown')
        
        # Add file header with context
        file_section = f"""
--- File: {file_path} (Language: {language}) ---
{content}
"""
        changes.append(file_section)
    
    return "\n".join(changes)
```

### AI Analysis Example

**Input to AI** (multiple files from a PR):
```
--- File: src/payment/processor.py (Language: python) ---
def process_payment(amount, user_id, card_token):
    # Process payment without validation
    result = stripe.charge(amount, card_token)
    return result

--- File: src/api/payment.py (Language: python) ---
@app.route('/payment', methods=['POST'])
def create_payment():
    data = request.json
    result = process_payment(data['amount'], data['user'], data['card'])
    return jsonify(result)
```

**AI Response** (identifies context-dependent issues):
```json
{
  "issues": [
    {
      "severity": "blocking",
      "category": "Security",
      "message": "Payment processing lacks input validation and error handling",
      "file_path": "src/payment/processor.py",
      "line_number": 2,
      "suggestion": "Add amount validation, user verification, and proper error handling"
    },
    {
      "severity": "warning", 
      "category": "Security",
      "message": "API endpoint exposes payment processing without authentication",
      "file_path": "src/api/payment.py",
      "line_number": 3,
      "suggestion": "Add authentication middleware and input sanitization"
    }
  ]
}
```

### Benefits of AI Analysis

**Static Analysis Misses:**
- Business logic flaws (like the payment example above)
- Cross-file security implications
- Context-dependent issues
- Domain-specific anti-patterns

**AI Catches:**
- **Inter-file relationships** - How changes affect multiple components
- **Business logic errors** - Flawed algorithms or workflows  
- **Security vulnerabilities** - Complex attack vectors
- **Maintainability issues** - Architecture problems, tech debt

## Usage in CI/CD

The quality gate automatically runs in GitHub Actions as part of the CI/CD pipeline:

1. **Quality Gate Job**: Runs first and analyzes all changed files
2. **Blocking Issues**: Stop the pipeline and prevent merging
3. **Warning Issues**: Add penalties to cognitive scoring
4. **Clean Code**: Proceeds to cognitive analysis with no penalties

## Metrics and Monitoring

The quality gate generates metrics tracked in your existing performance monitoring:

```json
{
  "tool": "QualityGate",
  "timestamp": "2025-07-14T...",
  "duration_seconds": 2,
  "status": "passed",
  "quality_score": 85,
  "blocking_issues": 0,
  "warning_issues": 2,
  "quality_penalty": 5
}
```

These metrics help you:
- Track quality trends over time
- Identify teams/repositories that need quality training
- Optimize quality gate rules based on real data

## Best Practices

### For Developers
1. **Run quality checks locally** before pushing
2. **Address blocking issues immediately** - they stop the pipeline
3. **Use the suggestions** to improve code quality over time
4. **Follow secure coding practices** to avoid security issues

### For Teams
1. **Review quality gate rules** regularly
2. **Add domain-specific patterns** for your codebase
3. **Train developers** on quality standards
4. **Monitor quality trends** in your metrics

### For Platform Teams
1. **Keep quality gate fast** (< 30 seconds)
2. **Provide clear error messages** with actionable suggestions
3. **Balance strictness** vs developer velocity
4. **Integrate with your existing tools** (SonarQube, etc.)
