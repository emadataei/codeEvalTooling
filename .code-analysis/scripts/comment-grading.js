/**
 * Shared grading utilities for PR comment consistency
 */

/**
 * Grade scales for different analysis types
 */
const GRADE_SCALES = {
  intent: {
    A: { min: 0.8, label: 'CLEAR', status: 'PASS' },
    B: { min: 0.6, label: 'GOOD', status: 'PASS' },
    C: { min: 0.4, label: 'UNCLEAR', status: 'REVIEW' },
    D: { min: 0.2, label: 'VAGUE', status: 'REVIEW' },
    F: { min: 0.0, label: 'UNKNOWN', status: 'BLOCK' }
  },
  risk: {
    A: { max: 0.2, label: 'LOW RISK', status: 'PASS' },
    B: { max: 0.4, label: 'MANAGEABLE', status: 'PASS' },
    C: { max: 0.6, label: 'MODERATE', status: 'REVIEW' },
    D: { max: 0.8, label: 'HIGH RISK', status: 'REVIEW' },
    F: { max: 1.0, label: 'CRITICAL', status: 'BLOCK' }
  },
  complexity: {
    A: { max: 35, label: 'AUTO-MERGE', status: 'PASS' },
    B: { max: 50, label: 'STANDARD', status: 'PASS' },
    C: { max: 65, label: 'COMPLEX', status: 'REVIEW' },
    D: { max: 80, label: 'EXPERT NEEDED', status: 'REVIEW' },
    F: { max: 100, label: 'CRITICAL REVIEW', status: 'BLOCK' }
  },
  dependencies: {
    A: { factors: ['no_circular', 'low_impact'], label: 'CLEAN', status: 'PASS' },
    B: { factors: ['minor_issues'], label: 'MINOR ISSUES', status: 'PASS' },
    C: { factors: ['some_concerns'], label: 'CONCERNS', status: 'REVIEW' },
    D: { factors: ['significant_issues'], label: 'ISSUES', status: 'REVIEW' },
    F: { factors: ['circular_deps', 'critical_issues'], label: 'CRITICAL', status: 'BLOCK' }
  }
};

/**
 * Calculate grade for intent classification
 * @param {number} confidence - Confidence score (0-1)
 * @returns {Object} Grade information
 */
function gradeIntentClassification(confidence) {
  const scale = GRADE_SCALES.intent;
  
  for (const [grade, criteria] of Object.entries(scale)) {
    if (confidence >= criteria.min) {
      return {
        grade,
        label: criteria.label,
        status: criteria.status,
        description: getIntentDescription(grade, confidence)
      };
    }
  }
  
  return scale.F;
}

/**
 * Calculate grade for risk assessment
 * @param {number} riskScore - Risk score (0-1)
 * @returns {Object} Grade information
 */
function gradeRiskAssessment(riskScore) {
  const scale = GRADE_SCALES.risk;
  
  for (const [grade, criteria] of Object.entries(scale)) {
    if (riskScore <= criteria.max) {
      return {
        grade,
        label: criteria.label,
        status: criteria.status,
        description: getRiskDescription(grade, riskScore)
      };
    }
  }
  
  return scale.F;
}

/**
 * Calculate grade for complexity analysis
 * @param {number} complexityScore - Complexity score
 * @param {number} tier - Complexity tier (0, 1, or 2)
 * @returns {Object} Grade information
 */
function gradeComplexity(complexityScore, tier) {
  const scale = GRADE_SCALES.complexity;
  
  // Use tier for primary grading
  if (tier === 0) return { ...scale.A, grade: 'A', description: 'Auto-merge eligible' };
  if (tier === 1 && complexityScore < 50) return { ...scale.B, grade: 'B', description: 'Standard review process' };
  if (tier === 1) return { ...scale.C, grade: 'C', description: 'Standard review with complexity' };
  if (tier === 2 && complexityScore < 80) return { ...scale.D, grade: 'D', description: 'Expert review recommended' };
  
  return { ...scale.F, grade: 'F', description: 'Critical complexity requiring expert review' };
}

/**
 * Calculate grade for dependency analysis
 * @param {Object} results - Dependency analysis results
 * @returns {Object} Grade information
 */
function gradeDependencies(results) {
  const factors = [];
  
  // Check for issues
  if (results.circular_dependencies && results.circular_dependencies.length > 0) {
    factors.push('circular_deps');
  }
  
  if (results.high_impact_changes && results.high_impact_changes.length > 5) {
    factors.push('critical_issues');
  } else if (results.high_impact_changes && results.high_impact_changes.length > 3) {
    factors.push('significant_issues');
  } else if (results.high_impact_changes && results.high_impact_changes.length > 0) {
    factors.push('some_concerns');
  }
  
  if (factors.length === 0) {
    if (results.changes && results.changes.length < 5) {
      factors.push('no_circular', 'low_impact');
    } else {
      factors.push('minor_issues');
    }
  }
  
  // Determine grade based on factors
  const scale = GRADE_SCALES.dependencies;
  
  if (factors.includes('circular_deps') || factors.includes('critical_issues')) {
    return { ...scale.F, grade: 'F', description: 'Critical dependency issues' };
  }
  if (factors.includes('significant_issues')) {
    return { ...scale.D, grade: 'D', description: 'Significant dependency changes' };
  }
  if (factors.includes('some_concerns')) {
    return { ...scale.C, grade: 'C', description: 'Some dependency concerns' };
  }
  if (factors.includes('minor_issues')) {
    return { ...scale.B, grade: 'B', description: 'Minor dependency changes' };
  }
  
  return { ...scale.A, grade: 'A', description: 'Clean dependencies' };
}

/**
 * Get status indicator emoji/text
 * @param {string} status - Status (PASS, REVIEW, BLOCK)
 * @returns {string} Status indicator
 */
function getStatusIndicator(status) {
  const indicators = {
    'PASS': '✅',
    'REVIEW': '⚠️',
    'BLOCK': '🚫'
  };
  
  return indicators[status] || '❓';
}

/**
 * Format confidence level for display
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} Formatted confidence
 */
function formatConfidence(confidence) {
  if (confidence > 0.8) return 'High confidence';
  if (confidence > 0.6) return 'Good confidence';
  if (confidence > 0.4) return 'Medium confidence';
  if (confidence > 0.2) return 'Low confidence';
  return 'Very low confidence';
}

/**
 * Helper functions for grade descriptions
 */
function getIntentDescription(grade, confidence) {
  const percentage = Math.round(confidence * 100);
  switch (grade) {
    case 'A': return `Clear intent with ${percentage}% confidence`;
    case 'B': return `Good classification with ${percentage}% confidence`;
    case 'C': return `Unclear intent, ${percentage}% confidence`;
    case 'D': return `Vague intent, only ${percentage}% confidence`;
    case 'F': return `Unknown intent, ${percentage}% confidence`;
    default: return `${percentage}% confidence`;
  }
}

function getRiskDescription(grade, riskScore) {
  const percentage = Math.round(riskScore * 100);
  switch (grade) {
    case 'A': return `Low risk deployment (${percentage}%)`;
    case 'B': return `Manageable risk (${percentage}%)`;
    case 'C': return `Moderate risk requiring review (${percentage}%)`;
    case 'D': return `High risk deployment (${percentage}%)`;
    case 'F': return `Critical risk requiring extensive review (${percentage}%)`;
    default: return `${percentage}% risk`;
  }
}

module.exports = {
  gradeIntentClassification,
  gradeRiskAssessment,
  gradeComplexity,
  gradeDependencies,
  getStatusIndicator,
  formatConfidence,
  GRADE_SCALES
};
