const { getPRNumber, loadResults, createOrUpdateComment } = require('./pr-comment-utils');

function buildPreviewSection(results) {
  let section = '';
  
  // Preview link
  if (results.preview_url) {
    section += `**Live Preview:** [View Changes](${results.preview_url})\n\n`;
  }
  
  // UI files summary
  if (results.ui_files_count) {
    section += `**UI Files Modified:** ${results.ui_files_count}\n`;
    if (results.ui_files && results.ui_files.length > 0) {
      section += `- ${results.ui_files.slice(0, 3).join('\\n- ')}\n`;
      if (results.ui_files_count > 3) {
        section += `- ... and ${results.ui_files_count - 3} more\n`;
      }
    }
    section += `\n`;
  }
  
  return section;
}

function buildVisualDiffsSection(results) {
  if (!results.visual_diffs || results.visual_diffs.length === 0) {
    return '';
  }
  
  let section = `**Visual Comparisons:**\n\n`;
  section += `| Viewport | Comparison |\n`;
  section += `|----------|------------|\n`;
  
  results.visual_diffs.forEach(diff => {
    const viewportLabel = diff.viewport.charAt(0).toUpperCase() + diff.viewport.slice(1);
    section += `| ${viewportLabel} | [View Diff](${diff.diff_url}) |\n`;
  });
  
  section += `\n`;
  return section;
}

function buildScreenshotsSection(results) {
  if (!results.preview_screenshots || results.preview_screenshots.length === 0) {
    return '';
  }
  
  let section = `<details>\n<summary>📱 Screenshots by Device</summary>\n\n`;
  
  results.preview_screenshots.forEach(screenshot => {
    const viewportLabel = screenshot.viewport.charAt(0).toUpperCase() + screenshot.viewport.slice(1);
    section += `**${viewportLabel}:**\n`;
    section += `[View Screenshot](${screenshot.url})\n\n`;
  });
  
  section += `</details>\n\n`;
  return section;
}

function buildReviewInstructions(results) {
  let section = `### How to Review Visual Changes\n\n`;
  section += `1. **Quick Check:** Click the Live Preview link to see the changes\n`;
  section += `2. **Visual Diff:** Use the comparison links to see before/after\n`;
  section += `3. **Multi-Device:** Check the screenshots for responsive behavior\n`;
  section += `4. **Interactive Testing:** Use the preview environment to test functionality\n\n`;
  
  // Fallback message if automated analysis failed
  if (results.message && results.message.includes('not available')) {
    section += `**Note:** ${results.message}\n\n`;
  }
  
  return section;
}

module.exports = async ({ github, context }) => {
  const prNumber = getPRNumber(context);
  
  if (!prNumber) {
    console.log('No PR number found, skipping visual diff comment');
    return;
  }
  
  // Load visual diff results
  const results = loadResults('visual-diff-results.json', { 
    has_ui_changes: false,
    message: 'Visual diff analysis not available'
  });
  
  // Skip if no UI changes
  if (!results.has_ui_changes) {
    console.log('No UI changes detected, skipping visual diff comment');
    return;
  }
  
  // Build the comment
  let comment = `## Visual Changes Preview\n\n`;
  comment += buildPreviewSection(results);
  comment += buildVisualDiffsSection(results);
  comment += buildScreenshotsSection(results);
  comment += buildReviewInstructions(results);
  comment += `---\n*Visual diff analysis powered by Playwright*`;
  
  // Create or update the comment
  try {
    await createOrUpdateComment(
      github, 
      context, 
      prNumber, 
      comment, 
      'Visual Changes Preview',  // identifier to find existing comments
      'VISUAL_DIFF_COMMENT'     // unique comment ID for reliable matching
    );
  } catch (error) {
    console.error('Error creating or updating visual diff comment:', error);
    throw error;
  }
};
