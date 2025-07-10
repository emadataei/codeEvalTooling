#!/bin/bash

# Script to collect performance metrics for security analysis tools
TOOL_NAME=$1
START_TIME=$2

if [ -z "$TOOL_NAME" ] || [ -z "$START_TIME" ]; then
    echo "Usage: $0 <tool_name> <start_time>"
    exit 1
fi

# Calculate metrics
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Count lines of code for different languages
LOC_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
LOC_TOTAL=$((LOC_PYTHON + LOC_JS + LOC_TS))

# Count files
FILES_PYTHON=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" | wc -l)
FILES_JS=$(find . -name "*.js" -o -name "*.jsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TS=$(find . -name "*.ts" -o -name "*.tsx" -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
FILES_TOTAL=$((FILES_PYTHON + FILES_JS + FILES_TS))

# Get repository size (in KB)
REPO_SIZE=$(du -sk . | cut -f1)

# Create metrics directory if it doesn't exist
mkdir -p metrics

# Log to structured JSON format
cat >> performance-metrics.jsonl << EOF
{
  "tool": "$TOOL_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $DURATION,
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
  "performance_ratio": $(echo "scale=4; $DURATION / $LOC_TOTAL" | bc -l 2>/dev/null || echo "0")
}
EOF

# Also create individual tool metric file
cat > "metrics/${TOOL_NAME,,}-metrics.json" << EOF
{
  "tool": "$TOOL_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $DURATION,
  "lines_of_code": $LOC_TOTAL,
  "files_analyzed": $FILES_TOTAL,
  "repository_size_kb": $REPO_SIZE,
  "performance_ratio": $(echo "scale=4; $DURATION / $LOC_TOTAL" | bc -l 2>/dev/null || echo "0")
}
EOF

echo "✅ Metrics collected for $TOOL_NAME: ${DURATION}s for ${LOC_TOTAL} LOC"
