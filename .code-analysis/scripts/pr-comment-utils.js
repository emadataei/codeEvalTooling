const fs = require('fs');

/**
 * Shared utilities for GitHub PR comment management
 */

/**
 * Get PR number from GitHub context
 * @param {object} context - GitHub context object
 * @returns {number|null} PR number or null if not found
 */
function getPRNumber(context) {
  const prNumber = context.issue?.number || 
                   context.payload?.pull_request?.number || 
                   context.payload?.number;
  
  if (!prNumber) {
    console.log('No PR number found in context');
    console.log('Available context keys:', Object.keys(context));
    if (context.payload) {
      console.log('Payload keys:', Object.keys(context.payload));
    }
  }
  
  return prNumber;
}

/**
 * Load JSON results from file
 * @param {string} filePath - Path to JSON file
 * @param {object} defaultResults - Default results if file not found
 * @returns {object} Parsed results or default
 */
function loadResults(filePath, defaultResults = {}) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const results = JSON.parse(content);
    console.log(`Successfully loaded results from ${filePath}`);
    return results;
  } catch (error) {
    console.log(`Could not read ${filePath}:`, error.message);
    return defaultResults;
  }
}

/**
 * Create or update a PR comment
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub context
 * @param {number} prNumber - PR number
 * @param {string} commentBody - Comment content
 * @param {string} identifier - Unique string to identify existing comments
 * @param {string} commentId - Optional unique comment ID for GitHub Actions workflow
 * @returns {Promise<void>}
 */
async function createOrUpdateComment(github, context, prNumber, commentBody, identifier, commentId = null) {
  try {
    // Get all comments on the PR
    const { data: comments } = await github.rest.issues.listComments({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: prNumber,
    });

    // Find existing comment by identifier
    const existingComment = comments.find(comment => 
      comment.body.includes(identifier)
    );

    // Add comment ID if provided (for GitHub Actions workflow tracking)
    const finalCommentBody = commentId ? 
      `${commentBody}\n\n<!-- comment-id: ${commentId} -->` : 
      commentBody;

    if (existingComment) {
      console.log(`Updating existing comment containing "${identifier}"`);
      await github.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: existingComment.id,
        body: finalCommentBody
      });
      console.log('Successfully updated existing comment');
    } else {
      console.log(`Creating new comment with identifier "${identifier}"`);
      const result = await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
        body: finalCommentBody
      });
      console.log('Successfully created new comment with ID:', result.data.id);
    }
  } catch (error) {
    console.error('Error posting/updating comment:', error);
    console.error('Error details:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

/**
 * Set labels on a PR
 * @param {object} github - GitHub API client
 * @param {object} context - GitHub context
 * @param {number} prNumber - PR number
 * @param {string[]} labels - Array of label names
 * @returns {Promise<void>}
 */
async function setLabels(github, context, prNumber, labels) {
  try {
    await github.rest.issues.setLabels({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: prNumber,
      labels: labels
    });
    console.log('Successfully set labels:', labels);
  } catch (error) {
    console.error('Error setting labels:', error);
    throw error;
  }
}

module.exports = {
  getPRNumber,
  loadResults,
  createOrUpdateComment,
  setLabels
};
