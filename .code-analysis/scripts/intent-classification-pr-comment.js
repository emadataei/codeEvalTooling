const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping intent classification comment');
    return;
  }

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

  const comment = buildComment(results);
  
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'Intent Classification',
    `intent-classification-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Intent classification comment posted/updated successfully');
};

function buildComment(results) {
  let comment = `## Intent Classification\n\n`;
  
  // Primary intent - concise format
  const confidenceLevel = getConfidenceLevel(results.confidence);
  comment += `**${results.primary_intent.toUpperCase()}** (${confidenceLevel}: ${Math.round(results.confidence * 100)}%)\n\n`;
  
  // Secondary intents - compact format
  if (results.secondary_intents && results.secondary_intents.length > 0) {
    comment += `**Secondary:** `;
    const secondaryList = results.secondary_intents.slice(0, 2)
      .map(([intent, conf]) => `${intent.toUpperCase()} (${Math.round(conf * 100)}%)`)
      .join(', ');
    comment += secondaryList + `\n\n`;
  }
  
  // Key metrics - one line
  const fileChanges = results.file_changes_summary;
  comment += `**Scope:** ${fileChanges.total_files} files, +${fileChanges.total_lines_added}/-${fileChanges.total_lines_removed} lines\n\n`;
  
  // Areas - compact format
  if (results.affected_areas && results.affected_areas.length > 0) {
    const areas = results.affected_areas.join(', ');
    comment += `**Areas:** ${areas}\n\n`;
  }

  // Only show reasoning if it's meaningful and short
  if (shouldShowReasoning(results.reasoning)) {
    const shortReason = results.reasoning.length > 120 
      ? results.reasoning.substring(0, 120) + '...' 
      : results.reasoning;
    comment += `**Why:** ${shortReason}\n\n`;
  }

  // Low confidence warning
  if (results.confidence < 0.6) {
    comment += `**Note:** Low confidence - add more descriptive PR title/description\n\n`;
  }

  return comment;
}

function getConfidenceLevel(confidence) {
  if (confidence > 0.8) return 'HIGH';
  if (confidence > 0.5) return 'MEDIUM';
  return 'LOW';
}

function shouldShowReasoning(reasoning) {
  return reasoning && 
         reasoning !== 'Intent classification analysis failed' &&
         reasoning !== 'Rule-based classification based on PR title pattern' &&
         reasoning.length > 20;
}
