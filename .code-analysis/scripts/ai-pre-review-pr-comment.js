const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping AI pre-review comment');
    return;
  }
  
  // Load AI pre-review results
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
    }
  });
  
  // Build the comment
  let comment = `## AI Pre-Review Analysis\n\n`;
  comment += `**Risk Level:** ${results.risk_level} | **Files:** ${results.file_count}\n\n`;
  
  // Plain-English Summary (truncated)
  const summary = results.ai_analysis.summary;
  const shortSummary = summary.length > 200 ? summary.substring(0, 200) + '...' : summary;
  comment += `**What This Change Does:**\n${shortSummary}\n\n`;
  
  // File categories breakdown (inline)
  const categories = results.file_categories;
  const categoryLabels = {
    'ui': 'UI',
    'api': 'API', 
    'database': 'DB',
    'config': 'Config',
    'test': 'Test',
    'documentation': 'Docs',
    'other': 'Other'
  };
  
  const nonEmptyCategories = Object.entries(categories)
    .filter(([_, files]) => files && files.length > 0)
    .map(([category, files]) => `${categoryLabels[category] || 'Other'}: ${files.length}`)
    .join(' | ');
  
  if (nonEmptyCategories) {
    comment += `**File Types:** ${nonEmptyCategories}\n\n`;
  }
  
  // Only show key sections if they have meaningful content
  const hasBusinessImpact = results.ai_analysis.business_impact && 
    results.ai_analysis.business_impact !== 'Unknown' && 
    results.ai_analysis.business_impact !== 'See summary above';
    
  const hasPotentialIssues = results.ai_analysis.potential_issues && 
    results.ai_analysis.potential_issues !== 'Unknown' && 
    results.ai_analysis.potential_issues !== 'Manual review recommended';
  
  if (hasBusinessImpact) {
    const businessImpact = results.ai_analysis.business_impact;
    const shortBusinessImpact = businessImpact.length > 150 ? businessImpact.substring(0, 150) + '...' : businessImpact;
    comment += `**Business Impact:** ${shortBusinessImpact}\n\n`;
  }
  
  if (hasPotentialIssues) {
    const potentialIssues = results.ai_analysis.potential_issues;
    const shortPotentialIssues = potentialIssues.length > 150 ? potentialIssues.substring(0, 150) + '...' : potentialIssues;
    comment += `**Things to Watch For:** ${shortPotentialIssues}\n\n`;
  }
  
  // Risk factors (only if any)
  if (results.risk_factors && results.risk_factors.length > 0) {
    comment += `**Risk Factors:** ${results.risk_factors.length} detected\n\n`;
  }
  
  // Minimal footer
  comment += `---\n*AI-generated analysis for review triage*`;
  
  // Create or update the comment
  try {
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      comment, 
      'AI Pre-Review Analysis',  // identifier to find existing comments
      'AI_PRE_REVIEW_COMMENT'   // unique comment ID for reliable matching
    );
  } catch (error) {
    console.error('Error creating or updating AI pre-review comment:', error);
    throw error;
  }
};
