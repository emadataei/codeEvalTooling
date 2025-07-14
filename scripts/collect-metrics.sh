#!/bin/bash

# Script to collect performance and security metrics for security analysis tools
TOOL_NAME=$1
START_TIME=$2

if [ -z "$TOOL_NAME" ] || [ -z "$START_TIME" ]; then
    echo "❌ Usage: $0 <tool_name> <start_time>"
    exit 1
fi

echo "🔄 Collecting metrics for $TOOL_NAME..."

# Calculate metrics
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "📊 Analysis duration: ${DURATION} seconds"

# Initialize security findings variables
VULNERABILITIES_HIGH=0
VULNERABILITIES_MEDIUM=0
VULNERABILITIES_LOW=0
VULNERABILITIES_TOTAL=0
ISSUES_FOUND=""

# Tool-specific security findings extraction
case "$TOOL_NAME" in
    "Semgrep")
        if [ -f "semgrep-results.json" ]; then
            echo "📄 Parsing Semgrep results..."
            if command -v jq >/dev/null 2>&1; then
                VULNERABILITIES_HIGH=$(jq '[.results[] | select(.extra.severity == "ERROR")] | length' semgrep-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_MEDIUM=$(jq '[.results[] | select(.extra.severity == "WARNING")] | length' semgrep-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_LOW=$(jq '[.results[] | select(.extra.severity == "INFO")] | length' semgrep-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_TOTAL=$(jq '.results | length' semgrep-results.json 2>/dev/null || echo 0)
                
                # Get top 5 most critical issues
                ISSUES_FOUND=$(jq -r '.results[:5] | .[] | "\(.extra.metadata.category // "unknown"):\(.check_id)"' semgrep-results.json 2>/dev/null | tr '\n' ';' || echo "")
            else
                # Fallback without jq
                VULNERABILITIES_TOTAL=$(grep -c '"check_id"' semgrep-results.json 2>/dev/null || echo 0)
            fi
        fi
        ;;
    "Snyk")
        # Parse Snyk JSON results
        if [ -f "snyk-code-results.json" ]; then
            echo "📄 Parsing Snyk results..."
            if command -v jq >/dev/null 2>&1; then
                VULNERABILITIES_HIGH=$(jq '[.runs[]?.results[]? | select(.level == "error")] | length' snyk-code-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_MEDIUM=$(jq '[.runs[]?.results[]? | select(.level == "warning")] | length' snyk-code-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_LOW=$(jq '[.runs[]?.results[]? | select(.level == "note")] | length' snyk-code-results.json 2>/dev/null || echo 0)
                VULNERABILITIES_TOTAL=$(jq '[.runs[]?.results[]?] | length' snyk-code-results.json 2>/dev/null || echo 0)
                
                # Get top 5 most critical issues
                ISSUES_FOUND=$(jq -r '.runs[]?.results[]? | select(.level == "error") | "\(.ruleId // "unknown"):\(.message.text // "No description")"' snyk-code-results.json 2>/dev/null | head -5 | tr '\n' ';' || echo "")
            else
                # Fallback without jq
                VULNERABILITIES_TOTAL=$(grep -c '"ruleId"' snyk-code-results.json 2>/dev/null || echo 0)
            fi
        fi
        ;;
    "CodeQL-"*)
        # CodeQL results are usually in GitHub's database, but we can check for local SARIF
        if [ -f "results.sarif" ]; then
            echo "📄 Parsing CodeQL SARIF results..."
            if command -v jq >/dev/null 2>&1; then
                VULNERABILITIES_HIGH=$(jq '[.runs[]?.results[]? | select(.level == "error")] | length' results.sarif 2>/dev/null || echo 0)
                VULNERABILITIES_MEDIUM=$(jq '[.runs[]?.results[]? | select(.level == "warning")] | length' results.sarif 2>/dev/null || echo 0)
                VULNERABILITIES_LOW=$(jq '[.runs[]?.results[]? | select(.level == "note")] | length' results.sarif 2>/dev/null || echo 0)
                VULNERABILITIES_TOTAL=$(jq '[.runs[]?.results[]?] | length' results.sarif 2>/dev/null || echo 0)
                
                # Get top 5 most critical issues
                ISSUES_FOUND=$(jq -r '.runs[]?.results[]? | "\(.ruleId // "unknown"):\(.message.text // "No description")"' results.sarif 2>/dev/null | head -5 | tr '\n' ';' || echo "")
            fi
        else
            echo "📄 CodeQL results stored in GitHub Security tab"
            # We'll get this from GitHub API if available
            VULNERABILITIES_TOTAL="github_stored"
        fi
        ;;
    "SonarQube")
        # SonarQube results are in SonarCloud, we can try to get metrics from quality gate
        echo "📄 SonarQube results stored in SonarCloud"
        # We could potentially use SonarQube API here
        VULNERABILITIES_TOTAL="sonarcloud_stored"
        ;;
esac

# Count lines of code for different languages
echo "📝 Counting lines of code..."
LOC_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)

# Ensure we have valid numbers
LOC_PYTHON=${LOC_PYTHON:-0}
LOC_JS=${LOC_JS:-0}
LOC_TS=${LOC_TS:-0}
LOC_TOTAL=$((LOC_PYTHON + LOC_JS + LOC_TS))

echo "📁 Lines of code found: Python=$LOC_PYTHON, JS=$LOC_JS, TS=$LOC_TS, Total=$LOC_TOTAL"

# Count files
FILES_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" | wc -l)
FILES_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TOTAL=$((FILES_PYTHON + FILES_JS + FILES_TS))

echo "📂 Files found: Python=$FILES_PYTHON, JS=$FILES_JS, TS=$FILES_TS, Total=$FILES_TOTAL"

# Get repository size (in KB)
REPO_SIZE=$(du -sk . 2>/dev/null | cut -f1 || echo 0)

# Calculate performance ratio with safety check
if [ "$LOC_TOTAL" -gt 0 ]; then
    PERFORMANCE_RATIO=$(echo "scale=8; $DURATION / $LOC_TOTAL" | bc -l 2>/dev/null || echo "0.0")
else
    PERFORMANCE_RATIO="0.0"
    LOC_TOTAL=1  # Avoid division by zero in reports
fi

echo "⚡ Performance ratio: $PERFORMANCE_RATIO s/LOC"

# Create metrics directory if it doesn't exist
mkdir -p metrics

# Create the JSON entry using a temporary file to avoid shell variable length limits
TEMP_JSON_FILE=$(mktemp)
cat > "$TEMP_JSON_FILE" << JSONEOF
{
  "tool": "$TOOL_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $DURATION,
  "security_findings": {
    "total_vulnerabilities": $VULNERABILITIES_TOTAL,
    "high_severity": $VULNERABILITIES_HIGH,
    "medium_severity": $VULNERABILITIES_MEDIUM,
    "low_severity": $VULNERABILITIES_LOW,
    "top_issues": "$ISSUES_FOUND"
  },
  "lines_of_code": {
    "total": $LOC_TOTAL,
    "python": $LOC_PYTHON,
    "javascript": $LOC_JS,
    "typescript": $LOC_TS
  },
  "files_analyzed": {
    "total": $FILES_TOTAL,
    "python": $FILES_PYTHON,
    "javascript": $FILES_JS,
    "typescript": $FILES_TS
  },
  "repository_size_kb": $REPO_SIZE,
  "commit_sha": "${GITHUB_SHA:-unknown}",
  "branch": "${GITHUB_REF_NAME:-unknown}",
  "workflow_run_id": "${GITHUB_RUN_ID:-unknown}",
  "performance_ratio": $PERFORMANCE_RATIO
}
JSONEOF

# Convert to single line JSON and append to metrics file
# Always use Python for consistent JSON formatting across environments
if command -v python3 >/dev/null 2>&1; then
    echo "🔧 Using Python3 for JSON formatting"
    python3 -c "
import json
with open('$TEMP_JSON_FILE', 'r') as f:
    data = json.load(f)
compact_json = json.dumps(data, separators=(',', ':'))
with open('performance-metrics.jsonl', 'a') as f:
    f.write(compact_json + '\n')
print(f'✅ Added compact JSON entry ({len(compact_json)} characters)')
"
elif command -v python >/dev/null 2>&1; then
    echo "🔧 Using Python for JSON formatting"
    python -c "
import json
with open('$TEMP_JSON_FILE', 'r') as f:
    data = json.load(f)
compact_json = json.dumps(data, separators=(',', ':'))
with open('performance-metrics.jsonl', 'a') as f:
    f.write(compact_json + '\n')
print('✅ Added compact JSON entry')
"
elif command -v jq >/dev/null 2>&1; then
    echo "🔧 Using jq for JSON formatting"
    # Force compact output and ensure it's a single line
    jq -c -M '.' "$TEMP_JSON_FILE" | tr -d '\n\r' >> performance-metrics.jsonl
    echo "" >> performance-metrics.jsonl
else
    echo "❌ Error: No JSON processor available (Python or jq required)"
    exit 1
fi

# Debug: Check what was actually written
echo "🔍 Verifying JSONL format..."
if [ -f performance-metrics.jsonl ]; then
    LAST_LINE=$(tail -1 performance-metrics.jsonl)
    echo "   Last entry length: ${#LAST_LINE} characters"
    echo "   Last entry preview: ${LAST_LINE:0:100}..."
    
    # Count lines in the last JSON object (should be 1)
    NEWLINE_COUNT=$(echo "$LAST_LINE" | grep -o $'\n' | wc -l)
    if [ "$NEWLINE_COUNT" -eq 0 ]; then
        echo "   ✅ Single-line JSON confirmed"
    else
        echo "   ❌ Warning: Multi-line JSON detected ($NEWLINE_COUNT newlines)"
    fi
else
    echo "   ❌ Warning: performance-metrics.jsonl not found"
fi

# Also create individual tool metric file for debugging
cp "$TEMP_JSON_FILE" "metrics/${TOOL_NAME,,}-metrics.json"

# Clean up temp file
rm -f "$TEMP_JSON_FILE"

# Ensure the file has proper permissions and no BOM
if command -v dos2unix >/dev/null 2>&1; then
    dos2unix performance-metrics.jsonl 2>/dev/null || true
fi

echo "💾 Metrics saved to performance-metrics.jsonl"

echo "✅ Metrics collected for $TOOL_NAME:"
echo "   📊 Duration: ${DURATION}s"
echo "   � Security Findings: ${VULNERABILITIES_TOTAL} total (High:${VULNERABILITIES_HIGH}, Med:${VULNERABILITIES_MEDIUM}, Low:${VULNERABILITIES_LOW})"
echo "   �📝 Lines of Code: ${LOC_TOTAL}"
echo "   📂 Files: ${FILES_TOTAL}"
echo "   ⚡ Performance Ratio: ${PERFORMANCE_RATIO} s/LOC"
echo "   💾 Repository Size: ${REPO_SIZE} KB"
echo "   📄 Saved to: performance-metrics.jsonl"

# Verify the JSON is valid
if command -v python3 >/dev/null 2>&1; then
    echo "🔍 Validating JSON format..."
    if tail -1 performance-metrics.jsonl | python3 -c "import json, sys; json.loads(sys.stdin.read())" 2>/dev/null; then
        echo "✅ JSON format is valid"
    else
        echo "❌ Warning: JSON format validation failed"
        echo "Last JSON entry: $(tail -1 performance-metrics.jsonl | head -c 200)..."
    fi
else
    echo "ℹ️  Python3 not available for JSON validation"
fi

echo "🎉 Metrics collection completed for $TOOL_NAME"
