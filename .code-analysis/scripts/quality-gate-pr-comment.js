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
  const icon = passed ? 'PASS' : 'FAIL';
  const status = passed ? 'PASSED' : 'FAILED';
  
  let comment = `## ${icon} GitHub Actions Quality Gate ${status}\n\n`;
  comment += `**Score:** ${score}/100\n`;
  comment += `**Summary:** ${results.summary}\n\n`;
  
  if (results.issues && results.issues.blocking && results.issues.blocking.length > 0) {
    comment += `### BLOCKING Issues (Must Fix)\n\n`;
    results.issues.blocking.forEach(issue => {
      comment += `- **${issue.category}**: ${issue.message}\n`;
      if (issue.file !== 'PR') {
        comment += `  - Location: \`${issue.file}:${issue.line}\`\n`;
      }
      if (issue.suggestion) {
        comment += `  - Suggestion: ${issue.suggestion}\n`;
      }
      comment += '\n';
    });
  }
  
  if (results.issues && results.issues.warning && results.issues.warning.length > 0) {
    comment += `### Warnings\n\n`;
    results.issues.warning.slice(0, 5).forEach(issue => {
      comment += `- **${issue.category}**: ${issue.message}\n`;
      if (issue.file !== 'PR') {
        comment += `  - Location: \`${issue.file}:${issue.line}\`\n`;
      }
      comment += '\n';
    });
    if (results.issues.warning.length > 5) {
      comment += `... and ${results.issues.warning.length - 5} more warnings\n\n`;
    }
  }
  
  if (passed) {
    comment += `\n**Ready for Cognitive Analysis** - Proceeding to next review stage.\n`;
  } else {
    comment += `\n**Cognitive Analysis Blocked** - Fix blocking issues before proceeding.\n`;
  }
  
  console.log('Creating PR comment with content length:', comment.length);
  console.log('Comment preview (first 100 chars):', comment.substring(0, 100));
  
  // Create or update the comment using shared utility
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'GitHub Actions Quality Gate',  // identifier to find existing comments
    'GITHUB_ACTIONS_QUALITY_GATE'  // comment ID for workflow tracking
  );
};
