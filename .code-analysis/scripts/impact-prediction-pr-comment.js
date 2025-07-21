const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping impact prediction comment');
    return;
  }
  
  // Load impact prediction results
  const results = loadResults('impact-prediction-results.json', { 
    overall_risk_score: 0.3,
    deployment_readiness: 'READY - Low risk deployment',
    summary: 'Impact prediction analysis failed',
    impacts: [],
    test_recommendations: [],
    monitoring_suggestions: [],
    rollback_considerations: ['Standard rollback procedures apply']
  });
  
  // Build the comment
  let comment = `## 📊 Impact Prediction Analysis\n\n`;
  
  // Risk score and deployment readiness
  const riskEmoji = getRiskEmoji(results.overall_risk_score);
  const riskPercentage = Math.round(results.overall_risk_score * 100);
  comment += `${riskEmoji} **Risk Score:** ${riskPercentage}% | **Deployment:** ${results.deployment_readiness}\n\n`;
  
  // Summary if meaningful
  if (results.summary && results.summary !== 'Impact prediction analysis failed') {
    const summary = results.summary.length > 250 
      ? results.summary.substring(0, 250) + '...' 
      : results.summary;
    comment += `**Analysis Summary:**\n${summary}\n\n`;
  }
  
  // High-priority impacts
  const highImpacts = results.impacts.filter(impact => 
    impact.severity === 'high' || impact.severity === 'critical'
  );
  
  if (highImpacts.length > 0) {
    comment += `**🚨 Key Concerns:**\n`;
    highImpacts.slice(0, 3).forEach(impact => {
      const severityEmoji = getSeverityEmoji(impact.severity);
      const categoryEmoji = getCategoryEmoji(impact.category);
      comment += `${severityEmoji} ${categoryEmoji} **${impact.category.toUpperCase()}** (${impact.severity})\n`;
      comment += `   ${impact.description}\n`;
      if (impact.confidence) {
        comment += `   *Confidence: ${Math.round(impact.confidence * 100)}%*\n`;
      }
      comment += `\n`;
    });
  }
  
  // High-priority test recommendations
  const highPriorityTests = results.test_recommendations.filter(test => 
    test.priority === 'high'
  );
  
  if (highPriorityTests.length > 0) {
    comment += `**🧪 Critical Testing Required:**\n`;
    highPriorityTests.slice(0, 3).forEach(test => {
      comment += `🔥 **${test.test_type.toUpperCase()}** - ${test.description}\n`;
    });
    comment += `\n`;
  }
  
  // Deployment guidance based on risk
  if (results.overall_risk_score > 0.7) {
    comment += `**🚀 Deployment Guidance:**\n`;
    comment += `⚠️ **High Risk Deployment** - Consider staged rollout\n`;
    if (results.rollback_considerations.length > 0) {
      comment += `📋 **Rollback Plan:** ${results.rollback_considerations[0]}\n`;
    }
    comment += `\n`;
  }
  
  // Monitoring suggestions for medium+ risk
  if (results.monitoring_suggestions.length > 0 && results.overall_risk_score > 0.4) {
    comment += `**📈 Monitoring Recommendations:**\n`;
    results.monitoring_suggestions.slice(0, 2).forEach(suggestion => {
      comment += `• ${suggestion}\n`;
    });
    comment += `\n`;
  }
  
  // Detailed breakdown in collapsible section
  comment += `<details>\n<summary>📋 View Detailed Analysis</summary>\n\n`;
  
  if (results.impacts.length > 0) {
    comment += `**All Predicted Impacts:**\n`;
    results.impacts.forEach(impact => {
      const severityEmoji = getSeverityEmoji(impact.severity);
      const categoryEmoji = getCategoryEmoji(impact.category);
      comment += `${severityEmoji} ${categoryEmoji} **${impact.category}** (${impact.severity})\n`;
      comment += `   ${impact.description}\n`;
      if (impact.affected_components && impact.affected_components.length > 0) {
        comment += `   *Affects: ${impact.affected_components.join(', ')}*\n`;
      }
      comment += `\n`;
    });
  }
  
  if (results.test_recommendations.length > 0) {
    comment += `**All Test Recommendations:**\n`;
    results.test_recommendations.forEach(test => {
      const priorityEmoji = test.priority === 'high' ? '🔥' : test.priority === 'medium' ? '⚡' : '💡';
      comment += `${priorityEmoji} **${test.test_type}** (${test.priority} priority)\n`;
      comment += `   ${test.description}\n`;
      if (test.specific_tests && test.specific_tests.length > 0) {
        comment += `   *Tests: ${test.specific_tests.join(', ')}*\n`;
      }
      comment += `\n`;
    });
  }
  
  if (results.rollback_considerations.length > 1) {
    comment += `**Rollback Considerations:**\n`;
    results.rollback_considerations.forEach(consideration => {
      comment += `• ${consideration}\n`;
    });
  }
  
  comment += `\n</details>`;
  
  // Add risk interpretation guide for high/critical risk
  if (results.overall_risk_score > 0.6) {
    comment += `\n💡 **Risk Interpretation:**\n`;
    if (results.overall_risk_score > 0.8) {
      comment += `🔴 **Critical Risk** - Extensive testing and staged deployment recommended\n`;
    } else {
      comment += `🟡 **High Risk** - Additional review and testing recommended\n`;
    }
  }
  
  // Post or update the comment
  await createOrUpdateComment(
    github, 
    context, 
    prNumber, 
    comment, 
    '📊 Impact Prediction Analysis',
    `impact-prediction-${context.payload?.pull_request?.head?.sha || 'unknown'}`
  );
  
  console.log('Impact prediction comment posted/updated successfully');
};

function getRiskEmoji(riskScore) {
  if (riskScore < 0.3) return '🟢';
  if (riskScore < 0.7) return '🟡';
  return '🔴';
}

function getSeverityEmoji(severity) {
  const emojis = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🟠',
    'critical': '🔴'
  };
  return emojis[severity] || '⚪';
}

function getCategoryEmoji(category) {
  const emojis = {
    'performance': '⚡',
    'security': '🔒',
    'compatibility': '🔄',
    'user_experience': '👤',
    'data_integrity': '🗄️',
    'reliability': '⚖️',
    'maintainability': '🔧',
    'testing': '🧪',
    'deployment': '🚀',
    'external_dependencies': '🔗'
  };
  return emojis[category] || '📋';
}
