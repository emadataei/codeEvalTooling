#!/usr/bin/env python3
"""
Quality Gate Analysis Script for GitHub Actions.

This script analyzes changed files with the Quality Ga    # Exit with error code if quality gate fails
    if not result['passed']:
        sys.exit(1)


if __name__ == '__main__':
    main()ts results for GitHub Actions workflows.
"""

import sys
import json
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scoring.quality_gate import QualityGate


def analyze_changed_files(file_list):
    """Analyze changed files with quality gate."""
    if not file_list.strip():
        return {
            'passed': True,
            'score': 100,
            'penalty': 0,
            'blocking_issues': 0,
            'summary': 'No code changes detected',
            'issues': {
                'blocking': [],
                'warning': []
            }
        }
    
    quality_gate = QualityGate()
    pr_files = []
    
    # Process each changed file
    file_paths = file_list.strip().split() if file_list.strip() else []
    for file_path in file_paths:
        if not file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine language from file extension
            ext = Path(file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.java': 'java',
                '.cs': 'csharp',
                '.go': 'go',
                '.rs': 'rust'
            }
            
            language = language_map.get(ext, 'unknown')
            
            pr_files.append({
                'path': file_path,
                'content': content,
                'language': language
            })
            
        except Exception:
            pass  # Skip files that can't be read
    
    if not pr_files:
        return {
            'passed': True,
            'score': 100,
            'penalty': 0,
            'blocking_issues': 0,
            'summary': 'No valid code files to analyze',
            'issues': {
                'blocking': [],
                'warning': []
            }
        }
    
    # Run quality gate analysis
    result = quality_gate.analyze_pr(pr_files)
    
    return {
        'passed': result.passed,
        'score': result.quality_score,
        'penalty': result.quality_penalty,
        'blocking_issues': len(result.blocking_issues),
        'summary': result.summary,
        'issues': {
            'blocking': [
                {
                    'category': issue.category,
                    'message': issue.message,
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'suggestion': issue.suggestion
                } for issue in result.blocking_issues
            ],
            'warning': [
                {
                    'category': issue.category,
                    'message': issue.message,
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'suggestion': issue.suggestion
                } for issue in result.warning_issues
            ]
        }
    }


def main():
    """Main entry point for the script."""
    changed_files = os.getenv('CHANGED_FILES', '')
    result = analyze_changed_files(changed_files)
    
    # Set outputs for GitHub Actions
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"passed={str(result['passed']).lower()}\n")
            f.write(f"score={result['score']}\n")
            f.write(f"penalty={result['penalty']}\n")
            f.write(f"blocking_issues={result['blocking_issues']}\n")
    
    # Create detailed results file
    with open('quality-gate-results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # Exit with error code if quality gate fails
    if not result['passed']:
        sys.exit(1)


if __name__ == '__main__':
    main()
