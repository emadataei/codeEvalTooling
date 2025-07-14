#!/usr/bin/env python3
import os
import json
import argparse
from github import Github
from pathlib import Path
import sys

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from scoring.cognitive_analyzer import CognitiveAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Analyze PR cognitive complexity")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--repo", type=str, required=True)
    args = parser.parse_args()
    
    # Initialize GitHub client
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    g = Github(github_token)
    repo = g.get_repo(args.repo)
    pr = repo.get_pull(args.pr_number)
    
    # Get PR files
    pr_files = []
    for file in pr.get_files():
        if file.patch:  # Only analyze files with changes
            try:
                # Get file content
                content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode('utf-8')
                
                pr_files.append({
                    'path': file.filename,
                    'content': content,
                    'changes': file.changes,
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'language': _detect_language(file.filename)
                })
            except Exception as e:
                print(f"Warning: Could not analyze file {file.filename}: {e}")
    
    # Analyze cognitive complexity using AI Foundry
    analyzer = CognitiveAnalyzer()
    score = analyzer.analyze_pr(pr_files)
    
    # Save results for other workflow steps
    with open("cognitive_score.json", "w") as f:
        json.dump({
            "static_score": score.static_score,
            "impact_score": score.impact_score,
            "ai_score": score.ai_score,
            "total_score": score.total_score,
            "tier": score.tier,
            "reasoning": score.reasoning,
            "ai_provider": "ai_foundry"
        }, f, indent=2)
    
    print(f"Cognitive Score: {score.total_score}/100 (Tier {score.tier})")
    print(f"Using AI Provider: ai_foundry")
    print(f"Reasoning: {score.reasoning}")

def _detect_language(filename: str) -> str:
    """Simple language detection based on file extension"""
    ext = Path(filename).suffix.lower()
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c'
    }
    return lang_map.get(ext, 'unknown')

if __name__ == "__main__":
    main()
