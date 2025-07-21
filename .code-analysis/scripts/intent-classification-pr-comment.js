const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping intent classification comment');
    return;
  }
  
  // Load intent classification results
  const results = loadResults('intent-classification-results.json', { 
    primary_intent: 'maintenance',
    confidence: 0.3,
    secondary_intents: [],
    reasoning: 'Intent classification analysis failed',
    affected_areas: ['unknown'],
    business_impact: 'Unable to determine without AI analysis',
    technical_details: 'Manual review required for detailed analysis',
    file_changes_summary: {
      total_files: 0,
      files_added: 0,
      files_modified: 0,
      files_deleted: 0,
      total_lines_added: 0,
      total_lines_removed: 0
    }
  });
  
  // Build the comment
  let comment = `## 🎯 Intent Classification Analysis\n\n`;
  
  // Primary intent with confidence
  const confidenceEmoji = results.confidence > 0.8 ? '🟢' : results.confidence > 0.5 ? '🟡' : '🔴';
  const intentEmoji = getIntentEmoji(results.primary_intent);
  comment += `${intentEmoji} **Primary Intent:** ${results.primary_intent.toUpperCase()} ${confidenceEmoji} *${Math.round(results.confidence * 100)}% confidence*\n\n`;
  
  // Secondary intents if available
  if (results.secondary_intents && results.secondary_intents.length > 0) {
    comment += `**Secondary Patterns:**\n`;
    results.secondary_intents.slice(0, 2).forEach(([intent, confidence]) => {
      const secEmoji = getIntentEmoji(intent);
      comment += `${secEmoji} ${intent.toUpperCase()} (${Math.round(confidence * 100)}%)\n`;
    });
    comment += `\n`;
  }
  
  // Affected areas
  if (results.affected_areas && results.affected_areas.length > 0) {
    const areaEmojis = {
      'ui': '🎨',
      'api': '🔌',
      'database': '🗄️',
      'authentication': '🔐',
      'testing': '🧪',
      'configuration': '⚙️',
      'documentation': '📚'
    };
    
    const areas = results.affected_areas.map(area => 
      `${areaEmojis[area] || '📁'} ${area}`
    ).join(', ');
    comment += `**Affected Areas:** ${areas}\n\n`;
  }
  
  // File changes summary
  const fileChanges = results.file_changes_summary;
  const totalChanges = fileChanges.total_lines_added + fileChanges.total_lines_removed;
  if (totalChanges > 0) {
    comment += `**Change Scope:** ${fileChanges.total_files} files, `;
    comment += `+${fileChanges.total_lines_added}/-${fileChanges.total_lines_removed} lines\n\n`;
  }
  
  // Reasoning (truncated for readability)
  if (results.reasoning && results.reasoning !== 'Intent classification analysis failed') {
    const reasoning = results.reasoning.length > 300 
      ? results.reasoning.substring(0, 300) + '...' 
      : results.reasoning;
    comment += `**Analysis Reasoning:**\n${reasoning}\n\n`;
  }
  
  // Business impact if meaningful
  if (results.business_impact && 
      results.business_impact !== 'Unable to determine without AI analysis' &&
      results.business_impact !== 'Unknown') {
    const impact = results.business_impact.length > 200 
      ? results.business_impact.substring(0, 200) + '...' 
      : results.business_impact;
    comment += `**Business Impact:**\n${impact}\n\n`;
  }
  
  // Technical details if available
  if (results.technical_details && 
      results.technical_details !== 'Manual review required for detailed analysis' &&
      results.technical_details !== 'Unknown') {
    const details = results.technical_details.length > 200 
      ? results.technical_details.substring(0, 200) + '...' 
      : results.technical_details;
    comment += `**Technical Details:**\n${details}\n\n`;
  }
  
  // Add helpful context for low confidence
  if (results.confidence < 0.6) {
    comment += `⚠️ *Low confidence classification. Consider adding more descriptive PR title/description for better analysis.*\n\n`;
  }
  
  comment += `<details>\n<summary>📊 View Detailed Metrics</summary>\n\n`;
  comment += `**Files by Change Type:**\n`;
  comment += `- Added: ${fileChanges.files_added}\n`;
  comment += `- Modified: ${fileChanges.files_modified}\n`;
  comment += `- Deleted: ${fileChanges.files_deleted}\n\n`;
  
  if (results.secondary_intents && results.secondary_intents.length > 0) {
    comment += `**All Secondary Intents:**\n`;
    results.secondary_intents.forEach(([intent, confidence]) => {
      comment += `- ${intent.toUpperCase()}: ${Math.round(confidence * 100)}%\n`;
    });
  }
  comment += `\n</details>`;
  
  // Post or update the comment
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    '🎯 Intent Classification Analysis',
    `intent-classification-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Intent classification comment posted/updated successfully');
};

function getIntentEmoji(intent) {
  const emojis = {
    'feature': '✨',
    'bugfix': '🐛',
    'refactor': '♻️',
    'performance': '⚡',
    'security': '🔒',
    'documentation': '📚',
    'testing': '🧪',
    'configuration': '⚙️',
    'dependency': '📦',
    'maintenance': '🔧',
    'style': '💄',
    'architecture': '🏗️'
  };
  return emojis[intent] || '📝';
}
