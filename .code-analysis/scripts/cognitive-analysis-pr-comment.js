const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  console.log('=== Cognitive Analysis PR Comment Debug ===');
  console.log('Event name:', context.eventName);
  console.log('Event type:', context.payload.action);
  console.log('Has issue context:', !!context.issue);
  console.log('Has PR context:', !!context.payload.pull_request);
  console.log('Starting cognitive analysis PR comment and label setting...');
  
  const prNumber = getPRNumber(context);
  console.log('Detected PR number:', prNumber);
  
  if (!prNumber) {
    console.log('No PR number found, skipping comment');
    return;
  }
  
  console.log('Attempting to read cognitive-analysis-results.json...');
  const results = loadResults('cognitive-analysis-results.json', { 
    tier: 0, 
    total_score: 0, 
    reasoning: 'Failed to load results' 
  });
  
  console.log('Loaded results:', results);
  if (results.reasoning === 'Failed to load results') {
    console.log('Failed to load cognitive analysis results, but will create comment anyway');
  }
  
  const tier = results.tier;
  const score = results.total_score;
  
  const tierInfo = {
    0: { name: 'Tier 0', action: 'Auto-Merge Eligible', description: 'Low complexity, minimal risk' },
    1: { name: 'Tier 1', action: 'Standard Review Required', description: 'Moderate complexity, normal review process' },
    2: { name: 'Tier 2', action: 'Expert Review Required', description: 'High complexity, requires domain expert' }
  };
  
  const info = tierInfo[tier] || tierInfo[2];
  
  const timestamp = new Date().toISOString();
  const runId = process.env.GITHUB_RUN_ID || 'unknown';
  let comment = `## Cognitive Complexity Analysis\n\n`;
  comment += `*Last updated: ${timestamp} (Run: ${runId})*\n\n`;
  comment += `### ${info.name} - ${info.action}\n\n`;
  comment += `**Complexity Score:** ${score} points (${info.description})\n\n`;
  comment += `**Analysis Summary:** ${results.reasoning}\n\n`;
  
  // Detailed score breakdown with explanations
  if (results.static_score !== undefined) {
    comment += `### Complexity Breakdown\n\n`;
    comment += `| Component | Score | Threshold | Status |\n`;
    comment += `|-----------|-------|-----------|--------|\n`;
    comment += `| Static Analysis | ${results.static_score}/40 | <20 for Tier 0 | ${results.static_score < 20 ? 'Low' : results.static_score < 30 ? 'Medium' : 'High'} |\n`;
    comment += `| Impact Surface | ${results.impact_score}/30 | <15 for Tier 0 | ${results.impact_score < 15 ? 'Low' : results.impact_score < 25 ? 'Medium' : 'High'} |\n`;
    comment += `| AI Complexity | ${results.ai_score}/30 | <15 for Tier 0 | ${results.ai_score < 15 ? 'Low' : results.ai_score < 25 ? 'Medium' : 'High'} |\n`;
    if (results.quality_penalty > 0) {
      comment += `| Quality Penalty | +${results.quality_penalty} | N/A | Applied |\n`;
    }
    comment += `\n`;
  }
  
  // Review guidelines with specific actions
  comment += `### Review Process\n\n`;
  
  if (tier === 0) {
    comment += `**Auto-Merge Candidate**\n`;
    comment += `- This change is low-risk and can be merged automatically if all checks pass\n`;
    comment += `- No human review required unless requested by the author\n`;
    comment += `- Typical changes: documentation updates, minor bug fixes, configuration changes\n\n`;
    comment += `**For Authors:** Ensure all automated checks pass before merging\n`;
    comment += `**For Maintainers:** This PR is eligible for auto-merge workflows\n`;
  } else if (tier === 1) {
    comment += `**Standard Review Process**\n`;
    comment += `- Requires approval from one team member before merge\n`;
    comment += `- Target review time: 12 hours during business days\n`;
    comment += `- Focus areas: code correctness, style adherence, basic logic review\n\n`;
    comment += `**For Reviewers:**\n`;
    comment += `- Review for obvious bugs and style issues\n`;
    comment += `- Check that tests cover the main functionality\n`;
    comment += `- Verify documentation is updated if needed\n`;
    comment += `- Standard approval process applies\n`;
  } else {
    comment += `**Expert Review Required**\n`;
    comment += `- Requires approval from a domain expert or senior team member\n`;
    comment += `- Target review time: 48 hours, may require additional time for complex changes\n`;
    comment += `- Focus areas: architecture impact, performance implications, security considerations\n\n`;
    comment += `**For Reviewers:**\n`;
    comment += `- Conduct thorough code review focusing on business logic\n`;
    comment += `- Consider architectural implications and future maintainability\n`;
    comment += `- Verify comprehensive test coverage for complex scenarios\n`;
    comment += `- May require multiple review rounds or team discussion\n`;
  }
  
  // Create or update the comment
  console.log('Creating or updating cognitive analysis comment...');
  console.log('Comment content length:', comment.length);
  console.log('First 200 chars of comment:', comment.substring(0, 200));
  
  try {
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      comment, 
      'Cognitive Complexity Analysis',  // identifier to find existing comments
      'COGNITIVE_ANALYSIS_COMMENT'  // unique comment ID for reliable matching
    );
    console.log('Successfully created or updated cognitive analysis comment');
  } catch (error) {
    console.error('Error creating or updating cognitive analysis comment:', error);
    throw error;
  }
  
  console.log('Cognitive analysis comment completed. Labels will be set by update_pr_metadata.py script.');
};
