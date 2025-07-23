#!/usr/bin/env python3
"""
Generate Change Heatmap for Enhanced PR Visuals
Reuses existing chart generation utilities
"""

import json
import os
import sys
from pathlib import Path

# Try to import matplotlib, but don't fail if it's not available
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def load_diff_stats():
    """Load git diff statistics"""
    diff_file = '.code-analysis/outputs/diff_stats.txt'
    if not Path(diff_file).exists():
        print(f"No diff stats file found at {diff_file}")
        return []
    
    return _parse_diff_file(diff_file)


def _parse_diff_file(diff_file):
    """Parse the diff statistics file"""
    file_changes = []
    total_additions = 0
    total_deletions = 0
    
    with open(diff_file, 'r') as f:
        for line in f:
            result = _parse_diff_line(line.strip())
            if result:
                change_data, added, deleted = result
                file_changes.append(change_data)
                total_additions += added
                total_deletions += deleted
    
    return file_changes, total_additions, total_deletions


def _parse_diff_line(line):
    """Parse a single line from diff stats"""
    parts = line.split('\t')
    if len(parts) < 3:
        return None
        
    added, deleted, file_path = parts[0], parts[1], parts[2]
    try:
        added_int = int(added) if added != '-' else 0
        deleted_int = int(deleted) if deleted != '-' else 0
        total_changes = added_int + deleted_int
        
        if total_changes > 0:
            change_data = {
                'file': file_path,
                'added': added_int,
                'deleted': deleted_int,
                'total': total_changes
            }
            return change_data, added_int, deleted_int
    except ValueError:
        pass
    
    return None


def categorize_files(file_changes):
    """Categorize files by type and extract metadata"""
    df = pd.DataFrame(file_changes)
    
    if df.empty:
        return df
    
    # Extract directory structure
    df['directory'] = df['file'].apply(lambda x: '/'.join(Path(x).parts[:-1]) if '/' in x else 'root')
    df['filename'] = df['file'].apply(lambda x: Path(x).name)
    df['extension'] = df['file'].apply(lambda x: Path(x).suffix)
    
    # Categorize by file type
    def categorize_file(file_path):
        path_lower = file_path.lower()
        if any(ext in path_lower for ext in ['.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte']):
            return 'Source Code'
        elif any(ext in path_lower for ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.env']):
            return 'Configuration'
        elif any(ext in path_lower for ext in ['.md', '.txt', '.rst', '.doc']):
            return 'Documentation'
        elif any(term in path_lower for term in ['test', 'spec', '__tests__']):
            return 'Tests'
        else:
            return 'Other'
    
    df['category'] = df['file'].apply(categorize_file)
    
    return df


def generate_change_heatmap():
    """Generate a comprehensive change heatmap visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, creating placeholder")
        create_simple_placeholder()
        return False
    
    print("Generating change heatmap...")
    
    # Load and process data
    file_changes, total_additions, total_deletions = load_diff_stats()
    
    if not file_changes:
        print("No file changes to visualize")
        create_no_changes_placeholder()
        return False
    
    # Convert to DataFrame and categorize
    df = categorize_files(file_changes)
    
    if df.empty:
        create_no_changes_placeholder()
        return False
    
    # Create visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Top changed files
    top_files = df.nlargest(10, 'total')
    if not top_files.empty:
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(top_files)))
        bars1 = ax1.barh(range(len(top_files)), top_files['total'], color=colors)
        ax1.set_yticks(range(len(top_files)))
        ax1.set_yticklabels([Path(f).name for f in top_files['file']], fontsize=8)
        ax1.set_xlabel('Lines Changed')
        ax1.set_title('Top 10 Files by Changes')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + max(top_files['total']) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=8)
    
    # 2. Changes by directory
    dir_changes = df.groupby('directory')['total'].sum().sort_values(ascending=False).head(8)
    if len(dir_changes) > 0:
        colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(dir_changes)))
        bars2 = ax2.bar(range(len(dir_changes)), dir_changes.values, color=colors)
        ax2.set_xticks(range(len(dir_changes)))
        ax2.set_xticklabels(dir_changes.index, rotation=45, ha='right', fontsize=8)
        ax2.set_ylabel('Lines Changed')
        ax2.set_title('Changes by Directory')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 3. Changes by file type/category
    category_changes = df.groupby('category')['total'].sum().sort_values(ascending=False)
    if len(category_changes) > 0:
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_changes)))
        _, _, autotexts = ax3.pie(category_changes.values, labels=category_changes.index, 
                                 autopct='%1.1f%%', colors=colors, startangle=90)
        ax3.set_title('Changes by Category')
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # 4. Addition vs Deletion breakdown
    summary_data = pd.DataFrame({
        'Type': ['Additions', 'Deletions'],
        'Lines': [total_additions, total_deletions]
    })
    colors = ['#2ecc71', '#e74c3c']
    bars4 = ax4.bar(summary_data['Type'], summary_data['Lines'], color=colors)
    ax4.set_ylabel('Lines')
    ax4.set_title('Additions vs Deletions')
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Add overall statistics as suptitle
    total_files = len(file_changes)
    total_changes = total_additions + total_deletions
    fig.suptitle(f'Change Analysis: {total_files} files, {total_changes} total lines (+{total_additions}/-{total_deletions})', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('.code-analysis/outputs/change_heatmap.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Heatmap generated with {len(file_changes)} changed files")
    print(f"📊 Total: +{total_additions}/-{total_deletions} lines")
    
    # Save analysis results
    results = {
        'total_files': total_files,
        'total_additions': total_additions,
        'total_deletions': total_deletions,
        'total_changes': total_changes,
        'top_files': top_files.head(5).to_dict('records') if not top_files.empty else [],
        'category_breakdown': category_changes.to_dict() if len(category_changes) > 0 else {}
    }
    
    with open('.code-analysis/outputs/change_heatmap_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return True


def create_simple_placeholder():
    """Create a simple text-based placeholder"""
    placeholder_content = """
# Change Heatmap Placeholder

Matplotlib is not available for generating visual heatmaps.

## Summary
- Check `.code-analysis/outputs/diff_stats.txt` for raw change data
- Visual heatmap generation requires matplotlib, seaborn, and pandas

## Alternative
Run `pip install matplotlib seaborn pandas` to enable visual heatmaps.
"""
    
    with open('.code-analysis/outputs/change_heatmap_placeholder.md', 'w') as f:
        f.write(placeholder_content)
    
    print("📋 Created text placeholder for change heatmap")


def create_no_changes_placeholder():
    """Create placeholder when no changes are detected"""
    if MATPLOTLIB_AVAILABLE:
        _, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.text(0.5, 0.5, 'No File Changes Detected', ha='center', va='center', 
                fontsize=20, fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.3, 'This PR may contain only non-code changes\nor the diff analysis failed', 
                ha='center', va='center', fontsize=12, style='italic', transform=ax.transAxes)
        ax.set_title('Change Heatmap', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig('.code-analysis/outputs/change_heatmap.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    print("Created no-changes placeholder")


def main():
    """Main heatmap generation logic"""
    print("Starting change heatmap generation...")
    
    # Ensure output directory exists
    os.makedirs('.code-analysis/outputs', exist_ok=True)
    
    success = generate_change_heatmap()
    
    print("Change heatmap generation complete!")
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
