#!/usr/bin/env python3
"""
Generate Development Flow Visualization for Enhanced PR Visuals
Creates a visual representation of the development workflow and code evolution
"""

import json
import os
import sys
from pathlib import Path
import subprocess
from datetime import datetime

# Try to import matplotlib, but don't fail if it's not available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import matplotlib.dates as mdates
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def run_git_command(command):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Git command failed: {command}")
            return None
    except subprocess.TimeoutExpired:
        print(f"Git command timed out: {command}")
        return None
    except Exception as e:
        print(f"Error running git command: {e}")
        return None


def get_commit_history():
    """Get commit history for the current branch"""
    # Get commits from the last 30 days or up to 20 commits, whichever is less
    cmd = 'git log --oneline --date=short --pretty=format:"%h|%ad|%s|%an" --since="30 days ago" -20'
    output = run_git_command(cmd)
    
    if not output:
        return []
    
    commits = []
    for line in output.split('\n'):
        if '|' in line:
            parts = line.split('|', 3)
            if len(parts) >= 4:
                commits.append({
                    'hash': parts[0],
                    'date': parts[1],
                    'message': parts[2],
                    'author': parts[3]
                })
    
    return commits


def categorize_commit(commit_message):
    """Categorize commits by type based on message"""
    message_lower = commit_message.lower()
    
    if any(keyword in message_lower for keyword in ['feat', 'feature', 'add']):
        return 'Feature'
    elif any(keyword in message_lower for keyword in ['fix', 'bug', 'hotfix']):
        return 'Bugfix'
    elif any(keyword in message_lower for keyword in ['refactor', 'refact', 'clean']):
        return 'Refactor'
    elif any(keyword in message_lower for keyword in ['test', 'spec']):
        return 'Testing'
    elif any(keyword in message_lower for keyword in ['doc', 'readme', 'comment']):
        return 'Documentation'
    elif any(keyword in message_lower for keyword in ['style', 'format', 'lint']):
        return 'Style'
    elif any(keyword in message_lower for keyword in ['config', 'setup', 'build']):
        return 'Configuration'
    else:
        return 'Other'


def get_file_changes_over_time():
    """Get file changes over time"""
    cmd = 'git log --oneline --name-status --since="30 days ago" -10'
    output = run_git_command(cmd)
    
    if not output:
        return {}
    
    changes_by_date = {}
    current_date = None
    
    for line in output.split('\n'):
        if line and not line.startswith(('A\t', 'M\t', 'D\t', 'R\t')):
            # This is likely a commit line
            continue
        elif line.startswith(('A\t', 'M\t', 'D\t', 'R\t')):
            # This is a file change line
            change_type = line[0]
            if current_date:
                if current_date not in changes_by_date:
                    changes_by_date[current_date] = {'added': 0, 'modified': 0, 'deleted': 0}
                
                if change_type == 'A':
                    changes_by_date[current_date]['added'] += 1
                elif change_type == 'M':
                    changes_by_date[current_date]['modified'] += 1
                elif change_type == 'D':
                    changes_by_date[current_date]['deleted'] += 1
    
    return changes_by_date


def generate_development_flow():
    """Generate development flow visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, creating placeholder")
        create_placeholder_image()
        return False
    
    print("Generating development flow visualization...")
    
    # Get commit data
    commits = get_commit_history()
    
    if not commits:
        print("No commit history available")
        create_no_commits_image()
        return False
    
    # Process commit data
    commit_types = [categorize_commit(c['message']) for c in commits]
    commit_type_counts = {}
    for ct in commit_types:
        commit_type_counts[ct] = commit_type_counts.get(ct, 0) + 1
    
    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Development Flow Diagram
    create_flow_diagram(ax1, commits)
    
    # 2. Commit Type Distribution
    if commit_type_counts:
        colors = plt.cm.Set3(np.linspace(0, 1, len(commit_type_counts)))
        wedges, texts, autotexts = ax2.pie(commit_type_counts.values(), 
                                          labels=commit_type_counts.keys(),
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Commit Type Distribution')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # 3. Recent Commit Timeline
    create_commit_timeline(ax3, commits)
    
    # 4. Development Activity Summary
    create_activity_summary(ax4, commits, commit_type_counts)
    
    plt.suptitle(f'Development Flow Analysis ({len(commits)} recent commits)', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('.code-analysis/outputs/development_flow.png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Development flow generated for {len(commits)} commits")
    
    # Save results
    results = {
        'total_commits': len(commits),
        'commit_types': commit_type_counts,
        'recent_commits': commits[:5],  # Top 5 most recent
        'analysis_date': datetime.now().isoformat()
    }
    
    with open('.code-analysis/outputs/development_flow_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return True


def create_flow_diagram(ax, commits):
    """Create a simple flow diagram showing development stages"""
    # Define flow stages
    stages = ['Planning', 'Development', 'Testing', 'Review', 'Deploy']
    stage_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
    
    # Create flow diagram
    for i, (stage, color) in enumerate(zip(stages, stage_colors)):
        # Draw stage box
        rect = patches.Rectangle((i * 2, 1), 1.5, 1, linewidth=2, 
                               edgecolor='black', facecolor=color, alpha=0.7)
        ax.add_patch(rect)
        
        # Add stage label
        ax.text(i * 2 + 0.75, 1.5, stage, ha='center', va='center', 
               fontweight='bold', fontsize=10, color='white')
        
        # Add arrow to next stage
        if i < len(stages) - 1:
            ax.arrow(i * 2 + 1.5, 1.5, 0.4, 0, head_width=0.1, head_length=0.1, 
                    fc='black', ec='black')
    
    # Add commit information
    commit_stage_mapping = {
        'Feature': 1, 'Bugfix': 1, 'Refactor': 1,
        'Testing': 2, 'Documentation': 3, 'Configuration': 0, 'Other': 1
    }
    
    # Count commits by stage
    stage_counts = [0] * len(stages)
    for commit in commits:
        commit_type = categorize_commit(commit['message'])
        stage_idx = commit_stage_mapping.get(commit_type, 1)
        stage_counts[stage_idx] += 1
    
    # Add activity indicators
    for i, count in enumerate(stage_counts):
        if count > 0:
            ax.text(i * 2 + 0.75, 0.5, f'{count} commits', ha='center', va='center', 
                   fontsize=8, fontweight='bold')
    
    ax.set_xlim(-0.5, len(stages) * 2 - 0.5)
    ax.set_ylim(0, 3)
    ax.set_title('Development Flow Pipeline')
    ax.axis('off')


def create_commit_timeline(ax, commits):
    """Create a timeline of recent commits"""
    if len(commits) < 2:
        ax.text(0.5, 0.5, 'Insufficient commit history', ha='center', va='center', 
               transform=ax.transAxes, fontsize=12)
        ax.set_title('Recent Commit Timeline')
        ax.axis('off')
        return
    
    # Get commit dates and types
    dates = [commit['date'] for commit in commits[:10]]  # Last 10 commits
    types = [categorize_commit(commit['message']) for commit in commits[:10]]
    
    # Create color map for types
    unique_types = list(set(types))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_types)))
    type_colors = {t: colors[i] for i, t in enumerate(unique_types)}
    
    # Plot timeline
    y_pos = range(len(dates))
    commit_colors = [type_colors[t] for t in types]
    
    ax.scatter([0] * len(dates), y_pos, c=commit_colors, s=100, alpha=0.7)
    
    # Add commit messages (truncated)
    for i, commit in enumerate(commits[:10]):
        message = commit['message'][:40] + '...' if len(commit['message']) > 40 else commit['message']
        ax.text(0.1, i, f"{commit['date']} - {message}", va='center', fontsize=8)
    
    ax.set_xlim(-0.1, 1)
    ax.set_ylim(-0.5, len(dates) - 0.5)
    ax.set_title('Recent Commit Timeline')
    ax.axis('off')


def create_activity_summary(ax, commits, commit_type_counts):
    """Create activity summary"""
    # Calculate activity metrics
    total_commits = len(commits)
    unique_authors = len(set(c['author'] for c in commits))
    most_active_type = max(commit_type_counts.items(), key=lambda x: x[1]) if commit_type_counts else ('None', 0)
    
    # Create summary text
    summary_text = f"""Development Activity Summary

Total Commits: {total_commits}
Unique Authors: {unique_authors}
Most Active Type: {most_active_type[0]} ({most_active_type[1]} commits)

Recent Activity:
• {commit_type_counts.get('Feature', 0)} new features
• {commit_type_counts.get('Bugfix', 0)} bug fixes
• {commit_type_counts.get('Refactor', 0)} refactors
• {commit_type_counts.get('Testing', 0)} test updates
"""
    
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    ax.set_title('Activity Summary')
    ax.axis('off')


def create_placeholder_image():
    """Create placeholder when matplotlib is not available"""
    print("Created development flow placeholder (matplotlib not available)")
    
    with open('.code-analysis/outputs/development_flow_placeholder.md', 'w') as f:
        f.write("""# Development Flow Placeholder

Matplotlib is not available for generating development flow visualizations.

## To Enable Visual Flow Diagrams:
```bash
pip install matplotlib numpy
```

## Alternative Analysis:
Use `git log --oneline --graph` to view commit history.
""")


def create_no_commits_image():
    """Create image when no commits are found"""
    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.text(0.5, 0.5, 'No Recent Commits Found', ha='center', va='center', 
                fontsize=24, fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.3, 'No commit history available for analysis', 
                ha='center', va='center', fontsize=14, style='italic', transform=ax.transAxes)
        ax.set_title('Development Flow', fontsize=18, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig('.code-analysis/outputs/development_flow.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    print("Created no-commits development flow image")


def main():
    """Main development flow generation logic"""
    print("Starting development flow generation...")
    
    # Ensure output directory exists
    os.makedirs('.code-analysis/outputs', exist_ok=True)
    
    success = generate_development_flow()
    
    print("Development flow generation complete!")
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
