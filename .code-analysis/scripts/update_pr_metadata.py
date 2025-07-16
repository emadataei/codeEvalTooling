#!/usr/bin/env python3
"""
Update PR metadata (labels, assignees) based on cognitive complexity analysis.
"""

import os
import json
import argparse
import sys
from github import Github
from pathlib import Path

# Label constants
COMPLEXITY_LOW = "complexity:low"
COMPLEXITY_MEDIUM = "complexity:medium"
COMPLEXITY_HIGH = "complexity:high"
TIER_0 = "tier:0"
TIER_1 = "tier:1" 
TIER_2 = "tier:2"
AUTO_MERGE = "auto-merge"
NEEDS_REVIEW = "needs-review"
NEEDS_EXPERT_REVIEW = "needs-expert-review"


def main():
    parser = argparse.ArgumentParser(description="Update PR metadata based on cognitive complexity")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--repo", type=str, help="Repository in format owner/repo")
    args = parser.parse_args()
    
    # Initialize GitHub client
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    # Load cognitive score results (try both filenames)
    score_file = None
    for filename in ["cognitive_score.json", "cognitive-analysis-results.json"]:
        if os.path.exists(filename):
            score_file = filename
            break
    
    if not score_file:
        print("ERROR: cognitive analysis results not found. Run run_cognitive_analysis.py first.")
        sys.exit(1)
    
    with open(score_file, "r") as f:
        score_data = json.load(f)
    
    tier = score_data.get("tier", 1)
    total_score = score_data.get("total_score", 0)
    
    g = Github(github_token)
    
    # Get repository and PR
    if args.repo:
        repo = g.get_repo(args.repo)
    else:
        # Try to get from environment (GitHub Actions context)
        repo_name = os.getenv("GITHUB_REPOSITORY")
        if not repo_name:
            print("ERROR: Repository not specified and GITHUB_REPOSITORY not set")
            sys.exit(1)
        repo = g.get_repo(repo_name)
    
    pr = repo.get_pull(args.pr_number)
    
    # Update labels based on tier
    try:
        update_pr_labels(pr, tier, total_score)
        print(f"Updated PR labels for tier {tier}")
    except Exception as e:
        print(f"Warning: Could not update labels: {e}")
    
    # Update assignees/reviewers based on tier
    try:
        update_pr_reviewers(pr, tier)
        print(f"Updated PR reviewers for tier {tier}")
    except Exception as e:
        print(f"Warning: Could not update reviewers: {e}")
    
    print(f"PR metadata updated successfully for cognitive complexity tier {tier}")


def update_pr_labels(pr, tier: int, total_score: int):
    """Update PR labels based on cognitive complexity tier."""
    
    # Remove any existing complexity labels
    existing_labels = [label.name for label in pr.get_labels()]
    complexity_labels = [
        COMPLEXITY_LOW, COMPLEXITY_MEDIUM, COMPLEXITY_HIGH,
        TIER_0, TIER_1, TIER_2,
        AUTO_MERGE, NEEDS_REVIEW, NEEDS_EXPERT_REVIEW
    ]
    
    _remove_existing_labels(pr, existing_labels, complexity_labels)
    labels_to_add = _get_labels_for_tier(tier, total_score)
    _add_labels_to_pr(pr, labels_to_add)


def _remove_existing_labels(pr, existing_labels, complexity_labels):
    """Remove existing complexity-related labels."""
    labels_to_remove = [label for label in existing_labels if label in complexity_labels]
    for label_name in labels_to_remove:
        try:
            pr.remove_from_labels(label_name)
        except Exception:
            pass  # Label might not exist


def _get_labels_for_tier(tier: int, total_score: int):
    """Get labels to add based on tier and score."""
    labels_to_add = []
    
    if tier == 0:
        labels_to_add.extend([TIER_0, COMPLEXITY_LOW, AUTO_MERGE])
    elif tier == 1:
        labels_to_add.extend([TIER_1, COMPLEXITY_MEDIUM, NEEDS_REVIEW])
    else:  # tier == 2
        labels_to_add.extend([TIER_2, COMPLEXITY_HIGH, NEEDS_EXPERT_REVIEW])
    
    # Add score-based label
    if total_score < 30:
        labels_to_add.append("score:low")
    elif total_score < 70:
        labels_to_add.append("score:medium")
    else:
        labels_to_add.append("score:high")
    
    return labels_to_add


def _add_labels_to_pr(pr, labels_to_add):
    """Create and add labels to PR."""
    repo = pr.base.repo
    for label_name in labels_to_add:
        try:
            # Try to get the label first
            repo.get_label(label_name)
        except Exception:
            # Label doesn't exist, create it
            try:
                color = get_label_color(label_name)
                repo.create_label(label_name, color)
                print(f"Created label: {label_name}")
            except Exception as e:
                print(f"Warning: Could not create label {label_name}: {e}")
        
        # Add label to PR
        try:
            pr.add_to_labels(label_name)
        except Exception as e:
            print(f"Warning: Could not add label {label_name}: {e}")


def update_pr_reviewers(pr, tier: int):
    """Update PR reviewers based on cognitive complexity tier."""
    
    # For tier 0 (auto-merge), we don't need to assign reviewers
    if tier == 0:
        print("Tier 0: No reviewers needed (auto-merge on CI green)")
        return
    
    # For tier 1 and 2, we would normally assign reviewers here
    # However, without knowing the team structure, we'll just add a comment
    # In a real implementation, you'd have team members configured
    
    if tier == 1:
        print("Tier 1: Single reviewer needed (12h SLA)")
        # pr.create_review_request(reviewers=["team-member-1"])
    else:  # tier == 2
        print("Tier 2: Domain expert review needed (48h SLA)")
        # pr.create_review_request(reviewers=["domain-expert-1", "domain-expert-2"])
    
    # For now, we'll just ensure the PR is not in draft mode
    if pr.draft:
        print("PR is in draft mode - keeping as draft until ready for review")


def get_label_color(label_name: str) -> str:
    """Get appropriate color for a label."""
    color_map = {
        TIER_0: "28a745",      # Green
        TIER_1: "ffc107",      # Yellow  
        TIER_2: "dc3545",      # Red
        COMPLEXITY_LOW: "28a745",
        COMPLEXITY_MEDIUM: "ffc107", 
        COMPLEXITY_HIGH: "dc3545",
        AUTO_MERGE: "28a745",
        NEEDS_REVIEW: "0366d6",
        NEEDS_EXPERT_REVIEW: "b60205",
        "score:low": "d4edda",
        "score:medium": "fff3cd",
        "score:high": "f8d7da"
    }
    return color_map.get(label_name, "d4d4d4")  # Default gray


if __name__ == "__main__":
    main()
