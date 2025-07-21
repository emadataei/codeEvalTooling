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
  let comment = `## Dependencies\n\n`;
  
  // Quick overview
  comment += `**${results.total_files_analyzed}** files analyzed | **${results.changes.length}** changes\n\n`;

  // High-impact changes only
  if (results.high_impact_changes && results.high_impact_changes.length > 0) {
    comment += `**High Impact:**\n`;
    results.high_impact_changes.slice(0, 3).forEach(change => {
      const changeType = getChangeType(change.change_type);
      comment += `**${changeType}** ${change.file_name} (${change.impact_score} deps affected)\n`;
    });
    comment += `\n`;
  }

  // Circular dependencies warning
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `**Circular Dependencies:**\n`;
    results.circular_dependencies.slice(0, 2).forEach(cycle => {
      comment += `CYCLE: ${cycle.join(' → ')}\n`;
    });
    comment += `\n`;
  }

  // Change summary - compact
  const changesByType = groupChangesByType(results.changes);
  if (Object.keys(changesByType).length > 0) {
    const summary = Object.entries(changesByType)
      .map(([type, changes]) => `${getChangeType(type)} ${changes.length} ${type}`)
      .join(', ');
    comment += `**Changes:** ${summary}\n\n`;
  }

  // Interactive graph if available
  if (fs.existsSync('dependency_graph.html')) {
    comment += `[View Interactive Graph](./dependency_graph.html)\n\n`;
  }

  // Quick recommendations
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `**Recommendation:** Fix circular dependencies before merge\n`;
  }
  if (results.high_impact_changes && results.high_impact_changes.length > 3) {
    comment += `**Recommendation:** Consider breaking into smaller changes\n`;
  }

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
