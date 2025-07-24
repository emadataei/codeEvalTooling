/**
 * Generate PR visual summary comment
 * This script creates a comment with visual overview and file categorization
 */

module.exports = async ({ github, context, changedFiles }) => {
  const fs = require('fs');
  const { createOrUpdateComment, getPRNumber } = require('./pr-comment-utils');
  
  try {
    console.log('Generating PR visual summary comment...');
    
    const prNumber = getPRNumber(context);
    if (!prNumber) {
      console.log('No PR number found, skipping comment');
      return;
    }
    
    // Try to load enhanced visuals reports
    let reportContent = '';
    
    // First try enhanced image report
    if (fs.existsSync('.code-analysis/outputs/enhanced_image_report.md')) {
      reportContent = fs.readFileSync('.code-analysis/outputs/enhanced_image_report.md', 'utf8');
      console.log('Using enhanced image report with embedded visuals');
    }
    // Then try comprehensive report
    else if (fs.existsSync('.code-analysis/outputs/comprehensive_pr_report.md')) {
      reportContent = fs.readFileSync('.code-analysis/outputs/comprehensive_pr_report.md', 'utf8');
      console.log('Using comprehensive report from enhanced visuals workflow');
    }
    // Generate basic visual summary as fallback
    else {
      console.log('No enhanced visuals reports found, generating basic visual summary');
      
      const files = changedFiles || [];
      const filteredFiles = files.filter(f => f && f.trim());
      
      try {
        // Create a mock result for comment generation
        const path = require('path');
        const categories = {
          'Frontend': [],
          'Backend': [],
          'Tests': [],
          'Config': [],
          'Documentation': []
        };        filteredFiles.forEach(file => {
          if (!file.trim()) return;
          
          const filePath = path.parse(file);
          const ext = filePath.ext.toLowerCase();
          const fileName = file.toLowerCase();
          
          if (['.tsx', '.jsx', '.vue', '.css', '.html', '.scss', '.sass'].includes(ext)) {
            categories.Frontend.push(file);
          } else if (['.py', '.js', '.ts', '.java', '.cs', '.go', '.rs'].includes(ext)) {
            if (fileName.includes('test') || fileName.includes('spec') || fileName.includes('__tests__')) {
              categories.Tests.push(file);
            } else {
              categories.Backend.push(file);
            }
          } else if (['.json', '.yml', '.yaml', '.toml', '.ini', '.env', '.config'].includes(ext)) {
            categories.Config.push(file);
          } else if (['.md', '.txt', '.rst', '.doc'].includes(ext)) {
            categories.Documentation.push(file);
          } else {
            categories.Backend.push(file);
          }
        });
        
        const totalFiles = Object.values(categories).reduce((sum, files) => sum + files.length, 0);
        const activeCategories = Object.fromEntries(
          Object.entries(categories).filter(([_, files]) => files.length > 0)
        );
        
        if (totalFiles > 0) {
          // Create a comment-specific summary
          const categoryBreakdown = Object.entries(activeCategories).map(([category, files]) => {
            let impact;
            if (files.length > 5) {
              impact = 'High';
            } else if (files.length > 2) {
              impact = 'Medium';
            } else {
              impact = 'Low';
            }
            const percentage = Math.round((files.length / totalFiles) * 100);
            return `- **${category}:** ${files.length} files (${percentage}%) ${impact}`;
          }).join('\n');
          
          reportContent = `## PR Visual Summary

### Quick Stats
- **Total Files Changed:** ${totalFiles}
- **Categories Affected:** ${Object.keys(activeCategories).length}

### Category Breakdown
${categoryBreakdown}

*Enhanced visuals and detailed analysis may be available in the enhanced-pr-visuals workflow.*`;
        } else {
          reportContent = '## PR Visual Summary\n\n**Status:** Analysis completed with basic metrics. Enhanced visuals may be available in a separate workflow run.';
        }
      } catch (scriptError) {
        console.error('Error running visual summary script:', scriptError);
        reportContent = '## PR Visual Summary\n\n**Status:** Analysis completed. Enhanced visuals may be available in a separate workflow run.';
      }
    }
    
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      reportContent,
      'PR Visual Summary',
      'pr-visual-summary'
    );
    
    console.log('PR visual summary comment posted/updated successfully');
    return { success: true };
    
  } catch (error) {
    console.error('Error generating PR visual summary comment:', error);
    return { success: false, error: error.message };
  }
};
