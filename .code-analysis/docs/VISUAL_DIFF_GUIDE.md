# Visual Diff System Setup & Usage

## Overview
Automated visual diffing for UI changes in pull requests. The system detects UI modifications, takes screenshots, generates comparisons, and posts visual feedback directly in PR comments.

## Quick Setup

### 1. Prerequisites
```bash
# Install dependencies (already in requirements.txt)
pip install playwright requests
playwright install chromium
```

### 2. Deployment Service Setup
Choose one deployment service:

#### Vercel (Recommended for Next.js)
1. Connect repository to Vercel
2. Enable preview deployments
3. Add `VERCEL_TOKEN` to GitHub secrets (optional, for API access)

#### Netlify
1. Connect repository to Netlify  
2. Enable deploy previews
3. Add `NETLIFY_TOKEN` to GitHub secrets (optional, for API access)

#### Custom Deployment
Set these GitHub repository secrets:
- `BASE_DEPLOYMENT_URL`: Main deployment URL
- `PREVIEW_DEPLOYMENT_URL`: Preview URL pattern (e.g., `https://pr-{pr_number}-myapp.example.com`)

### 3. GitHub Actions Integration
The system is already integrated in `.github/workflows/cognitive_scoring.yml` and will automatically:
- Detect UI file changes (`.tsx`, `.jsx`, `.vue`, `.css`, etc.)
- Generate deployment URLs based on your service
- Take screenshots and create visual diffs
- Post results as PR comments

## How It Works

### Automatic Detection
- **UI Files**: Detects changes in React, Vue, CSS, and other UI files
- **Deployment Service**: Auto-detects Vercel, Netlify, GitHub Pages, or custom
- **Preview URLs**: Generates appropriate preview URLs for your deployment service

### Visual Comparison Process
1. **Wait for deployment** (2-minute timeout with progress indicators)
2. **Take screenshots** at multiple viewport sizes (desktop, tablet, mobile)
3. **Generate visual diffs** comparing base vs preview deployments
4. **Post PR comment** with live preview links and visual comparisons

### Example PR Comment
```markdown
## Visual Changes Preview

**Live Preview:** [View Changes](https://pr-123-myapp.vercel.app)

**UI Files Modified:** 3
- src/components/UserProfile.tsx
- src/app/page.tsx
- src/app/globals.css

**Visual Comparisons:**
| Viewport | Comparison |
|----------|------------|
| Desktop | [View Diff](https://github.com/user/repo/actions/runs/123456/artifacts/diff-desktop.png) |
| Tablet | [View Diff](https://github.com/user/repo/actions/runs/123456/artifacts/diff-tablet.png) |
| Mobile | [View Diff](https://github.com/user/repo/actions/runs/123456/artifacts/diff-mobile.png) |

📱 Screenshots by Device
- Desktop: [View Screenshot](https://github.com/user/repo/actions/runs/123456/artifacts/preview-desktop.png)
- Tablet: [View Screenshot](https://github.com/user/repo/actions/runs/123456/artifacts/preview-tablet.png)
- Mobile: [View Screenshot](https://github.com/user/repo/actions/runs/123456/artifacts/preview-mobile.png)
```

## What You'll See in PRs

When you push changes that modify UI files, you'll get:

1. **PR Comment** with live preview link and artifact links
2. **GitHub Actions Artifacts** containing:
   - Visual diff images (before/after comparisons)
   - Screenshot images for each viewport
   - Analysis results JSON
3. **Workflow Status** showing if visual analysis passed/failed

## Deployment URL Patterns

The system automatically generates URLs based on your deployment service:

### Vercel
- **Base**: `https://{repo-name}.vercel.app`
- **Preview**: `https://pr-{pr-number}-{repo-name}.vercel.app`

### Netlify
- **Base**: `https://{repo-name}.netlify.app` 
- **Preview**: `https://deploy-preview-{pr-number}--{repo-name}.netlify.app`

### GitHub Pages
- **Base**: `https://{owner}.github.io/{repo-name}`
- **Preview**: `https://{owner}.github.io/{repo-name}/pr-{pr-number}`

### Custom
- Use `BASE_DEPLOYMENT_URL` and `PREVIEW_DEPLOYMENT_URL` environment variables
- Preview URL supports `{pr_number}` and `{repo_name}` placeholders

## Configuration

### Environment Variables
- `PR_NUMBER`: Pull request number (auto-set by GitHub Actions)
- `GITHUB_REPOSITORY`: Repository name (auto-set by GitHub Actions)
- `BASE_DEPLOYMENT_URL`: Base deployment URL (for custom deployments)
- `PREVIEW_DEPLOYMENT_URL`: Preview URL pattern (for custom deployments)
- `VERCEL_TOKEN`: Vercel API token (optional, for real-time status)
- `NETLIFY_TOKEN`: Netlify API token (optional, for real-time status)

### Viewport Sizes
Default viewports can be customized in `generate_visual_diffs.py`:
```python
viewports = [
    (1200, 800),   # Desktop
    (768, 1024),   # Tablet
    (375, 667)     # Mobile
]
```

## Troubleshooting

### Common Issues

**No visual diffs generated**
- Check if deployment service is properly connected
- Verify preview deployment is accessible
- Ensure UI files are detected in the changed files

**Deployment timeout**
- Default timeout is 2 minutes
- Check deployment service status
- Verify URL patterns are correct

**Screenshots failing**
- Ensure Playwright is installed (`playwright install chromium`)
- Check if preview URL returns HTTP 200
- Verify ImageMagick is available for diff generation

### Local Testing
```bash
# Test deployment integration
export TEST_MODE=true
export PR_NUMBER=123
export GITHUB_REPOSITORY=user/repo
python .code-analysis/scripts/deployment_integration.py

# Test visual diff generation
python .code-analysis/scripts/generate_visual_diffs.py
```

## Benefits

### For Reviewers
- **Visual feedback** instead of just code changes
- **Live preview links** for immediate testing
- **Multi-device screenshots** for responsive design review
- **Before/after comparisons** for impact assessment

### For Teams
- **Automated visual testing** in CI/CD pipeline
- **Faster review cycles** with visual context
- **Reduced back-and-forth** on UI changes
- **Stakeholder-friendly** visual summaries

## Performance

- **2-minute deployment timeout** (down from 5 minutes)
- **Parallel processing** where possible
- **Graceful degradation** when services unavailable
- **Test mode** for instant local development

The system is designed to be lightweight, fast, and reliable for production use across different deployment services.
