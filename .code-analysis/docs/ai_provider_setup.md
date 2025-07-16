# AI Foundry Setup Guide

This project uses Azure AI Foundry for cognitive complexity analysis to automatically score pull requests and assign appropriate review tiers.

## Azure AI Foundry

Azure AI Foundry provides a unified platform for AI model access with enterprise-grade security and compliance features.

## GitHub Actions Configuration

For the automated PR analysis to work, you need to configure the following repository secrets:

### 1. Navigate to Repository Secrets
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### 2. Configure AI Foundry Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AI_FOUNDRY_ENDPOINT` | `https://hveai7690491737.services.ai.azure.com/models` | Your AI Foundry project endpoint |
| `AI_FOUNDRY_MODEL` | `gpt-4o` | Your model deployment name (optional) |
| `AI_FOUNDRY_TOKEN` | `your-token` | API token (optional if using DefaultAzureCredential) |

## Getting Your Credentials

### AI Foundry
1. Go to [AI Foundry Studio](https://ai.azure.com)
2. Navigate to your project
3. Copy the project endpoint from the overview page
4. For API tokens, go to **Settings** → **Connections**

## Local Development

For local development, copy `.env.example` to `.env` and update the AI Foundry values:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```properties
# AI Foundry Configuration
AI_FOUNDRY_ENDPOINT=https://hveai7690491737.services.ai.azure.com/models
AI_FOUNDRY_MODEL=gpt-4o
# AI_FOUNDRY_TOKEN=your-token-if-using-api-key-auth
```

**Note:** If you don't set `AI_FOUNDRY_TOKEN`, the system will use `DefaultAzureCredential` which works with Azure CLI authentication.

## How It Works

When a pull request is opened or updated, the GitHub Actions workflow:

1. **Analyzes static complexity** - Counts cyclomatic complexity, nesting depth, function length
2. **Calculates impact score** - Considers files changed, type of files, blast radius
3. **Uses AI assessment** - Sends code to your configured AI provider for comprehension analysis
4. **Assigns tier** - Combines scores to determine review requirements:
   - **Tier 0**: Auto-merge eligible (< 30 points)
   - **Tier 1**: Single reviewer required (30-60 points)
   - **Tier 2**: Domain expert required (60+ points)

## Security Notes

- **Never commit credentials** - Always use GitHub secrets or environment variables
- **Minimum permissions** - Only grant necessary access to your AI provider resources
- **Monitor usage** - Keep track of API usage to avoid unexpected costs
- **Rotate keys** - Regularly rotate your API keys for security

## Troubleshooting

### Common Issues

**Error: "Unsupported AI provider"**
- Check that `AI_PROVIDER` is set to either `azure` or `ai_foundry`

**Error: "Missing required environment variables"**
- Verify all required secrets are configured for your chosen provider

**Error: "API authentication failed"**
- Check that your API key/token is correct and has not expired
- Verify the endpoint URL is correct

**Analysis not running**
- Check that the workflow file `.github/workflows/cognitive_scoring.yml` exists
- Verify GitHub Actions are enabled for your repository

### Getting Help

If you encounter issues:
1. Check the Actions tab in your GitHub repository for error logs
2. Verify your AI provider credentials are correct
3. Test the configuration locally using the `.env` file
4. Check the [GitHub Actions documentation](https://docs.github.com/en/actions) for workflow troubleshooting
