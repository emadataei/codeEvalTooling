const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping comment');
    return;
  }
  
  const results = loadResults('quality-gate-results.json', { 
    passed: false, 
    score: 0, 
    summary: 'Failed to load results' 
  });
  
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
  
  // Create or update the comment using shared utility
  try {
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      comment, 
      'Code Quality Gate',  // identifier to find existing comments (matches comment header)
      'QUALITY_GATE_COMMENT'  // unique comment ID for reliable matching
    );
  } catch (error) {
    console.error('Error creating or updating quality gate comment:', error);
    throw error;
  }
};
