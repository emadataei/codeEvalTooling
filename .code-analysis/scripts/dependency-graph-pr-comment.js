const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');
const fs = require('fs');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping dependency graph comment');
    return;
  }
  
  // Load dependency graph results
  const results = loadResults('dependency-graph-results.json', { 
    changes: [],
    total_files_analyzed: 0,
    graph_generated: false,
    circular_dependencies: [],
    high_impact_changes: []
  });
  
  // Check if HTML graph file exists
  const htmlGraphExists = fs.existsSync('dependency_graph.html');
  
  // Build the comment
  let comment = `## Dependency Graph Analysis\n\n`;
  
  // Overview stats
  comment += `**Files Analyzed:** ${results.total_files_analyzed} | `;
  comment += `**Changes Detected:** ${results.changes.length}\n\n`;
  
  // High-impact changes
  if (results.high_impact_changes && results.high_impact_changes.length > 0) {
    comment += `**High-Impact Changes:**\n`;
    results.high_impact_changes.slice(0, 3).forEach(change => {
      comment += `**${change.file_name}** (${change.change_type.toUpperCase()})\n`;
      comment += `   Impact Score: ${change.impact_score} dependencies affected\n\n`;
    });
  }
  
  // Circular dependencies warning
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `**Circular Dependencies Detected:**\n`;
    results.circular_dependencies.slice(0, 3).forEach(cycle => {
      comment += `${cycle.join(' → ')}\n`;
    });
    comment += `\n`;
  }
  
  // Interactive graph link
  if (htmlGraphExists) {
    comment += `**Interactive Visualization:**\n`;
    comment += `[View Dependency Graph](./dependency_graph.html) - Download and open in browser\n\n`;
  }
  
  // Change summary by type
  const changesByType = groupChangesByType(results.changes);
  if (Object.keys(changesByType).length > 0) {
    comment += `**Changes by Type:**\n`;
    Object.entries(changesByType).forEach(([type, changes]) => {
      comment += `**${type.toUpperCase()}**: ${changes.length} files\n`;
    });
    comment += `\n`;
  }
  
  // Architectural insights
  if (results.changes.length > 0) {
    const affectedModules = extractAffectedModules(results.changes);
    if (affectedModules.length > 0) {
      comment += `**Affected Modules:**\n`;
      affectedModules.slice(0, 5).forEach(module => {
        comment += `${module}\n`;
      });
      if (affectedModules.length > 5) {
        comment += `   ... and ${affectedModules.length - 5} more\n`;
      }
      comment += `\n`;
    }
  }
  
  // Detailed breakdown
  comment += `<details>\n<summary>View Detailed Changes</summary>\n\n`;
  
  if (results.changes.length > 0) {
    comment += `**All File Changes:**\n`;
    results.changes.forEach(change => {
      comment += `**${change.file_path}** (${change.change_type.toUpperCase()})\n`;
      
      if (change.dependencies_before && change.dependencies_after) {
        const depsBefore = change.dependencies_before.length;
        const depsAfter = change.dependencies_after.length;
        const depChange = depsAfter - depsBefore;
        
        if (depChange !== 0) {
          const changeSymbol = depChange > 0 ? '+' : '';
          comment += `   Dependencies: ${depsBefore} → ${depsAfter} (${changeSymbol}${depChange})\n`;
        }
      }
      
      if (change.impact_score > 0) {
        comment += `   Impact Score: ${change.impact_score}\n`;
      }
      
      comment += `\n`;
    });
  } else {
    comment += `No dependency changes detected in this PR.\n\n`;
  }
  
  // Graph generation status
  comment += `**Graph Generation:**\n`;
  if (results.graph_generated) {
    comment += `Dependency graph generated successfully\n`;
    if (htmlGraphExists) {
      comment += `Interactive HTML visualization available\n`;
    }
  } else {
    comment += `Graph generation failed or skipped\n`;
  }
  
  comment += `\n</details>`;
  
  // Recommendations based on findings
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    comment += `\n**Recommendations:**\n`;
    comment += `**Circular Dependencies**: Consider refactoring to break cycles\n`;
  }
  
  if (results.high_impact_changes && results.high_impact_changes.length > 3) {
    comment += `**High Impact**: Many files affected - consider breaking into smaller changes\n`;
  }
  
  if (results.changes.length === 0) {
    comment += `\n**Good news!** No significant dependency changes detected.`;
  }
  
  // Post or update the comment
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    'Dependency Graph Analysis',
    `dependency-graph-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Dependency graph comment posted/updated successfully');
};

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

function extractAffectedModules(changes) {
  const modules = new Set();
  changes.forEach(change => {
    const pathParts = change.file_path.split('/');
    // Extract likely module names from paths
    if (pathParts.length > 1) {
      // Get the first directory as potential module
      modules.add(pathParts[0]);
      // Also check for src/components, src/api patterns
      if (pathParts[0] === 'src' && pathParts.length > 2) {
        modules.add(`${pathParts[0]}/${pathParts[1]}`);
      }
    }
  });
  return Array.from(modules).filter(module => module !== '.' && module !== '..');
}
