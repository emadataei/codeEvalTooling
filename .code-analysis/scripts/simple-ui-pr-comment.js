const { getPRNumber, createOrUpdateComment } = require('./pr-comment-utils');

function buildSimpleUIComment(results, prNumber, runId, repoName) {
  if (!results.has_ui_changes) {
    return null; // No comment needed
  }
  
  let comment = `## UI Changes Detected\n\n`;
  
  // Show UI file changes by category in a clean format
  comment += `**Files Changed:** ${results.ui_files_count}\n\n`;
  
  if (results.categories.components.length > 0) {
    comment += `**Components:**\n`;
    results.categories.components.forEach(file => {
      comment += `- \`${file}\`\n`;
    });
    comment += `\n`;
  }
  
  if (results.categories.pages.length > 0) {
    comment += `**Pages:**\n`;
    results.categories.pages.forEach(file => {
      comment += `- \`${file}\`\n`;
    });
    comment += `\n`;
  }
  
  if (results.categories.styles.length > 0) {
    comment += `**Styles:**\n`;
    results.categories.styles.forEach(file => {
      comment += `- \`${file}\`\n`;
    });
    comment += `\n`;
  }
  
  // Add embedded screenshots if available
  comment += addEmbeddedScreenshots();
  
  // Simple review checklist
  comment += `**Review Focus:**\n`;
  comment += `- Check the modified files in the Files tab\n`;
  comment += `- Review the screenshots above\n`;
  comment += `- Test the changes locally\n`;
  comment += `- Verify responsive design if styles changed\n`;
  comment += `- Check accessibility if components changed\n\n`;
  
  return comment;
}

function addEmbeddedScreenshots() {
  try {
    const fs = require('fs');
    const screenshotData = JSON.parse(fs.readFileSync('screenshot_urls.json', 'utf8'));
    
    let screenshotsSection = `**Visual Preview:**\n\n`;
    
    Object.entries(screenshotData).forEach(([filename, dataUrl]) => {
      const pageName = filename.replace('.png', '').replace('_', ' ');
      screenshotsSection += `**${pageName}:**\n\n`;
      
      // Check data URL size
      const sizeKB = Math.round(dataUrl.length / 1024);
      
      if (dataUrl && dataUrl.startsWith('data:image/') && sizeKB < 100) {
        // Small images can be embedded directly
        screenshotsSection += `![${pageName}](${dataUrl})\n\n`;
      } else if (dataUrl && dataUrl.startsWith('data:image/')) {
        // Large images - provide size info and refer to artifacts
        screenshotsSection += `📸 Screenshot captured (${sizeKB} KB)\n\n`;
        screenshotsSection += `*Due to size limits, the full screenshot is available in the GitHub Actions artifacts. Click the "Actions" tab above and download the "ui-screenshots" artifact for the full resolution image.*\n\n`;
      } else {
        screenshotsSection += `❌ Screenshot data not available\n\n`;
      }
    });
    
    return screenshotsSection;
  } catch (error) {
    console.log('No screenshot data found, skipping embedded images:', error.message);
    return `**Visual Preview:**\n\n*No screenshots available - check the Actions tab for artifacts.*\n\n`;
  }
}

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping UI changes comment');
    return;
  }
  
  let results;
  try {
    const fs = require('fs');
    results = JSON.parse(fs.readFileSync('visual-diff-results.json', 'utf8'));
  } catch (error) {
    console.log('No UI analysis results found, skipping comment:', error.message);
    return;
  }
  
  // Get GitHub Actions context for artifact links
  const runId = process.env.GITHUB_RUN_ID;
  const repoName = process.env.GITHUB_REPOSITORY;
  
  const commentBody = buildSimpleUIComment(results, prNumber, runId, repoName);
  
  if (!commentBody) {
    console.log('No UI changes detected, skipping comment');
    return;
  }
  
  await createOrUpdateComment(
    github,
    context,
    prNumber,
    commentBody,
    'UI Changes Detected'
  );
  
  console.log('UI changes comment posted successfully');
};
