#!/usr/bin/env python3
"""
Quality Gate Analysis Script for GitHub Actions.

This script analyzes changed files with the Quality Gate system
and outputs results for GitHub Actions workflows.
"""

import sys
import json
import os
from pathlib import Path

# Add .code-analysis to Python path (script is now inside .code-analysis/scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    
    # Parse file list (GitHub Actions passes space-separated files)
    changed_files = [f.strip() for f in file_list.split() if f.strip()]
    print(f"DEBUG: Parsed {len(changed_files)} files: {changed_files}")
    
    # Filter for code files and read content
    pr_files = []
    
    for file_path in changed_files:
        try:
            print(f"DEBUG: Checking file: {file_path}")
            if not os.path.exists(file_path):
                print(f"DEBUG: File does not exist: {file_path}")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine language from extension
            ext = Path(file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.jsx': 'javascript',
                '.tsx': 'typescript',
                '.java': 'java',
                '.cs': 'csharp',
                '.go': 'go',
                '.rs': 'rust'
            }
            
            language = language_map.get(ext, 'unknown')
            
            print(f"DEBUG: Added file {file_path} with language {language}")
            pr_files.append({
                'path': file_path,
                'content': content,
                'language': language
            })
            
        except Exception as e:
            # Skip files that can't be read
            print(f"DEBUG: Error reading file {file_path}: {e}")
            continue
    
    print(f"DEBUG: Total valid code files: {len(pr_files)}")
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

    # Run quality gate analysis with AI enabled
    # Set enable_ai=False to disable AI analysis for faster execution
    enable_ai = os.getenv('QUALITY_GATE_AI_ENABLED', 'true').lower() == 'true'
    
    print(f"DEBUG: AI enabled: {enable_ai}")
    try:
        quality_gate = QualityGate(enable_ai=enable_ai)
        print("DEBUG: QualityGate initialized successfully")
    except Exception as e:
        print(f"DEBUG: Error initializing QualityGate: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    try:
        result = quality_gate.analyze_pr(pr_files)
        print("DEBUG: Quality gate analysis completed successfully")
        print(f"DEBUG: Result passed: {result.passed}, score: {result.quality_score}")
    except Exception as e:
        print(f"DEBUG: Error during quality gate analysis: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Get standards information for enhanced reporting
    standards_info = {}
    if enable_ai:
        try:
            print("DEBUG: Getting standards information...")
            standards = quality_gate.copilot_parser.get_standards()
            emphasis_areas = []
            if standards.error_handling_required:
                emphasis_areas.append('Error Handling')
            if standards.type_safety_emphasis:
                emphasis_areas.append('Type Safety')
            if standards.performance_focus:
                emphasis_areas.append('Performance')
            if standards.documentation_required:
                emphasis_areas.append('Documentation')
            if standards.testing_emphasis:
                emphasis_areas.append('Testing')
        
            standards_info = {
                'standards_applied': True,
                'emphasis_areas': emphasis_areas
            }
            print("DEBUG: Standards information retrieved successfully")
        except Exception as e:
            print(f"DEBUG: Error getting standards: {e}")
            standards_info = {'standards_applied': False}
    else:
        standards_info = {'standards_applied': False}
    
    # Convert to format expected by GitHub Actions
    print("DEBUG: Converting result to GitHub Actions format...")
    try:
        result_dict = {
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
                    }
                    for issue in result.blocking_issues
                ],
                'warning': [
                    {
                        'category': issue.category,
                        'message': issue.message,
                        'file': issue.file_path,
                        'line': issue.line_number,
                        'suggestion': issue.suggestion
                    }
                    for issue in result.warning_issues
                ]
            }
        }
        print("DEBUG: Result conversion completed successfully")
    except Exception as e:
        print(f"DEBUG: Error converting result: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Add standards information
    result_dict.update(standards_info)
    
    return result_dict


def main():
    """Main entry point for GitHub Actions."""
    try:
        changed_files = os.getenv('CHANGED_FILES', '')
        print(f"DEBUG: CHANGED_FILES env var: '{changed_files}'")
        print(f"DEBUG: Working directory: {os.getcwd()}")
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
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
