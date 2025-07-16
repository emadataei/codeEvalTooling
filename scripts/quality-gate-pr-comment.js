const fs = require('fs');

module.exports = async ({ github, context }) => {
  console.log('=== Quality Gate PR Comment Debug ===');
  console.log('Event name:', context.eventName);
  console.log('Event type:', context.payload.action);
  console.log('Has issue context:', !!context.issue);
  console.log('Has PR context:', !!context.payload.pull_request);
  
  const prNumber = context.issue?.number || 
                 context.payload?.pull_request?.number || 
                 context.payload?.number;
  
  console.log('Detected PR number:', prNumber);
  
  if (!prNumber) {
    console.log('No PR number found, skipping comment');
    console.log('Available context keys:', Object.keys(context));
    if (context.payload) {
      console.log('Payload keys:', Object.keys(context.payload));
    }
    return;
  }
  
  console.log('Attempting to read quality-gate-results.json...');
  let results = { passed: false, score: 0, summary: 'Failed to load results' };
  try {
    results = JSON.parse(fs.readFileSync('quality-gate-results.json', 'utf8'));
    console.log('Quality gate results loaded successfully:', Object.keys(results));
  } catch (error) {
    console.log('Could not read quality gate results:', error.message);
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
  
  try {
    console.log('Looking for existing GitHub Actions Quality Gate comments...');
    const { data: comments } = await github.rest.issues.listComments({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: prNumber,
    });
    
    console.log(`Found ${comments.length} total comments on PR`);
    
    const existingComment = comments.find(comment => 
      comment.body.includes('<!-- GITHUB_ACTIONS_QUALITY_GATE -->') ||
      (comment.body.includes('Quality Gate') && comment.user.login === 'github-actions[bot]')
    );
    
    const commentWithId = `<!-- GITHUB_ACTIONS_QUALITY_GATE -->\n${comment}`;
    
    if (existingComment) {
      console.log('Updating existing GitHub Actions Quality Gate comment ID:', existingComment.id);
      await github.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: existingComment.id,
        body: commentWithId
      });
      console.log('Successfully updated existing GitHub Actions comment');
    } else {
      console.log('Creating new GitHub Actions Quality Gate comment...');
      const result = await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
        body: commentWithId
      });
      console.log('Successfully created new GitHub Actions comment with ID:', result.data.id);
    }
  } catch (error) {
    console.error('Error posting/updating GitHub Actions comment:', error);
    console.error('Error details:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
};
