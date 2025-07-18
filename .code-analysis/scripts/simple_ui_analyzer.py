#!/usr/bin/env python3
"""
Simple UI Change Detector
Just detects UI file changes and creates a simple report - no screenshots needed.
"""

import os
import sys
import json
from typing import List, Dict


class SimpleUIAnalyzer:
    """Simple UI change analyzer that doesn't require deployments"""
    
    def __init__(self):
        self.pr_number = os.getenv('PR_NUMBER', '0')
        self.repo_name = os.getenv('GITHUB_REPOSITORY', '').split('/')[-1]
        
    def get_ui_files(self) -> List[str]:
        """Get list of UI files from changed files"""
        changed_files = os.getenv('CHANGED_FILES', '')
        ui_extensions = ['.tsx', '.jsx', '.vue', '.svelte', '.css', '.scss', '.less', '.sass']
        
        ui_files = []
        for file in changed_files.split():
            if any(file.lower().endswith(ext) for ext in ui_extensions):
                ui_files.append(file)
        
        return ui_files
    
    def categorize_ui_changes(self, ui_files: List[str]) -> Dict:
        """Categorize UI changes by type"""
        categories = {
            'components': [],
            'styles': [],
            'pages': []
        }
        
        for file in ui_files:
            file_lower = file.lower()
            if any(ext in file_lower for ext in ['.css', '.scss', '.less', '.sass']):
                categories['styles'].append(file)
            elif any(path in file_lower for path in ['/page', '/layout', '/app/']):
                categories['pages'].append(file)
            else:
                categories['components'].append(file)
        
        return categories
    
    def generate_analysis(self) -> Dict:
        """Generate simple UI analysis without deployment complexity"""
        ui_files = self.get_ui_files()
        
        if not ui_files:
            return {
                'has_ui_changes': False,
                'ui_files_count': 0,
                'ui_files': [],
                'categories': {'components': [], 'styles': [], 'pages': []},
                'message': 'No UI files changed'
            }
        
        categories = self.categorize_ui_changes(ui_files)
        
        return {
            'has_ui_changes': True,
            'ui_files_count': len(ui_files),
            'ui_files': ui_files,
            'categories': categories,
            'message': f'Found {len(ui_files)} UI file changes'
        }


def main():
    """Main entry point"""
    analyzer = SimpleUIAnalyzer()
    results = analyzer.generate_analysis()
    
    # Save results for the GitHub Action
    with open('visual-diff-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"UI analysis complete. Changes detected: {results['has_ui_changes']}")
    if results.get('ui_files_count'):
        print(f"UI files analyzed: {results['ui_files_count']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
