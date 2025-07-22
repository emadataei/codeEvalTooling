const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping AI pre-review comment');
    return;
  }

  const results = loadResults('ai-pre-review-results.json', { 
    summary: 'AI pre-review analysis failed',
    risk_level: 'UNKNOWN',
    risk_factors: [],
    file_categories: {},
    file_count: 0,
    ai_analysis: {
      summary: 'Analysis failed',
      business_impact: 'Unknown',
      technical_changes: 'Unknown',
      potential_issues: 'Manual review required'
    },
    confidence_metrics: {
      analysis_confidence: 'MEDIUM',
      prediction_reliability: 'MEDIUM',
      completeness: 'MEDIUM'
    }
  });

  const comment = buildComment(results);
  
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'AI Pre-Review Analysis',
    `ai-pre-review-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('AI pre-review comment posted/updated successfully');
};

function buildComment(results) {
  const confidenceTier = getConfidenceTier(results);
  const riskLevel = getRiskLevel(results.risk_level);
  
  let comment = `## AI Pre-Review Analysis\n\n`;
  
  // Header with confidence and risk
  comment += `**Confidence:** ${confidenceTier} | **Risk:** ${riskLevel} | **Files:** ${results.file_count}\n\n`;

  // Summary section
  const summarySection = buildSummarySection(results);
  comment += summarySection;

  // File categories breakdown
  const categoriesSection = buildCategoriesSection(results);
  if (categoriesSection) {
    comment += categoriesSection;
  }

  // Business impact and technical details
  const impactSection = buildImpactSection(results);
  if (impactSection) {
    comment += impactSection;
  }

  // Risk factors and potential issues
  const riskSection = buildRiskSection(results);
  if (riskSection) {
    comment += riskSection;
  }

  // Confidence metrics
  const confidenceSection = buildConfidenceSection(results);
  if (confidenceSection) {
    comment += confidenceSection;
  }

  // Footer
  comment += `---\n*AI pre-review analysis • Confidence: ${confidenceTier}*`;

  return comment;
}

function getConfidenceTier(results) {
  const metrics = results.confidence_metrics || {};
  const scores = Object.values(metrics);
  
  if (scores.includes('VERY HIGH') || scores.filter(s => s === 'HIGH').length >= 2) {
    return 'VERY HIGH';
  }
  if (scores.includes('HIGH') || scores.filter(s => s === 'MEDIUM').length >= 2) {
    return 'HIGH';
  }
  if (scores.includes('MEDIUM')) {
    return 'MEDIUM';
  }
  if (scores.includes('LOW')) {
    return 'LOW';
  }
  return 'VERY LOW';
}

function getRiskLevel(riskLevel) {
  const levels = {
    'CRITICAL': 'CRITICAL',
    'HIGH': 'HIGH',
    'MEDIUM': 'MEDIUM', 
    'LOW': 'LOW',
    'MINIMAL': 'MINIMAL'
  };
  return levels[riskLevel] || 'UNKNOWN';
}

function buildSummarySection(results) {
  const summary = results.ai_analysis.summary;
  const shortSummary = summary.length > 200 ? summary.substring(0, 200) + '...' : summary;
  
  return `**Change Summary:**\n${shortSummary}\n\n`;
}

function buildCategoriesSection(results) {
  const categories = results.file_categories;
  if (!categories || Object.keys(categories).length === 0) return '';
  
  const categoryLabels = {
    'ui': 'UI Components',
    'api': 'API/Backend', 
    'database': 'Database',
    'config': 'Configuration',
    'test': 'Testing',
    'documentation': 'Documentation',
    'other': 'Other'
  };
  
  const categoryBreakdown = Object.entries(categories)
    .filter(([_, files]) => files && files.length > 0)
    .map(([category, files]) => `${categoryLabels[category] || 'Other'}: ${files.length}`)
    .join(' | ');
  
  return categoryBreakdown ? `**File Categories:** ${categoryBreakdown}\n\n` : '';
}

function buildImpactSection(results) {
  const analysis = results.ai_analysis;
  let section = '';
  
  const hasBusinessImpact = analysis.business_impact && 
    analysis.business_impact !== 'Unknown' && 
    analysis.business_impact !== 'See summary above';
    
  if (hasBusinessImpact) {
    const businessImpact = analysis.business_impact.length > 150 
      ? analysis.business_impact.substring(0, 150) + '...' 
      : analysis.business_impact;
    section += `**Business Impact:** ${businessImpact}\n\n`;
  }
  
  return section;
}

function buildRiskSection(results) {
  let section = '';
  
  // Potential issues
  const analysis = results.ai_analysis;
  const hasPotentialIssues = analysis.potential_issues && 
    analysis.potential_issues !== 'Unknown' && 
    analysis.potential_issues !== 'Manual review recommended';
  
  if (hasPotentialIssues) {
    const potentialIssues = analysis.potential_issues.length > 150 
      ? analysis.potential_issues.substring(0, 150) + '...' 
      : analysis.potential_issues;
    section += `**Potential Issues:** ${potentialIssues}\n\n`;
  }
  
  // Risk factors
  if (results.risk_factors && results.risk_factors.length > 0) {
    section += `**Risk Factors:**\n`;
    results.risk_factors.slice(0, 3).forEach(factor => {
      section += `- ${factor}\n`;
    });
    if (results.risk_factors.length > 3) {
      section += `- ... and ${results.risk_factors.length - 3} more\n`;
    }
    section += `\n`;
  }
  
  return section;
}

function buildConfidenceSection(results) {
  const metrics = results.confidence_metrics;
  if (!metrics) return '';
  
  let section = `### Analysis Confidence\n`;
  section += `| Metric | Level | Description |\n`;
  section += `|--------|-------|-------------|\n`;
  
  const metricDescriptions = {
    analysis_confidence: 'Overall analysis accuracy',
    prediction_reliability: 'Risk prediction reliability',
    completeness: 'Analysis coverage completeness'
  };
  
  Object.entries(metrics).forEach(([metric, level]) => {
    const desc = metricDescriptions[metric] || 'Analysis metric';
    const displayName = metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    section += `| ${displayName} | ${level} | ${desc} |\n`;
  });
  
  section += `\n`;
  return section;
}
