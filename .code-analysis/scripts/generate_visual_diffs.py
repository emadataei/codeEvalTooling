#!/usr/bin/env python3
"""
Visual Diff Generator for UI Changes

This script generates visual diffs by taking screenshots of preview environments
and comparing them with the main deployment.
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import base64
from urllib.parse import urljoin

# Add .code-analysis to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from deployment_integration import DeploymentIntegration
    DEPLOYMENT_INTEGRATION_AVAILABLE = True
except ImportError:
    DEPLOYMENT_INTEGRATION_AVAILABLE = False

class VisualDiffGenerator:
    def __init__(self):
        if DEPLOYMENT_INTEGRATION_AVAILABLE:
            self.deployment = DeploymentIntegration()
            self.pr_number = self.deployment.pr_number
            self.repo_name = self.deployment.repo_name
            self.base_url = self.deployment.get_base_url()
            self.preview_url = self.deployment.get_preview_url()
        else:
            # Fallback to environment variables
            self.pr_number = os.environ.get('PR_NUMBER')
            self.repo_name = os.environ.get('GITHUB_REPOSITORY', '').split('/')[-1]
            self.base_url = os.environ.get('BASE_DEPLOYMENT_URL', '')
            self.preview_url = os.environ.get('PREVIEW_DEPLOYMENT_URL', '')
        
        self.output_dir = Path('visual-diffs')
        self.output_dir.mkdir(exist_ok=True)
        
    def get_ui_files(self) -> List[str]:
        """Get list of UI files from changed files"""
        changed_files = os.environ.get('CHANGED_FILES', '')
        ui_extensions = ['.tsx', '.jsx', '.vue', '.svelte', '.css', '.scss', '.less']
        
        ui_files = []
        for file in changed_files.split():
            if any(ext in file.lower() for ext in ui_extensions):
                ui_files.append(file)
        
        return ui_files
    
    def generate_preview_url(self) -> Optional[str]:
        """Generate preview URL from deployment integration"""
        return self.preview_url
    
    async def take_screenshot(self, url: str, filename: str, viewport_size: Tuple[int, int] = (1200, 800)) -> str:
        """Take screenshot of a URL"""
        if not PLAYWRIGHT_AVAILABLE:
            return ""
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={'width': viewport_size[0], 'height': viewport_size[1]})
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for any animations to complete
                await page.wait_for_timeout(2000)
                
                screenshot_path = self.output_dir / f"{filename}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                await browser.close()
                return str(screenshot_path)
                
        except Exception as e:
            print(f"Screenshot failed for {url}: {e}")
            return ""
    
    def generate_github_artifact_url(self, filename: str) -> str:
        """Generate GitHub Actions artifact URL for diff images"""
        repo = os.getenv('GITHUB_REPOSITORY', '')
        run_id = os.getenv('GITHUB_RUN_ID', '')
        
        if repo and run_id:
            # GitHub Actions artifact URL format
            return f"https://github.com/{repo}/actions/runs/{run_id}/artifacts/{filename.replace('visual-diffs/', '')}"
        
        # Fallback to filename only
        return filename
    
    def generate_visual_diff(self, base_screenshot: str, preview_screenshot: str) -> Optional[str]:
        """Generate visual diff between two screenshots"""
        if not base_screenshot or not preview_screenshot:
            return None
            
        try:
            # Use ImageMagick to create a diff
            diff_path = self.output_dir / f"diff-{self.pr_number}.png"
            
            # Simple diff using ImageMagick compare command
            result = subprocess.run([
                'magick', 'compare', 
                base_screenshot, preview_screenshot, 
                str(diff_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return str(diff_path)
            else:
                print(f"ImageMagick compare failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Visual diff generation failed: {e}")
            return None
    
    async def capture_multiple_viewports(self, url: str, name: str) -> List[str]:
        """Capture screenshots at different viewport sizes"""
        viewports = [
            (1200, 800),   # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        screenshots = []
        for i, viewport in enumerate(viewports):
            viewport_name = ['desktop', 'tablet', 'mobile'][i]
            filename = f"{name}-{viewport_name}"
            screenshot = await self.take_screenshot(url, filename, viewport)
            if screenshot:
                screenshots.append({
                    'viewport': viewport_name,
                    'size': f"{viewport[0]}x{viewport[1]}",
                    'path': screenshot
                })
        
        return screenshots
    
    def upload_to_github_artifacts(self, file_path: str) -> str:
        """Upload file to GitHub artifacts and return URL"""
        # This is a placeholder - in reality you'd upload to GitHub artifacts
        # or another hosting service and return the public URL
        return f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ.get('GITHUB_RUN_ID')}/artifacts/{Path(file_path).name}"
    
    async def generate_visual_analysis(self) -> Dict:
        """Generate complete visual analysis"""
        ui_files = self.get_ui_files()
        
        if not ui_files:
            return {
                'has_ui_changes': False,
                'message': 'No UI changes detected'
            }
        
        if not PLAYWRIGHT_AVAILABLE:
            return {
                'has_ui_changes': True,
                'ui_files_count': len(ui_files),
                'message': 'Playwright not available - install with: pip install playwright',
                'manual_preview_url': self.generate_preview_url()
            }
        
        preview_url = self.generate_preview_url()
        if not preview_url:
            return {
                'has_ui_changes': True,
                'ui_files_count': len(ui_files),
                'message': 'No preview URL available'
            }
        
        # Take screenshots of both environments
        base_screenshots = []
        preview_screenshots = []
        
        if self.base_url:
            base_screenshots = await self.capture_multiple_viewports(self.base_url, 'base')
        
        preview_screenshots = await self.capture_multiple_viewports(preview_url, 'preview')
        
        # Generate visual diffs
        visual_diffs = []
        for i, preview_shot in enumerate(preview_screenshots):
            if i < len(base_screenshots):
                diff_path = self.generate_visual_diff(
                    base_screenshots[i]['path'], 
                    preview_shot['path']
                )
                if diff_path:
                    visual_diffs.append({
                        'viewport': preview_shot['viewport'],
                        'diff_url': self.generate_github_artifact_url(str(diff_path))
                    })
        
        return {
            'has_ui_changes': True,
            'ui_files_count': len(ui_files),
            'ui_files': ui_files[:5],  # Show first 5 files
            'preview_url': preview_url,
            'base_url': self.base_url,
            'base_screenshots': [{'viewport': s['viewport'], 'url': self.generate_github_artifact_url(s['path'])} for s in base_screenshots],
            'preview_screenshots': [{'viewport': s['viewport'], 'url': self.generate_github_artifact_url(s['path'])} for s in preview_screenshots],
            'visual_diffs': visual_diffs,
            'message': f'Visual analysis complete for {len(ui_files)} UI files'
        }

def main():
    """Main entry point"""
    async def run_analysis():
        generator = VisualDiffGenerator()
        return await generator.generate_visual_analysis()
    
    results = asyncio.run(run_analysis())
    
    # Save results for the GitHub Action
    with open('visual-diff-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Visual diff analysis complete. UI changes: {results['has_ui_changes']}")
    if results.get('ui_files_count'):
        print(f"UI files analyzed: {results['ui_files_count']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
