#!/usr/bin/env python3
"""
Cognitive Analysis Script for GitHub Actions.

This script runs cognitive complexity analysis on changed files
and outputs results for GitHub Actions workflows.
"""

import sys
import json
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Try to import cognitive analyzer, fallback if dependencies missing
try:
    from scoring.cognitive_analyzer import CognitiveAnalyzer, CognitiveScore
    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False
    # Create a dummy CognitiveScore for fallback
    from dataclasses import dataclass
    
    @dataclass
    class CognitiveScore:
        static_score: int
        impact_score: int  
        ai_score: int
        total_score: int
        tier: int
        reasoning: str


def run_cognitive_analysis(file_list, quality_penalty=0):
    """Run cognitive analysis on changed files."""
    if not file_list.strip():
        print("No code files changed, assigning Tier 0")
        return {
            'tier': 0,
            'total_score': 0,
            'reasoning': 'No code changes detected',
            'static_score': 0,
            'impact_score': 0,
            'ai_score': 0,
            'quality_penalty': 0
        }
    
    try:
        if COGNITIVE_AVAILABLE:
            analyzer = CognitiveAnalyzer()
        else:
            raise ImportError("Cognitive analyzer dependencies not available")
    except Exception as e:
        print(f"Warning: Could not initialize AI client: {e}")
        print("Falling back to static analysis only")
        # Create a minimal analyzer without AI
        class MinimalAnalyzer:
            def analyze_pr(self, _files):
                return CognitiveScore(
                    static_score=10,
                    impact_score=5,
                    ai_score=0,
                    total_score=15 + quality_penalty,
                    tier=0 if 15 + quality_penalty <= 25 else 1,
                    reasoning="Static analysis only (AI unavailable)"
                )
        analyzer = MinimalAnalyzer()
    
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
            
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
    
    if not pr_files:
        print("No valid code files found")
        return {
            'tier': 0,
            'total_score': quality_penalty,
            'reasoning': 'No valid code files to analyze',
            'static_score': 0,
            'impact_score': 0,
            'ai_score': 0,
            'quality_penalty': quality_penalty
        }
    
    # Run cognitive analysis
    result = analyzer.analyze_pr(pr_files)
    
    # Add quality penalty to total score
    adjusted_total = result.total_score + quality_penalty
    
    # Recalculate tier with penalty
    if adjusted_total <= 25:
        tier = 0
    elif adjusted_total <= 65:
        tier = 1
    else:
        tier = 2
    
    # Update reasoning with quality penalty info
    reasoning = result.reasoning
    if quality_penalty > 0:
        reasoning += f" (Quality penalty: +{quality_penalty} points)"
    
    return {
        'tier': tier,
        'total_score': adjusted_total,
        'reasoning': reasoning,
        'static_score': result.static_score,
        'impact_score': result.impact_score,
        'ai_score': result.ai_score,
        'quality_penalty': quality_penalty
    }


def main():
    """Main entry point for the script."""
    changed_files = os.getenv('CHANGED_FILES', '')
    
    # Load quality penalty from quality gate results
    quality_penalty = 0
    try:
        with open('quality-gate-results.json', 'r') as f:
            quality_results = json.load(f)
            quality_penalty = quality_results.get('penalty', 0)
            print(f"Quality penalty from gate: {quality_penalty}")
    except Exception as e:
        print(f"Could not load quality results: {e}")
    
    result = run_cognitive_analysis(changed_files, quality_penalty)
    
    # Output results for GitHub Actions
    print("Cognitive Analysis Result:")
    print(f"  Tier: {result['tier']}")
    print(f"  Total Score: {result['total_score']}")
    print(f"  Reasoning: {result['reasoning']}")
    
    # Set outputs for GitHub Actions
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"tier={result['tier']}\n")
            f.write(f"total_score={result['total_score']}\n")
            f.write(f"reasoning={result['reasoning']}\n")
    
    # Create detailed results file
    with open('cognitive-analysis-results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nCognitive Analysis Complete - Assigned to Tier {result['tier']}")


if __name__ == '__main__':
    main()
