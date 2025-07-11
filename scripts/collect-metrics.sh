#!/bin/bash

# Script to collect performance metrics for security analysis tools
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

# Create the JSON entry - using proper JSON formatting
JSON_ENTRY=$(cat << EOF
{"tool": "$TOOL_NAME", "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "duration_seconds": $DURATION, "lines_of_code": {"total": $LOC_TOTAL, "python": $LOC_PYTHON, "javascript": $LOC_JS, "typescript": $LOC_TS}, "files_analyzed": {"total": $FILES_TOTAL, "python": $FILES_PYTHON, "javascript": $FILES_JS, "typescript": $FILES_TS}, "repository_size_kb": $REPO_SIZE, "commit_sha": "${GITHUB_SHA:-unknown}", "branch": "${GITHUB_REF_NAME:-unknown}", "workflow_run_id": "${GITHUB_RUN_ID:-unknown}", "performance_ratio": $PERFORMANCE_RATIO}
EOF
)

# Log to structured JSON format
echo "$JSON_ENTRY" >> performance-metrics.jsonl

echo "💾 Metrics saved to performance-metrics.jsonl"

# Also create individual tool metric file for debugging
echo "$JSON_ENTRY" | jq '.' > "metrics/${TOOL_NAME,,}-metrics.json" 2>/dev/null || {
    # Fallback if jq is not available
    cat > "metrics/${TOOL_NAME,,}-metrics.json" << EOF
{
  "tool": "$TOOL_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $DURATION,
  "lines_of_code": $LOC_TOTAL,
  "files_analyzed": $FILES_TOTAL,
  "repository_size_kb": $REPO_SIZE,
  "performance_ratio": $PERFORMANCE_RATIO
}
EOF
}

echo "✅ Metrics collected for $TOOL_NAME:"
echo "   📊 Duration: ${DURATION}s"
echo "   📝 Lines of Code: ${LOC_TOTAL}"
echo "   📂 Files: ${FILES_TOTAL}"
echo "   ⚡ Performance Ratio: ${PERFORMANCE_RATIO} s/LOC"
echo "   💾 Repository Size: ${REPO_SIZE} KB"
echo "   📄 Saved to: performance-metrics.jsonl"

# Verify the JSON is valid
if command -v python3 >/dev/null 2>&1; then
    echo "🔍 Validating JSON format..."
    if echo "$JSON_ENTRY" | python3 -m json.tool >/dev/null 2>&1; then
        echo "✅ JSON format is valid"
    else
        echo "❌ Warning: JSON format validation failed"
        echo "JSON content: $JSON_ENTRY"
    fi
else
    echo "ℹ️  Python3 not available for JSON validation"
fi

echo "🎉 Metrics collection completed for $TOOL_NAME"
