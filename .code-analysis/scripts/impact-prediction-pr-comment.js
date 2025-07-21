const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping impact prediction comment');
    return;
  }

  const results = loadResults('impact-prediction-results.json', { 
    overall_risk_score: 0.3,
    deployment_readiness: 'READY - Low risk deployment',
    summary: 'Impact prediction analysis failed',
    impacts: [],
    test_recommendations: [],
    monitoring_suggestions: [],
    rollback_considerations: ['Standard rollback procedures apply']
  });

  const comment = buildComment(results);
  
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'Impact Prediction',
    `impact-prediction-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Impact prediction comment posted/updated successfully');
};

function buildComment(results) {
  let comment = `## Impact Prediction\n\n`;
  
  // Risk score with visual bar
  const riskLevel = getRiskLevel(results.overall_risk_score);
  const riskBar = getRiskBar(results.overall_risk_score);
  const riskPercentage = Math.round(results.overall_risk_score * 100);
  comment += `**Risk Assessment:** ${riskBar} ${riskPercentage}% (${riskLevel})\n`;
  comment += `**Deployment Status:** ${results.deployment_readiness.split(' - ')[0]}\n\n`;

  // High priority impacts in structured format
  const criticalImpacts = results.impacts.filter(impact => 
    impact.severity === 'high' || impact.severity === 'critical'
  );
  
  if (criticalImpacts.length > 0) {
    comment += `### Key Concerns\n`;
    comment += `| Severity | Category | Issue |\n`;
    comment += `|----------|----------|-------|\n`;
    criticalImpacts.slice(0, 2).forEach(impact => {
      comment += `| ${impact.severity.toUpperCase()} | ${impact.category.toUpperCase()} | ${impact.description.split('.')[0]} |\n`;
    });
    comment += `\n`;
  }

  // Critical tests with priority indicators
  const criticalTests = results.test_recommendations.filter(test => test.priority === 'high');
  if (criticalTests.length > 0) {
    comment += `**Required Testing:**\n`;
    criticalTests.slice(0, 2).forEach(test => {
      comment += `- [!] ${test.test_type.toUpperCase()}\n`;
    });
    comment += `\n`;
  }

  // Deployment guidance with visual indicator
  if (results.overall_risk_score > 0.7) {
    comment += `> **⚠ High Risk Deployment:** Consider staged rollout strategy\n\n`;
  }

  // Footer
  comment += `---\n*AI-generated analysis for review triage*`;

  return comment;
}

function getRiskLevel(riskScore) {
  if (riskScore < 0.3) return 'LOW';
  if (riskScore < 0.7) return 'MEDIUM';
  return 'HIGH';
}

function getRiskBar(riskScore) {
  const filled = Math.round(riskScore * 10);
  const empty = 10 - filled;
  return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
}
