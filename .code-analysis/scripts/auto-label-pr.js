const fs = require('fs');
const { getPRNumber, loadResults, setLabels } = require('./pr-comment-utils');

/**
 * Automatically set PR labels based on analysis results
 */
async function autoLabelPR({ github, context }) {
  const prNumber = getPRNumber(context);
  if (!prNumber) {
    console.log('No PR number found, skipping auto-labeling');
    return;
  }

  console.log(`Setting automatic labels for PR #${prNumber}`);
  
  const labels = new Set();
  
  // Collect labels from different analysis sources
  await addIntentLabels(labels);
  await addRiskLabels(labels);
  await addQualityLabels(labels);
  await addSizeLabels(labels, github, context, prNumber);
  await addTechnologyLabels(labels, github, context, prNumber);
  addVisualLabels(labels);
  addDocumentationLabels(labels);

  // Apply labels
  const finalLabels = Array.from(labels).filter(label => label && label.trim());
  
  if (finalLabels.length > 0) {
    console.log(`Setting labels: ${finalLabels.join(', ')}`);
    await setLabels(github, context, prNumber, finalLabels);
    console.log('✅ Labels set successfully');
  } else {
    console.log('No labels to set');
  }

  return finalLabels;
}

/**
 * Add intent-based labels
 */
async function addIntentLabels(labels) {
  try {
    // Check multiple possible locations for intent results
    const locations = [
      '.code-analysis/outputs/intent-classification-results.json',
      'intent_classification.json'
    ];
    
    let intentResults = null;
    for (const location of locations) {
      try {
        intentResults = loadResults(location);
        if (intentResults.primary_intent) break;
      } catch (locationError) {
        console.log(`Could not load from ${location}:`, locationError.message);
      }
    }
    
    if (intentResults && intentResults.primary_intent) {
      const intentLabel = getIntentLabel(intentResults.primary_intent);
      if (intentLabel) labels.add(intentLabel);
      
      // Add confidence indicator
      if (intentResults.confidence > 0.8) {
        labels.add('high-confidence');
      } else if (intentResults.confidence < 0.5) {
        labels.add('needs-review');
      }
    }
  } catch (error) {
    console.log('Intent classification results not available:', error.message);
  }
}

/**
 * Add risk-based labels
 */
async function addRiskLabels(labels) {
  try {
    // Check multiple possible locations for risk results
    const locations = [
      '.code-analysis/outputs/impact-prediction-results.json',
      'impact_prediction.json'
    ];
    
    let impactResults = null;
    for (const location of locations) {
      try {
        impactResults = loadResults(location);
        if (impactResults.overall_risk_score !== undefined) break;
      } catch (locationError) {
        console.log(`Could not load from ${location}:`, locationError.message);
      }
    }
    
    if (impactResults && impactResults.overall_risk_score !== undefined) {
      const riskLabel = getRiskLabel(impactResults.overall_risk_score);
      if (riskLabel) labels.add(riskLabel);
    }
  } catch (error) {
    console.log('Impact prediction results not available:', error.message);
  }
}

/**
 * Add quality gate labels
 */
async function addQualityLabels(labels) {
  try {
    const qualityResults = findQualityResults();
    if (!qualityResults) return;
    
    addQualityScoreLabels(labels, qualityResults);
    addQualityIssueLabels(labels, qualityResults);
  } catch (error) {
    console.log('Quality gate results not available:', error.message);
  }
}

/**
 * Find quality results from multiple locations
 */
function findQualityResults() {
  const locations = [
    '.code-analysis/outputs/quality-gate-results.json',
    'quality-gate-results.json'
  ];
  
  for (const location of locations) {
    try {
      const results = loadResults(location);
      if (results.overall_score !== undefined) return results;
    } catch (locationError) {
      console.log(`Could not load from ${location}:`, locationError.message);
    }
  }
  return null;
}

/**
 * Add quality score labels
 */
function addQualityScoreLabels(labels, qualityResults) {
  if (qualityResults.overall_score === undefined) return;
  
  if (qualityResults.overall_score >= 8) {
    labels.add('✅ high-quality');
  } else if (qualityResults.overall_score >= 6) {
    labels.add('🟡 needs-improvement');
  } else {
    labels.add('🔴 quality-issues');
  }
}

/**
 * Add quality issue labels
 */
function addQualityIssueLabels(labels, qualityResults) {
  if (!qualityResults.issues || qualityResults.issues.length === 0) return;
  
  const hasSecurityIssues = qualityResults.issues.some(issue => 
    issue.type && issue.type.toLowerCase().includes('security')
  );
  if (hasSecurityIssues) {
    labels.add('🔒 security-review');
  }
  
  const hasPerformanceIssues = qualityResults.issues.some(issue => 
    issue.type && issue.type.toLowerCase().includes('performance')
  );
  if (hasPerformanceIssues) {
    labels.add('⚡ performance-review');
  }
}

/**
 * Add size-based labels
 */
async function addSizeLabels(labels, github, context, prNumber) {
  try {
    const prStats = await getPRStats(github, context, prNumber);
    const sizeLabel = getSizeLabel(prStats);
    if (sizeLabel) labels.add(sizeLabel);
  } catch (error) {
    console.log('Could not get PR stats for size labeling:', error.message);
  }
}

/**
 * Add technology-based labels
 */
async function addTechnologyLabels(labels, github, context, prNumber) {
  try {
    const changedFiles = await getChangedFiles(github, context, prNumber);
    const techLabels = getTechnologyLabels(changedFiles);
    techLabels.forEach(label => labels.add(label));
  } catch (error) {
    console.log('Could not get changed files for technology labeling:', error.message);
  }
}

/**
 * Add visual analysis labels
 */
function addVisualLabels(labels) {
  try {
    const hasVisuals = checkForGeneratedVisuals();
    if (hasVisuals.length > 0) {
      labels.add('📊-visuals-generated');
      
      // Specific visual types
      if (hasVisuals.includes('impact_heatmap.png')) labels.add('impact-analysis');
      if (hasVisuals.includes('dependency_graph_pr.png')) labels.add('dependency-changes');
      if (hasVisuals.includes('story_arc.gif')) labels.add('animated-summary');
    }
  } catch (error) {
    console.log('Could not check for generated visuals:', error.message);
  }
}

/**
 * Add documentation labels
 */
function addDocumentationLabels(labels) {
  try {
    const docsContent = fs.readFileSync('.code-analysis/outputs/documentation_suggestions.md', 'utf8');
    if (docsContent.includes('Missing documentation') || docsContent.includes('documentation gaps')) {
      labels.add('docs-needed');
    }
    if (docsContent.includes('Well documented') || docsContent.includes('comprehensive')) {
      labels.add('well-documented');
    }
  } catch (error) {
    console.log('Documentation analysis not available:', error.message);
  }
}

/**
 * Map intent to label
 */
function getIntentLabel(intent) {
  const labelMap = {
    'feature': '✨ feature',
    'bug': '🐛 bug',
    'bugfix': '🐛 bug',
    'refactor': '♻️ refactor',
    'documentation': '📚 documentation',
    'ui': '🎨 ui',
    'api': '🔧 api',
    'infrastructure': '🏗️ infrastructure',
    'infra': '🏗️ infrastructure',
    'test': '🧪 test',
    'testing': '🧪 test',
    'security': '🔒 security',
    'performance': '⚡ performance',
    'maintenance': '🔧 maintenance',
    'style': '💄 style',
    'config': '⚙️ config',
    'build': '🏗️ build'
  };
  
  return labelMap[intent.toLowerCase()];
}

/**
 * Map risk score to label
 */
function getRiskLabel(riskScore) {
  if (riskScore < 0.2) return '🟢 low-risk';
  if (riskScore < 0.5) return '🟡 medium-risk';
  if (riskScore < 0.8) return '🟠 high-risk';
  return '🔴 critical-risk';
}

/**
 * Get PR size label based on stats
 */
function getSizeLabel(stats) {
  const totalChanges = stats.additions + stats.deletions;
  
  if (totalChanges < 50) return 'size/XS';
  if (totalChanges < 200) return 'size/S';
  if (totalChanges < 500) return 'size/M';
  if (totalChanges < 1000) return 'size/L';
  return 'size/XL';
}

/**
 * Get technology labels based on file extensions
 */
function getTechnologyLabels(files) {
  const labels = new Set();
  
  files.forEach(file => {
    const ext = file.split('.').pop().toLowerCase();
    const path = file.toLowerCase();
    
    // Frontend
    if (['tsx', 'jsx'].includes(ext)) labels.add('react');
    if (['vue'].includes(ext)) labels.add('vue');
    if (['js', 'ts'].includes(ext) && (path.includes('frontend') || path.includes('client'))) {
      labels.add('frontend');
    }
    
    // Backend
    if (['py'].includes(ext)) labels.add('python');
    if (['js', 'ts'].includes(ext) && (path.includes('api') || path.includes('server'))) {
      labels.add('backend');
    }
    
    // Infrastructure
    if (['yml', 'yaml'].includes(ext) && path.includes('.github')) labels.add('ci/cd');
    if (['dockerfile', 'docker-compose'].some(d => path.includes(d))) labels.add('docker');
    
    // Documentation
    if (['md'].includes(ext)) labels.add('documentation');
    
    // Configuration
    if (['json', 'yaml', 'yml', 'toml', 'ini'].includes(ext)) labels.add('config');
  });
  
  return Array.from(labels);
}

/**
 * Get PR statistics
 */
async function getPRStats(github, context, prNumber) {
  const { data: pr } = await github.rest.pulls.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: prNumber
  });
  
  return {
    additions: pr.additions,
    deletions: pr.deletions,
    changedFiles: pr.changed_files
  };
}

/**
 * Get list of changed files
 */
async function getChangedFiles(github, context, prNumber) {
  const { data: files } = await github.rest.pulls.listFiles({
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: prNumber
  });
  
  return files.map(file => file.filename);
}

/**
 * Check what visual files were generated
 */
function checkForGeneratedVisuals() {
  const visualFiles = [
    'change_heatmap.png',
    'impact_heatmap.png', 
    'development_flow.png',
    'story_arc.gif',
    'dependency_graph_pr.png'
  ];
  
  const outputsDir = '.code-analysis/outputs';
  const rootDir = '.';
  
  const foundVisuals = [];
  
  visualFiles.forEach(file => {
    if (fs.existsSync(`${outputsDir}/${file}`) || fs.existsSync(`${rootDir}/${file}`)) {
      foundVisuals.push(file);
    }
  });
  
  return foundVisuals;
}

module.exports = autoLabelPR;
