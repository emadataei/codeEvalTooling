#!/usr/bin/env python3
"""
Generate UI Screenshots for Changed Files
Creates screenshots of pages that have UI changes for visual review.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class UIScreenshotGenerator:
    """Generates screenshots of UI changes for visual review."""
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Get project info
        self.pr_number = os.getenv('PR_NUMBER', '0')
        self.project_dir = Path("sample-project")
        
        # Load UI analysis results
        self.analysis_results = self._load_analysis_results()
        
    def _load_analysis_results(self) -> Dict:
        """Load the UI analysis results from the previous step."""
        try:
            with open('visual-diff-results.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("No UI analysis results found. Skipping screenshot generation.")
            return {}
    
    def _get_screenshot_pages(self) -> List[Dict]:
        """Determine which pages to screenshot based on changed files."""
        pages = []
        
        if not self.analysis_results.get('has_ui_changes'):
            return pages
        
        ui_files = self.analysis_results.get('ui_files', [])
        
        # Main pages to always screenshot if any UI changes
        main_pages = [
            {'name': 'home', 'path': '/', 'description': 'Home page'},
        ]
        
        # Add specific pages based on changed files
        for file_path in ui_files:
            if 'page.tsx' in file_path:
                # Extract route from file path
                route = self._extract_route_from_file(file_path)
                if route and route != '/':
                    pages.append({
                        'name': route.replace('/', '').replace('-', '_') or 'root',
                        'path': route,
                        'description': f'Page: {route}'
                    })
        
        # Always include main pages
        pages.extend(main_pages)
        
        # Remove duplicates
        seen = set()
        unique_pages = []
        for page in pages:
            if page['path'] not in seen:
                seen.add(page['path'])
                unique_pages.append(page)
        
        return unique_pages
    
    def _extract_route_from_file(self, file_path: str) -> str:
        """Extract the route from a file path."""
        # For Next.js app router: src/app/some-page/page.tsx -> /some-page
        if 'src/app' in file_path:
            parts = file_path.split('src/app')[1].split('/')
            # Remove empty parts and page.tsx
            route_parts = [p for p in parts if p and p != 'page.tsx']
            return '/' + '/'.join(route_parts) if route_parts else '/'
        
        return '/'
    
    def _start_dev_server(self) -> subprocess.Popen:
        """Start the development server for screenshot generation."""
        print("Starting development server...")
        
        # Change to project directory and start server
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=self.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        import time
        time.sleep(10)  # Give server time to start
        
        return process
    
    def _generate_screenshot(self, page: Dict) -> Optional[str]:
        """Generate a screenshot for a specific page."""
        page_name = page['name']
        page_path = page['path']
        
        # Create playwright script
        playwright_script = f"""
const {{ chromium }} = require('playwright');

(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {{
    await page.setViewportSize({{ width: 1280, height: 720 }});
    await page.goto('http://localhost:3000{page_path}', {{ waitUntil: 'networkidle' }});
    
    // Wait a bit for dynamic content
    await page.waitForTimeout(2000);
    
    await page.screenshot({{ 
      path: 'screenshots/{page_name}.png',
      fullPage: true
    }});
    
    console.log('Screenshot saved: {page_name}.png');
  }} catch (error) {{
    console.error('Error capturing {page_name}:', error.message);
  }} finally {{
    await browser.close();
  }}
}})();
"""
        
        # Write and execute the script
        script_path = self.screenshots_dir / f"{page_name}_screenshot.js"
        with open(script_path, 'w') as f:
            f.write(playwright_script)
        
        try:
            result = subprocess.run(
                ['node', str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                screenshot_path = self.screenshots_dir / f"{page_name}.png"
                if screenshot_path.exists():
                    print(f"✅ Screenshot generated: {page_name}.png")
                    return str(screenshot_path)
                else:
                    print(f"❌ Screenshot file not found: {page_name}.png")
            else:
                print(f"❌ Screenshot failed for {page_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"❌ Screenshot timeout for {page_name}")
        except Exception as e:
            print(f"❌ Screenshot error for {page_name}: {e}")
        
        finally:
            # Clean up script
            if script_path.exists():
                script_path.unlink()
        
        return None
    
    def generate_all_screenshots(self) -> List[str]:
        """Generate screenshots for all relevant pages."""
        if not self.analysis_results.get('has_ui_changes'):
            print("No UI changes detected. Skipping screenshot generation.")
            return []
        
        pages = self._get_screenshot_pages()
        if not pages:
            print("No pages to screenshot.")
            return []
        
        print(f"Generating screenshots for {len(pages)} pages...")
        
        # Start development server
        dev_server = None
        screenshots = []
        
        try:
            dev_server = self._start_dev_server()
            
            # Generate screenshots
            for page in pages:
                print(f"Capturing screenshot for {page['description']}...")
                screenshot_path = self._generate_screenshot(page)
                if screenshot_path:
                    screenshots.append(screenshot_path)
        
        finally:
            # Stop development server
            if dev_server:
                dev_server.terminate()
                dev_server.wait()
        
        # Generate manifest
        self._generate_manifest(screenshots, pages)
        
        # Upload screenshots to GitHub's comment system for embedding
        self._upload_to_github_comments(screenshots)
        
        return screenshots
    
    def _generate_manifest(self, screenshots: List[str], pages: List[Dict]):
        """Generate a manifest of all screenshots."""
        manifest = {
            'pr_number': self.pr_number,
            'generated_at': None,
            'ui_changes': self.analysis_results.get('categories', {}),
            'screenshots': []
        }
        
        # Add timestamp
        from datetime import datetime, timezone
        manifest['generated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Add screenshot info
        for i, screenshot_path in enumerate(screenshots):
            page = pages[i] if i < len(pages) else {'name': 'unknown', 'path': '/', 'description': 'Unknown page'}
            manifest['screenshots'].append({
                'filename': os.path.basename(screenshot_path),
                'page_name': page['name'],
                'page_path': page['path'],
                'description': page['description']
            })
        
        # Save manifest
        manifest_path = self.screenshots_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Screenshot manifest saved: {manifest_path}")
    
    def _upload_to_github_comments(self, screenshots: List[str]):
        """Upload screenshots to GitHub's comment system for embedding."""
        import base64
        
        # Create a JSON file with image data that can be embedded in comments
        image_data = {}
        
        for screenshot_path in screenshots:
            try:
                # Read the image file
                with open(screenshot_path, 'rb') as f:
                    image_bytes = f.read()
                
                # Encode as base64 for embedding
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                filename = os.path.basename(screenshot_path)
                
                # Store the base64 data for embedding in PR comment
                image_data[filename] = f"data:image/png;base64,{image_b64}"
                
            except Exception as e:
                print(f"Failed to process {screenshot_path}: {e}")
                continue
        
        # Save the image data for the PR comment script
        with open('screenshot_urls.json', 'w') as f:
            json.dump(image_data, f, indent=2)
        
        print(f"Processed {len(image_data)} screenshots for embedding")


def main():
    """Main entry point."""
    generator = UIScreenshotGenerator()
    
    try:
        screenshots = generator.generate_all_screenshots()
        
        if screenshots:
            print(f"\n✅ Successfully generated {len(screenshots)} screenshots")
            print("Screenshots saved to:", generator.screenshots_dir)
        else:
            print("\n⚠️  No screenshots generated")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating screenshots: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
