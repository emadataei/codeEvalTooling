const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping comment');
    return;
  }
  
  const results = loadResults('cognitive-analysis-results.json', { 
    tier: 0, 
    total_score: 0, 
    reasoning: 'Failed to load results' 
  });
  
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
  
  // AST Analysis Details
  if (results.ast_metrics && results.ast_metrics.summary) {
    const summary = results.ast_metrics.summary;
    comment += `### AST Analysis Summary\n\n`;
    comment += `| Metric | Value | Impact |\n`;
    comment += `|--------|-------|--------|\n`;
    comment += `| Total Cyclomatic Complexity | ${summary.total_cyclomatic_complexity} | ${summary.total_cyclomatic_complexity > 20 ? 'High' : summary.total_cyclomatic_complexity > 10 ? 'Medium' : 'Low'} |\n`;
    comment += `| Maximum Nesting Depth | ${summary.max_nesting_depth} | ${summary.max_nesting_depth > 4 ? 'High' : summary.max_nesting_depth > 2 ? 'Medium' : 'Low'} |\n`;
    comment += `| Total Functions | ${summary.total_functions} | ${summary.total_functions > 10 ? 'High' : summary.total_functions > 5 ? 'Medium' : 'Low'} |\n`;
    comment += `| Total Control Structures | ${summary.total_control_structures} | ${summary.total_control_structures > 30 ? 'High' : summary.total_control_structures > 15 ? 'Medium' : 'Low'} |\n`;
    comment += `\n`;
    
    // Complex files breakdown
    if (summary.complex_files && summary.complex_files.length > 0) {
      comment += `### Complex Files Requiring Attention\n\n`;
      summary.complex_files.forEach(file => {
        comment += `**${file.path}** (Score: ${file.score})\n`;
        comment += `- ${file.main_issues.join('\n- ')}\n\n`;
      });
    }
    
    // Per-file breakdown for detailed analysis
    if (results.ast_metrics.files && Object.keys(results.ast_metrics.files).length > 0) {
      comment += `<details>\n<summary>Detailed File Analysis</summary>\n\n`;
      
      Object.values(results.ast_metrics.files).forEach(file => {
        comment += `**${file.path}** (${file.language})\n`;
        comment += `- Complexity Score: ${file.total_score}\n`;
        comment += `- Cyclomatic Complexity: ${file.cyclomatic_complexity}\n`;
        comment += `- Nesting Depth: ${file.nesting_depth}\n`;
        comment += `- Functions: ${file.function_count}\n`;
        comment += `- Control Structures: ${file.control_structures}\n`;
        if (file.function_length_penalty > 0) {
          comment += `- Function Length Penalty: +${file.function_length_penalty}\n`;
        }
        if (file.file_size_penalty > 0) {
          comment += `- File Size Penalty: +${file.file_size_penalty}\n`;
        }
        comment += `\n`;
      });
      
      comment += `</details>\n\n`;
    }
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
  try {
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      comment, 
      'Cognitive Complexity Analysis',  // identifier to find existing comments
      'COGNITIVE_ANALYSIS_COMMENT'  // unique comment ID for reliable matching
    );
  } catch (error) {
    console.error('Error creating or updating cognitive analysis comment:', error);
    throw error;
  }
};
