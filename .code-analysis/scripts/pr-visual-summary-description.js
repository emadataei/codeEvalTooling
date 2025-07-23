/**
 * Generate and add PR visual summary to the PR description
 * This script creates a visual overview with file categorization and Mermaid diagrams
 */

module.exports = async ({ github, context, changedFiles }) => {
  const path = require('path');
  
  try {
    console.log('Generating PR visual summary for description...');
    
    // Get changed files from parameter or context
    const files = changedFiles || [];
    const filteredFiles = files.filter(f => f && f.trim());
    
    console.log(`Processing ${filteredFiles.length} changed files`);
    
    // Categorize files
    const categories = {
      'Frontend': [],
      'Backend': [],
      'Tests': [],
      'Config': [],
      'Documentation': []
    };
    
    filteredFiles.forEach(file => {
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
        categories.Backend.push(file); // Default category
      }
    });
    
    // Generate Mermaid diagram
    let mermaid = '```mermaid\ngraph TB\n';
    mermaid += '    PR[📋 Pull Request Changes]\n';
    
    let nodeId = 1;
    const hasCategories = Object.values(categories).some(files => files.length > 0);
    
    if (hasCategories) {
      Object.entries(categories).forEach(([category, files]) => {
        if (files.length > 0) {
          const catId = `CAT${nodeId}`;
          let impact;
          if (files.length > 5) {
            impact = '🔴';
          } else if (files.length > 2) {
            impact = '🟡';
          } else {
            impact = '🟢';
          }
          mermaid += `    ${catId}[${impact} ${category}<br/>${files.length} files]\n`;
          mermaid += `    PR --> ${catId}\n`;
          nodeId++;
        }
      });
      
      // Add styling
      mermaid += '    classDef high fill:#ffebee,stroke:#f44336,stroke-width:2px\n';
      mermaid += '    classDef medium fill:#fff8e1,stroke:#ff9800,stroke-width:2px\n';
      mermaid += '    classDef low fill:#e8f5e8,stroke:#4caf50,stroke-width:2px\n';
    } else {
      mermaid += '    EMPTY[No categorizable files detected]\n';
      mermaid += '    PR --> EMPTY\n';
    }
    mermaid += '```\n\n';
    
    // Generate impact summary
    const totalFiles = Object.values(categories).reduce((sum, files) => sum + files.length, 0);
    let impactSummary = '**Impact Summary:** ';
    const summaryParts = [];
    
    if (totalFiles > 0) {
      Object.entries(categories).forEach(([category, files]) => {
        if (files.length > 0) {
          const percentage = Math.round((files.length / totalFiles) * 100);
          let impact;
          if (files.length > 5) {
            impact = '🔴';
          } else if (files.length > 2) {
            impact = '🟡';
          } else {
            impact = '🟢';
          }
          summaryParts.push(`${impact} ${category}: ${files.length} (${percentage}%)`);
        }
      });
      
      impactSummary += summaryParts.join(' | ') + '\n\n';
    } else {
      impactSummary += 'No significant file changes detected\n\n';
    }
    
    // Create visual summary section
    const visualSection = `## 📊 Visual Overview\n\n${mermaid}${impactSummary}`;
    
    // Get current PR
    const { data: pr } = await github.rest.pulls.get({
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: context.payload.pull_request.number
    });
    
    let body = pr.body || '';
    
    // Remove existing visual overview if present
    body = body.replace(/## 📊 Visual Overview[\s\S]*?(?=##|$)/g, '').trim();
    
    // Add visual summary at the end of description
    if (body && !body.endsWith('\n\n')) {
      body += '\n\n';
    }
    body += visualSection;
    
    // Update PR description
    await github.rest.pulls.update({
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: context.payload.pull_request.number,
      body: body
    });
    
    console.log('PR description updated with visual summary');
    console.log(`Updated description with ${totalFiles} files across ${summaryParts.length} categories`);
    
    return {
      success: true,
      totalFiles,
      categories: Object.fromEntries(
        Object.entries(categories).filter(([_, files]) => files.length > 0)
      )
    };
    
  } catch (error) {
    console.error('Error generating PR visual summary:', error);
    
    // Try to add a fallback summary
    try {
      const { data: pr } = await github.rest.pulls.get({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.payload.pull_request.number
      });
      
      let body = pr.body || '';
      body = body.replace(/## 📊 Visual Overview[\s\S]*?(?=##|$)/g, '').trim();
      
      const fallbackSection = `## 📊 Visual Overview\n\n**Status:** Visual summary generation encountered an error. Please check the workflow logs for details.\n\n`;
      
      if (body && !body.endsWith('\n\n')) {
        body += '\n\n';
      }
      body += fallbackSection;
      
      await github.rest.pulls.update({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.payload.pull_request.number,
        body: body
      });
      
      console.log('Added fallback visual summary to PR description');
    } catch (fallbackError) {
      console.error('Failed to add fallback summary:', fallbackError);
    }
    
    return {
      success: false,
      error: error.message
    };
  }
};
