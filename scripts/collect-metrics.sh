#!/bin/bash

# Script to collect performance metrics for security analysis tools
TOOL_NAME=$1
START_TIME=$2

if [ -z "$TOOL_NAME" ] || [ -z "$START_TIME" ]; then
    echo "Usage: $0 <tool_name> <start_time>"
    exit 1
fi

echo "🔄 Collecting metrics for $TOOL_NAME..."

# Calculate metrics
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Count lines of code for different languages
LOC_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_TOTAL=$((LOC_PYTHON + LOC_JS + LOC_TS))

# Count files
FILES_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" | wc -l)
FILES_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TOTAL=$((FILES_PYTHON + FILES_JS + FILES_TS))

# Get repository size (in KB)
REPO_SIZE=$(du -sk . 2>/dev/null | cut -f1 || echo 0)

# Calculate performance ratio with safety check
if [ "$LOC_TOTAL" -gt 0 ]; then
    PERFORMANCE_RATIO=$(echo "scale=8; $DURATION / $LOC_TOTAL" | bc -l 2>/dev/null || echo "0.0")
else
    PERFORMANCE_RATIO="0.0"
fi

# Create metrics directory if it doesn't exist
mkdir -p metrics

# Ensure we have valid values
LOC_TOTAL=${LOC_TOTAL:-0}
FILES_TOTAL=${FILES_TOTAL:-0}
REPO_SIZE=${REPO_SIZE:-0}
DURATION=${DURATION:-0}

# Log to structured JSON format - create new file or append
cat >> performance-metrics.jsonl << EOF
{"tool": "$TOOL_NAME", "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "duration_seconds": $DURATION, "lines_of_code": {"total": $LOC_TOTAL, "python": $LOC_PYTHON, "javascript": $LOC_JS, "typescript": $LOC_TS}, "files_analyzed": {"total": $FILES_TOTAL, "python": $FILES_PYTHON, "javascript": $FILES_JS, "typescript": $FILES_TS}, "repository_size_kb": $REPO_SIZE, "commit_sha": "${GITHUB_SHA:-unknown}", "branch": "${GITHUB_REF_NAME:-unknown}", "workflow_run_id": "${GITHUB_RUN_ID:-unknown}", "performance_ratio": $PERFORMANCE_RATIO}
EOF

# Also create individual tool metric file for easier debugging
cat > "metrics/${TOOL_NAME,,}-metrics.json" << EOF
{
  "tool": "$TOOL_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $DURATION,
  "lines_of_code": $LOC_TOTAL,
  "files_analyzed": $FILES_TOTAL,
  "repository_size_kb": $REPO_SIZE,
  "performance_ratio": $PERFORMANCE_RATIO,
  "commit_sha": "${GITHUB_SHA:-unknown}",
  "branch": "${GITHUB_REF_NAME:-unknown}",
  "workflow_run_id": "${GITHUB_RUN_ID:-unknown}"
}
EOF

echo "✅ Metrics collected for $TOOL_NAME:"
echo "   Duration: ${DURATION}s"
echo "   Lines of Code: ${LOC_TOTAL}"
echo "   Files: ${FILES_TOTAL}"
echo "   Performance Ratio: ${PERFORMANCE_RATIO} s/LOC"
echo "   Saved to: performance-metrics.jsonl and metrics/${TOOL_NAME,,}-metrics.json"

# Verify JSON is valid
if command -v python3 >/dev/null 2>&1; then
    echo "🔍 Validating JSON format..."
    if tail -1 performance-metrics.jsonl | python3 -m json.tool >/dev/null 2>&1; then
        echo "✅ JSON format is valid"
    else
        echo "❌ Warning: JSON format may be invalid"
        echo "Last line content:"
        tail -1 performance-metrics.jsonl
    fi
fi
