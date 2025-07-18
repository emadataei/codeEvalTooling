#!/usr/bin/env python3
"""
Deployment Integration Helper
Detects deployment environment and generates appropriate preview URLs.
"""

import os
import re
import subprocess
import json
from typing import Optional, Dict, Any


class DeploymentIntegration:
    """Handles integration with various deployment services."""
    
    def __init__(self):
        self.pr_number = os.getenv('PR_NUMBER', '0')
        self.repo_name = self._get_repo_name()
        self.deployment_type = self._detect_deployment_type()
    
    def _get_repo_name(self) -> str:
        """Extract repository name from environment or git config."""
        # Try GitHub Actions environment first
        github_repo = os.getenv('GITHUB_REPOSITORY', '')
        if github_repo:
            return github_repo.split('/')[-1]
        
        # Fallback to git config
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()
            # Extract repo name from git URL
            match = re.search(r'([^/]+?)(?:\.git)?$', url)
            return match.group(1) if match else 'unknown'
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 'unknown'
    
    def _detect_deployment_type(self) -> str:
        """Detect the deployment service being used."""
        # Check for Vercel
        if os.path.exists('vercel.json') or os.getenv('VERCEL_TOKEN'):
            return 'vercel'
        
        # Check for Netlify
        if os.path.exists('netlify.toml') or os.path.exists('_redirects') or os.getenv('NETLIFY_TOKEN'):
            return 'netlify'
        
        # Check for custom deployment URLs
        if os.getenv('BASE_DEPLOYMENT_URL') and os.getenv('PREVIEW_DEPLOYMENT_URL'):
            return 'custom'
        
        # Default to GitHub Pages pattern
        return 'github-pages'
    
    def get_preview_url(self) -> Optional[str]:
        """Generate preview URL based on deployment type."""
        if self.deployment_type == 'vercel':
            return self._get_vercel_preview_url()
        elif self.deployment_type == 'netlify':
            return self._get_netlify_preview_url()
        elif self.deployment_type == 'custom':
            return self._get_custom_preview_url()
        elif self.deployment_type == 'github-pages':
            return self._get_github_pages_preview_url()
        
        return None
    
    def get_base_url(self) -> Optional[str]:
        """Get the base deployment URL for comparison."""
        if self.deployment_type == 'vercel':
            return f"https://{self.repo_name}.vercel.app"
        elif self.deployment_type == 'netlify':
            return f"https://{self.repo_name}.netlify.app"
        elif self.deployment_type == 'custom':
            return os.getenv('BASE_DEPLOYMENT_URL')
        elif self.deployment_type == 'github-pages':
            github_repo = os.getenv('GITHUB_REPOSITORY', '')
            if github_repo:
                return f"https://{github_repo.split('/')[0]}.github.io/{self.repo_name}"
        
        return None
    
    def _get_vercel_preview_url(self) -> Optional[str]:
        """Generate Vercel preview URL."""
        # Try to get from Vercel API if token is available
        if os.getenv('VERCEL_TOKEN'):
            try:
                return self._fetch_vercel_preview_url()
            except Exception:
                pass
        
        # Fallback to standard pattern
        return f"https://pr-{self.pr_number}-{self.repo_name}.vercel.app"
    
    def _get_netlify_preview_url(self) -> Optional[str]:
        """Generate Netlify preview URL."""
        # Try to get from Netlify API if token is available
        if os.getenv('NETLIFY_TOKEN'):
            try:
                return self._fetch_netlify_preview_url()
            except Exception:
                pass
        
        # Fallback to standard pattern
        return f"https://deploy-preview-{self.pr_number}--{self.repo_name}.netlify.app"
    
    def _get_custom_preview_url(self) -> Optional[str]:
        """Generate custom preview URL."""
        pattern = os.getenv('PREVIEW_DEPLOYMENT_URL', '')
        if pattern:
            return pattern.format(
                pr_number=self.pr_number,
                repo_name=self.repo_name
            )
        return None
    
    def _get_github_pages_preview_url(self) -> Optional[str]:
        """Generate GitHub Pages preview URL."""
        github_repo = os.getenv('GITHUB_REPOSITORY', '')
        if github_repo:
            return f"https://{github_repo.split('/')[0]}.github.io/{self.repo_name}/pr-{self.pr_number}"
        return None
    
    def _fetch_vercel_preview_url(self) -> Optional[str]:
        """Fetch actual preview URL from Vercel API."""
        import requests
        
        token = os.getenv('VERCEL_TOKEN')
        if not token:
            return None
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get deployments for the project
        response = requests.get(
            f'https://api.vercel.com/v6/deployments?projectId={self.repo_name}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            deployments = response.json()['deployments']
            
            # Find the deployment for this PR
            for deployment in deployments:
                if deployment.get('meta', {}).get('githubCommitRef') == f"refs/pull/{self.pr_number}/merge":
                    return f"https://{deployment['url']}"
        
        return None
    
    def _fetch_netlify_preview_url(self) -> Optional[str]:
        """Fetch actual preview URL from Netlify API."""
        import requests
        
        token = os.getenv('NETLIFY_TOKEN')
        if not token:
            return None
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get sites
        response = requests.get(
            'https://api.netlify.com/api/v1/sites',
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        sites = response.json()
        site_id = self._find_netlify_site_id(sites)
        
        if not site_id:
            return None
        
        return self._get_netlify_deploy_preview_url(site_id, headers)
    
    def _find_netlify_site_id(self, sites: list) -> Optional[str]:
        """Find the Netlify site ID for this repository."""
        for site in sites:
            if site.get('name') == self.repo_name:
                return site['id']
        return None
    
    def _get_netlify_deploy_preview_url(self, site_id: str, headers: dict) -> Optional[str]:
        """Get the deploy preview URL for this PR."""
        import requests
        
        # Get deploy previews
        deploys_response = requests.get(
            f'https://api.netlify.com/api/v1/sites/{site_id}/deploys',
            headers=headers,
            timeout=10
        )
        
        if deploys_response.status_code != 200:
            return None
        
        deploys = deploys_response.json()
        
        # Find the deploy preview for this PR
        for deploy in deploys:
            if (deploy.get('context') == 'deploy-preview' and 
                str(deploy.get('review_id')) == self.pr_number):
                return deploy['deploy_ssl_url']
        
        return None
    
    def wait_for_deployment(self, url: str, timeout: int = 120) -> bool:
        """Wait for deployment to be ready."""
        import requests
        import time
        
        start_time = time.time()
        attempt = 0
        max_attempts = timeout // 10  # Check every 10 seconds
        
        print(f"Checking deployment readiness (max {max_attempts} attempts, {timeout}s timeout)...")
        
        while time.time() - start_time < timeout and attempt < max_attempts:
            attempt += 1
            try:
                print(f"Attempt {attempt}/{max_attempts}: Checking {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Deployment ready after {attempt} attempts")
                    return True
                else:
                    print(f"   Status: {response.status_code}")
            except requests.RequestException as e:
                print(f"   Connection failed: {type(e).__name__}")
            
            if attempt < max_attempts:
                time.sleep(10)
        
        print(f"❌ Deployment not ready after {timeout}s timeout")
        return False
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get comprehensive deployment information."""
        return {
            'type': self.deployment_type,
            'repo_name': self.repo_name,
            'pr_number': self.pr_number,
            'preview_url': self.get_preview_url(),
            'base_url': self.get_base_url(),
            'ready': False  # Will be updated after deployment check
        }


def main():
    """Main function for testing deployment integration."""
    deployment = DeploymentIntegration()
    info = deployment.get_deployment_info()
    
    print(f"Deployment Type: {info['type']}")
    print(f"Repository: {info['repo_name']}")
    print(f"PR Number: {info['pr_number']}")
    print(f"Preview URL: {info['preview_url']}")
    print(f"Base URL: {info['base_url']}")
    
    # Check if we're in test mode (skip deployment wait)
    test_mode = os.getenv('TEST_MODE', '').lower() == 'true'
    
    if test_mode:
        print("\n🧪 Test mode enabled - skipping deployment wait")
        info['ready'] = False
    else:
        # Test if preview URL is accessible
        preview_url = info['preview_url']
        if preview_url:
            print(f"\nWaiting for deployment at {preview_url}...")
            if deployment.wait_for_deployment(preview_url):
                print("✅ Deployment is ready!")
                info['ready'] = True
            else:
                print("❌ Deployment timeout or failed")
                info['ready'] = False
    
    # Output JSON for use in other scripts
    print("\nJSON Output:")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
