const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  console.log('=== Quality Gate PR Comment Debug ===');
  console.log('Event name:', context.eventName);
  console.log('Event type:', context.payload.action);
  console.log('Has issue context:', !!context.issue);
  console.log('Has PR context:', !!context.payload.pull_request);
  
  const prNumber = getPRNumber(context);
  console.log('Detected PR number:', prNumber);
  
  if (!prNumber) {
    console.log('No PR number found, skipping comment');
    return;
  }
  
  console.log('Attempting to read quality-gate-results.json...');
  const results = loadResults('quality-gate-results.json', { 
    passed: false, 
    score: 0, 
    summary: 'Failed to load results' 
  });
  
  if (!results.passed && results.summary === 'Failed to load results') {
    console.log('Failed to load results, skipping comment');
    return;
  }
  
  const passed = results.passed;
  const score = results.score;
  const status = passed ? 'PASSED' : 'FAILED';
  
  // Build comprehensive, actionable comment
  const timestamp = new Date().toISOString();
  const runId = process.env.GITHUB_RUN_ID || 'unknown';
  let comment = `## Code Quality Gate ${status}\n\n`;
  comment += `*Last updated: ${timestamp} (Run: ${runId})*\n\n`;
  
  // Score and summary with context
  comment += `**Quality Score:** ${score}/100`;
  if (score >= 85) {
    comment += ` (Excellent)`;
  } else if (score >= 70) {
    comment += ` (Good)`;
  } else if (score >= 50) {
    comment += ` (Needs Improvement)`;
  } else {
    comment += ` (Significant Issues)`;
  }
  comment += `\n\n`;
  
  comment += `**Assessment:** ${results.summary}\n\n`;
  
  // Blocking issues with detailed guidance
  if (results.issues && results.issues.blocking && results.issues.blocking.length > 0) {
    comment += `### Critical Issues (Must Fix Before Merge)\n\n`;
    comment += `The following issues must be resolved before this PR can proceed:\n\n`;
    
    results.issues.blocking.forEach((issue, index) => {
      comment += `**${index + 1}. ${issue.category} Issue**\n`;
      comment += `- **Problem:** ${issue.message}\n`;
      if (issue.file !== 'PR' && issue.file !== 'general') {
        comment += `- **Location:** \`${issue.file}\``;
        if (issue.line) comment += ` (line ${issue.line})`;
        comment += `\n`;
      }
      if (issue.suggestion) {
        comment += `- **Action Required:** ${issue.suggestion}\n`;
      }
      comment += `\n`;
    });
  }
  
  // Warning issues with helpful context
  if (results.issues && results.issues.warning && results.issues.warning.length > 0) {
    comment += `### Quality Improvements (Recommended)\n\n`;
    comment += `These issues don't block the merge but should be addressed for better code quality:\n\n`;
    
    const warningsToShow = Math.min(results.issues.warning.length, 8);
    results.issues.warning.slice(0, warningsToShow).forEach((issue, index) => {
      comment += `**${index + 1}. ${issue.category}**\n`;
      comment += `- ${issue.message}`;
      if (issue.file !== 'PR' && issue.file !== 'general') {
        comment += ` (in \`${issue.file}\`)`;
      }
      comment += `\n`;
      if (issue.suggestion) {
        comment += `- **Suggested Fix:** ${issue.suggestion}\n`;
      }
      comment += `\n`;
    });
    
    if (results.issues.warning.length > warningsToShow) {
      const remaining = results.issues.warning.length - warningsToShow;
      comment += `*...and ${remaining} additional improvement${remaining > 1 ? 's' : ''} available in detailed analysis.*\n\n`;
    }
  }
  
  // Add project standards context if available
  if (results.standards_applied) {
    comment += `### Standards Applied\n\n`;
    comment += `This analysis used your project's coding standards from \`.github/copilot-instructions.md\`:\n`;
    if (results.emphasis_areas && results.emphasis_areas.length > 0) {
      comment += `- **Focus Areas:** ${results.emphasis_areas.join(', ')}\n`;
    }
    comment += `- **AI Analysis:** Enhanced review using project-specific patterns\n\n`;
  }
  
  // Next steps guidance
  if (passed) {
    comment += `### Next Steps\n\n`;
    comment += `**Status:** Quality gate passed. This PR is ready for cognitive complexity analysis.\n\n`;
    if (results.issues && results.issues.warning && results.issues.warning.length > 0) {
      comment += `**Recommendation:** Consider addressing the quality improvements above before final merge.\n\n`;
    }
    comment += `**For Reviewers:** Focus on business logic, architecture, and domain-specific concerns.\n`;
  } else {
    comment += `### Required Actions\n\n`;
    comment += `**Status:** Quality gate failed. Please resolve critical issues above before requesting review.\n\n`;
    comment += `**For Developers:** \n`;
    comment += `1. Fix all critical issues listed above\n`;
    comment += `2. Run quality checks locally before pushing\n`;
    comment += `3. Consider the recommended improvements for better code quality\n\n`;
    comment += `**Note:** Cognitive analysis will still run to provide complexity insights.\n`;
  }
  
  console.log('Creating PR comment with content length:', comment.length);
  console.log('Comment preview (first 100 chars):', comment.substring(0, 100));
  
  // Create or update the comment using shared utility
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'Code Quality Gate',  // identifier to find existing comments (matches comment header)
    'QUALITY_GATE_COMMENT'  // unique comment ID for reliable matching
  );
};
