# Comment Update Issue Fix

## Problem
The "Impact Assessment | MANAGEABLE Risk" comment was not updating existing comments but instead creating new ones on each workflow run.

## Root Cause Analysis

### 1. Identifier Mismatch
- **Comment Body**: Used `## ⚡ Impact Assessment` in the comment content
- **Comment Identifier**: Was using `'Risk Assessment'` as the identifier
- **Result**: Comment matching failed because the identifier didn't match the actual comment content

### 2. Unstable Comment IDs
- **Previous Logic**: Used `context.payload?.pull_request?.head?.sha` for comment IDs
- **Problem**: SHA can change between workflow runs or be inconsistent
- **Result**: Comment ID matching failed, leading to duplicate comments instead of updates

## Solutions Implemented

### 1. Fixed Identifier Mismatch
```javascript
// Before
createOrUpdateComment(
  github, context, prNumber, comment, 
  'Risk Assessment',  // ❌ Didn't match comment content
  commentId
);

// After  
createOrUpdateComment(
  github, context, prNumber, comment, 
  'Impact Assessment',  // ✅ Matches "## ⚡ Impact Assessment"
  commentId
);
```

### 2. Stabilized Comment IDs
```javascript
// Before (unstable)
`impact-prediction-${context.payload?.pull_request?.head?.sha || 'unknown'}`

// After (stable)
`impact-prediction-pr-${prNumber}`
```

### 3. Applied Fix Across All Comment Scripts
Updated comment IDs for consistency across all scripts:
- `intent-classification-pr-comment.js`
- `impact-prediction-pr-comment.js` 
- `dependency-graph-pr-comment.js`
- `quality-gate-pr-comment.js`
- `semantic-commit-pr-description.js`

## How Comment Matching Works

### Dual Matching Strategy
The `createOrUpdateComment` function uses a two-tier approach:

1. **Primary**: Match by unique comment ID (hidden HTML comment)
   ```html
   <!-- comment-id: impact-prediction-pr-123 -->
   ```

2. **Fallback**: Match by identifier text in comment body
   ```javascript
   comment.body.includes('Impact Assessment')
   ```

### Comment ID Format
Now using stable, PR-specific IDs:
- `intent-classification-pr-{prNumber}`
- `impact-prediction-pr-{prNumber}`
- `dependency-graph-pr-{prNumber}`
- `quality-gate-pr-{prNumber}`
- `semantic-commit-pr-{prNumber}`

## Expected Behavior After Fix

### First Run
- Creates new comments with proper identifiers and stable comment IDs
- Each comment gets a hidden HTML comment with the unique ID

### Subsequent Runs
- **Primary Matching**: Finds existing comments by comment ID (most reliable)
- **Fallback Matching**: Uses identifier text if comment ID isn't found
- **Updates in Place**: Modifies existing comment content instead of creating new ones

### Benefits
- **No Duplicate Comments**: Each analysis type maintains exactly one comment per PR
- **Consistent Updates**: Comments update reliably across workflow runs
- **Better UX**: Reviewers see evolving analysis instead of comment spam
- **Preserved Context**: Comment threads and reactions are maintained

## Validation

### Testing
To verify the fix works:
1. Trigger a workflow run on a PR
2. Verify initial comments are created
3. Make another change and trigger workflow again  
4. Confirm comments are updated (not duplicated)
5. Check that comment IDs are present in HTML source

### Monitoring
Watch for these success indicators:
- Console logs showing "Successfully updated existing comment"
- No duplicate analysis comments in PRs
- Stable comment URLs between workflow runs

This fix ensures reliable comment updating and eliminates the duplicate comment issue that was affecting the Impact Assessment and other analysis comments.
