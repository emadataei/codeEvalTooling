const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');
const fs = require('fs');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping dependency graph comment');
    return;
  }

  const results = loadResults('dependency-graph-results.json', { 
    changes: [],
    total_files_analyzed: 0,
    graph_generated: false,
    circular_dependencies: [],
    high_impact_changes: []
  });

  const comment = buildComment(results);
  
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'Dependency Graph',
    `dependency-graph-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Dependency graph comment posted/updated successfully');
};

function buildComment(results) {
  let comment = `## Dependency Analysis\n\n`;
  
  // Overview metrics
  comment += `**Analysis Summary:** ${results.total_files_analyzed} files | ${results.changes.length} changes\n\n`;

  // High-impact changes in structured table
  if (results.high_impact_changes && results.high_impact_changes.length > 0) {
    comment += `### High Impact Changes\n`;
    comment += `| Type | File | Dependencies Affected |\n`;
    comment += `|------|------|-----------------------|\n`;
    results.high_impact_changes.slice(0, 3).forEach(change => {
      const changeType = getChangeType(change.change_type);
      comment += `| ${changeType} | \`${change.file_name}\` | ${change.impact_score} |\n`;
    });
    comment += `\n`;
  }

  // Circular dependencies with clear warning
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `### ⚠ Circular Dependencies Detected\n`;
    comment += `\`\`\`\n`;
    results.circular_dependencies.slice(0, 2).forEach(cycle => {
      comment += `${cycle.join(' → ')}\n`;
    });
    comment += `\`\`\`\n\n`;
  }

  // Change summary - organized by type
  const changesByType = groupChangesByType(results.changes);
  if (Object.keys(changesByType).length > 0) {
    comment += `**Change Breakdown:**\n`;
    Object.entries(changesByType).forEach(([type, changes]) => {
      comment += `- ${getChangeType(type)}: ${changes.length}\n`;
    });
    comment += `\n`;
  }

  // Interactive graph reference
  if (fs.existsSync('dependency_graph.html')) {
    comment += `📊 **[View Interactive Dependency Graph](./dependency_graph.html)**\n\n`;
  }

  // Recommendations with action items
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `> **Action Required:** Resolve circular dependencies before merge\n`;
  }
  if (results.high_impact_changes && results.high_impact_changes.length > 3) {
    comment += `> **Consider:** Breaking this PR into smaller, focused changes\n`;
  }

  // Footer
  comment += `\n---\n*AI-generated analysis for review triage*`;

  return comment;
}

function getChangeType(changeType) {
  const types = {
    'added': 'ADDED',
    'modified': 'MODIFIED',
    'deleted': 'DELETED',
    'renamed': 'RENAMED'
  };
  return types[changeType] || 'CHANGED';
}

function groupChangesByType(changes) {
  const grouped = {};
  changes.forEach(change => {
    if (!grouped[change.change_type]) {
      grouped[change.change_type] = [];
    }
    grouped[change.change_type].push(change);
  });
  return grouped;
}
