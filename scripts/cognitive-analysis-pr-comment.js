const fs = require('fs');

module.exports = async ({ github, context }) => {
  let results = { tier: 0, total_score: 0, reasoning: 'Failed to load results' };
  try {
    results = JSON.parse(fs.readFileSync('cognitive-analysis-results.json', 'utf8'));
  } catch (error) {
    console.log('Could not read cognitive analysis results:', error);
  }
  
  const tier = results.tier;
  const score = results.total_score;
  
  const tierInfo = {
    0: { icon: 'TIER0', name: 'Tier 0', action: 'Auto-mergeable', color: 'green' },
    1: { icon: 'TIER1', name: 'Tier 1', action: 'Light Review Required', color: 'yellow' },
    2: { icon: 'TIER2', name: 'Tier 2', action: 'Deep Review Required', color: 'red' }
  };
  
  const info = tierInfo[tier] || tierInfo[2];
  
  let comment = `## Cognitive Complexity Analysis\n\n`;
  comment += `### ${info.icon} ${info.name} - ${info.action}\n\n`;
  comment += `**Total Score:** ${score} points\n`;
  comment += `**Reasoning:** ${results.reasoning}\n\n`;
  
  if (results.static_score !== undefined) {
    comment += `### Score Breakdown\n`;
    comment += `- **Static Analysis:** ${results.static_score}/40 points\n`;
    comment += `- **Impact Surface:** ${results.impact_score}/30 points\n`;
    comment += `- **AI Complexity:** ${results.ai_score}/30 points\n`;
    if (results.quality_penalty > 0) {
      comment += `- **Quality Penalty:** +${results.quality_penalty} points\n`;
    }
    comment += '\n';
  }
  
  comment += `### Review Guidelines\n`;
  if (tier === 0) {
    comment += `- **Auto-merge eligible** (if all checks pass)\n`;
    comment += `- No human review required\n`;
    comment += `- Low complexity change\n`;
  } else if (tier === 1) {
    comment += `- **Single reviewer** required\n`;
    comment += `- **12-hour SLA** for review\n`;
    comment += `- Standard review process\n`;
  } else {
    comment += `- **Domain expert review** required\n`;
    comment += `- **48-hour SLA** for review\n`;
    comment += `- High complexity - careful review needed\n`;
  }
  
  const { data: comments } = await github.rest.issues.listComments({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: context.issue.number,
  });
  
  const existingComment = comments.find(comment => 
    comment.body.includes('Cognitive Complexity Analysis')
  );
  
  if (existingComment) {
    await github.rest.issues.updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: existingComment.id,
      body: comment
    });
  } else {
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: context.issue.number,
      body: comment
    });
  }
  
  const labels = [`tier-${tier}`];
  if (tier === 0) labels.push('auto-merge-candidate');
  if (tier === 2) labels.push('needs-expert-review');
  
  await github.rest.issues.setLabels({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: context.issue.number,
    labels: labels
  });
};
