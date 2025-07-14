# GitHub Actions Permissions Setup

## Issue: 403 Forbidden when creating/adding labels

The GitHub Actions workflow is failing with "Resource not accessible by integration" errors when trying to create and add labels to PRs.

## Solution 1: Repository Permissions (Current)

The workflow has been updated with explicit permissions:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

This should allow the workflow to:
- Read repository contents
- Create and manage labels
- Add labels to pull requests
- Post comments on pull requests

## Solution 2: Personal Access Token (If permissions don't work)

If the repository permissions still don't work (sometimes happens with organization repositories), you can create a Personal Access Token:

### Steps:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Create a new token with these scopes:
   - `repo` (Full control of private repositories)
   - `pull_requests` (Access pull requests)
3. Add the token as a repository secret named `GITHUB_PAT`
4. Update the workflow to use: `GITHUB_TOKEN: ${{ secrets.GITHUB_PAT }}`

## Troubleshooting

### If you still get 403 errors:

1. **Check repository settings:**
   - Go to Settings → Actions → General
   - Ensure "Read and write permissions" is selected for Workflow permissions

2. **For organization repositories:**
   - Organization admins may need to enable "Allow GitHub Actions to create and approve pull requests"
   - Check organization-level permissions for workflows

3. **Alternative: Manual label creation**
   - Create the labels manually in the repository:
     - `tier:0` (green)
     - `tier:1` (yellow) 
     - `tier:2` (red)
     - `complexity:low` (green)
     - `complexity:medium` (yellow)
     - `complexity:high` (red)
     - `auto-merge` (green)
     - `needs-review` (blue)
     - `needs-expert-review` (red)
     - `score:low`, `score:medium`, `score:high`

## Testing

After applying the permissions fix, test by creating a new PR. The workflow should now be able to:
- Create missing labels
- Add appropriate labels based on cognitive complexity  
- Post cognitive score comments
