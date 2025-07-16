# Cognitive Complexity Analyzer - Scoring System Documentation

## Overview

The cognitive analyzer evaluates Pull Requests using a multi-dimensional scoring system to determine the appropriate review tier and automation level. The total score combines three main components plus optional quality penalties to assess the mental effort required to safely review and approve code changes.

## Scoring Components

### 1. Static Score (0-40 points)
Measures code complexity through static analysis using language-specific analysis techniques.

**Analysis Methods:**
- **Python**: AST-based analysis with nesting calculations
- **JavaScript/TypeScript**: Pattern matching for control structures and async patterns
- **Generic Languages**: Control structure counting and bracket analysis

**Scoring Breakdown:**
- Control structures (if/for/while/with): **+1 point each**
- Nesting depth: **+1 point per level beyond first**
- Function length penalties:
  - Functions > 50 lines: **+3 points**
  - Functions > 20 lines: **+1 point**
- File size penalties (generic analysis):
  - Files > 100 lines: **+5 points**
  - Files > 50 lines: **+2 points**

### 2. Impact Score (0-30 points)
Measures blast radius and change impact based on file types, dependencies, and external integrations.

**File Type Weights:**
- Migration files: **+10 points**
- Schema changes: **+10 points**
- Payment systems: **+9 points**
- API changes: **+8 points**
- Security files: **+8 points**
- Config files: **+6 points**
- Test files: **+2 points**
- Documentation: **+1 point**

**Dependencies:**
- Import statements: **+1 point per 5 imports** (max +5)

**External Integrations:**
- Database/API keywords: **+3 points**
- Detected keywords: `database`, `db.`, `api.`, `fetch(`, `axios`

### 3. AI Score (0-30 points)
AI-powered assessment of cognitive load and comprehension difficulty.

**AI Analysis (when available):**
- Uses Azure AI Foundry to evaluate comprehension difficulty
- Assesses business rule complexity
- Detects unusual patterns or anti-patterns
- Evaluates required domain knowledge

**Heuristic Fallback Scoring:**
- **Complex patterns (+5 points each):**
  - `algorithm`, `recursive`, `optimization`, `performance`
  - `threading`, `async`, `promise`, `callback`

- **Business logic (+3 points each):**
  - `pricing`, `payment`, `billing`, `discount`, `tax`
  - `inventory`, `order`, `subscription`

- **Data structures (+2 points each):**
  - `nested`, `recursive`, `tree`, `graph`, `matrix`

### 4. Quality Penalty (0-50+ points)
Additional penalties applied for code quality issues, security vulnerabilities, performance regressions, and test coverage drops.

**Quality Gate Analysis:**
- **Static Analysis**: Pattern-based security checks, code smell detection
- **AI-Powered Analysis** (when enabled): Advanced quality review using Azure AI Foundry
  - Business logic flaw detection
  - Complex security vulnerability identification
  - Architecture and maintainability concerns
  - Context-dependent anti-pattern recognition

**Quality Gate AI Capabilities:**
- Reviews entire PR context, not just individual files
- Identifies issues that static analysis might miss
- Provides detailed suggestions for improvement
- Categorizes issues by severity (blocking, warning, advisory)
- Considers business logic and domain-specific concerns

## Total Score Calculation

```
TOTAL SCORE = Static Score + Impact Score + AI Score + Quality Penalty
Range: 0-150+ points
```

## Tier Assignment

| Total Score | Tier | Review Type | Description |
|-------------|------|-------------|-------------|
| **≤ 35** | **Tier 0** | Auto-merge | Automated merge on CI success, no human review required |
| **36-65** | **Tier 1** | Standard Review | Standard peer review required, 1-2 reviewers needed |
| **66+** | **Tier 2** | Expert Review | Senior/expert review required, domain expertise needed |

## Language-Specific Analysis

### Python Analysis
- **AST parsing** for accurate complexity measurement
- **Control structure counting** (if/for/while/with statements)
- **Nesting depth calculation** through AST traversal
- **Function length penalties** based on line count
- **Fallback** to generic analysis if AST parsing fails

### JavaScript/TypeScript Analysis
- **Control structures:** +1 each (if/for/while/switch/try/catch)
- **Functions:** +1 each (function declarations and arrow functions)
- **Async patterns:** +1 each (.then/.catch/callback calls)

### Generic Language Analysis
- **Control structures:** Case-insensitive pattern matching
- **Structural complexity:** Bracket counting for nesting estimation
- **File size penalties:** Based on line count thresholds

## Scoring Examples

### Simple Utility Function
```python
def format_currency(amount: float, currency_code: str = "USD") -> str:
    currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = currency_symbols.get(currency_code, currency_code)
    return f"{symbol}{amount:,.2f}"
```
**Scoring:**
- Static: **0** (no control structures, simple logic)
- Impact: **2** (utility file)
- AI: **0** (simple formatting)
- **Total: 2 → Tier 0 (Auto-merge)**

### Standard Feature Implementation
```python
def validate_user_input(data: dict) -> dict:
    errors = []
    if not data.get('email'):
        errors.append("Email required")
    if len(data.get('password', '')) < 8:
        errors.append("Password too short")
    return {"valid": len(errors) == 0, "errors": errors}
```
**Scoring:**
- Static: **15** (multiple if statements, moderate complexity)
- Impact: **8** (API/validation changes)
- AI: **10** (moderate business logic)
- **Total: 33 → Tier 0 (Auto-merge)**

### Complex Algorithm
```python
def calculate_dynamic_pricing(user, product, market_conditions):
    base_price = get_product_price(product.id)
    
    for condition in market_conditions:
        if condition.type == 'demand':
            if condition.level > 0.8:
                base_price *= 1.2
            elif condition.level < 0.3:
                base_price *= 0.9
                
        if condition.type == 'competition':
            competitor_prices = get_competitor_prices(product.category)
            if base_price > max(competitor_prices):
                base_price = max(competitor_prices) * 0.95
                
    return apply_user_discount(base_price, user.tier)
```
**Scoring:**
- Static: **25** (nested loops, multiple conditions, complex logic)
- Impact: **12** (pricing affects multiple systems)
- AI: **20** (algorithmic complexity, business rules)
- **Total: 57 → Tier 1 (Standard Review)**

### Critical System Change
```python
async def process_payment_with_fraud_detection(payment_data):
    # Complex payment processing with multiple integrations
    fraud_score = await fraud_detection_service.analyze(payment_data)
    
    if fraud_score > FRAUD_THRESHOLD:
        await audit_service.log_suspicious_activity(payment_data)
        raise FraudDetectionError("Transaction flagged")
        
    payment_method = await payment_gateway.validate_method(payment_data)
    
    try:
        result = await payment_gateway.process_payment(payment_data)
        await update_user_balance(payment_data.user_id, result.amount)
        await notification_service.send_receipt(payment_data.user_id)
        return result
    except PaymentError as e:
        await audit_service.log_payment_failure(payment_data, str(e))
        raise
```
**Scoring:**
- Static: **30** (async patterns, error handling, complex flow)
- Impact: **18** (payment system, security, multiple integrations)
- AI: **25** (critical business logic, requires domain expertise)
- **Total: 73 → Tier 2 (Expert Review)**

## Configuration Constants

The scoring system uses configurable thresholds defined in `ScoringThresholds` class:

```python
# Score Caps
STATIC_SCORE_MAX = 40
IMPACT_SCORE_MAX = 30
AI_SCORE_MAX = 30

# Tier Thresholds
TIER_0_THRESHOLD = 35  # Auto-merge
TIER_1_THRESHOLD = 65  # Standard review

# Static Scoring
CONTROL_STRUCTURE_POINTS = 1
FUNCTION_LENGTH_LARGE_PENALTY = 3  # >50 lines
FUNCTION_LENGTH_MEDIUM_PENALTY = 1  # >20 lines

# Impact Scoring
IMPORTS_PER_POINT = 5  # 1 point per 5 imports
DATABASE_API_POINTS = 3

# AI Scoring (Heuristic)
COMPLEX_PATTERN_POINTS = 5
BUSINESS_LOGIC_POINTS = 3
DATA_STRUCTURE_POINTS = 2
```

## Integration Points

- **GitHub Actions**: Automatic scoring on PR creation/updates
- **Azure AI Foundry**: AI-powered complexity assessment and quality gate analysis
- **SonarQube**: Code quality integration and penalties
- **PR Automation**: Automatic labeling and reviewer assignment
- **Quality Gates**: AI-enhanced integration with build pipeline decisions

## Continuous Improvement

The scoring system is designed for continuous refinement:

- **Feedback Collection**: Track actual review time vs. predicted complexity
- **Threshold Tuning**: Adjust scoring weights based on team feedback
- **Pattern Recognition**: Expand keyword patterns and complexity indicators
- **Team Calibration**: Regular reviews of scoring accuracy and tier assignments
