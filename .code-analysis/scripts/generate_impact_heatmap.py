#!/usr/bin/env python3
"""
Generate Impact Heatmap for Enhanced PR Visuals
Creates a visual representation of code change impact across different dimensions
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
    
    file_changes = []
    with open(diff_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                try:
                    added = int(parts[0]) if parts[0] != '-' else 0
                    deleted = int(parts[1]) if parts[1] != '-' else 0
                    file_path = parts[2]
                    
                    if added > 0 or deleted > 0:
                        file_changes.append({
                            'file': file_path,
                            'added': added,
                            'deleted': deleted,
                            'total': added + deleted
                        })
                except ValueError:
                    continue
    
    return file_changes


def categorize_file_impact(file_path):
    """Categorize files by their potential impact level"""
    path_lower = file_path.lower()
    
    # Critical system files
    if any(pattern in path_lower for pattern in [
        'package.json', 'requirements.txt', 'dockerfile', 'docker-compose',
        '.github/workflows', 'makefile', 'webpack.config', 'vite.config',
        'next.config', 'tsconfig.json', 'babel.config'
    ]):
        return 'Critical Infrastructure'
    
    # Core application logic
    elif any(pattern in path_lower for pattern in [
        'src/app', 'src/core', 'src/lib', 'src/utils', 'src/services',
        'lib/', 'core/', 'api/', 'server/', 'backend/'
    ]):
        return 'Core Logic'
    
    # User interface components
    elif any(pattern in path_lower for pattern in [
        'components/', 'pages/', 'views/', 'templates/', 'ui/',
        '.tsx', '.jsx', '.vue', '.svelte'
    ]):
        return 'User Interface'
    
    # Testing files
    elif any(pattern in path_lower for pattern in [
        'test', 'spec', '__tests__', '.test.', '.spec.',
        'cypress/', 'jest/', 'vitest/'
    ]):
        return 'Testing'
    
    # Documentation and configuration
    elif any(pattern in path_lower for pattern in [
        '.md', '.txt', '.rst', 'readme', 'changelog', 'license',
        '.env', '.yml', '.yaml', '.toml', '.ini'
    ]):
        return 'Documentation/Config'
    
    else:
        return 'Other'


def calculate_risk_level(total_changes, file_category):
    """Calculate risk level based on changes and file category"""
    # Base risk from number of changes
    if total_changes > 100:
        base_risk = 3  # High
    elif total_changes > 50:
        base_risk = 2  # Medium
    else:
        base_risk = 1  # Low
    
    # Adjust based on file category
    category_multipliers = {
        'Critical Infrastructure': 1.5,
        'Core Logic': 1.3,
        'User Interface': 1.0,
        'Testing': 0.7,
        'Documentation/Config': 0.5,
        'Other': 0.8
    }
    
    multiplier = category_multipliers.get(file_category, 1.0)
    risk_score = base_risk * multiplier
    
    if risk_score >= 3:
        return 'High Risk'
    elif risk_score >= 2:
        return 'Medium Risk'
    else:
        return 'Low Risk'


def generate_impact_heatmap():
    """Generate impact heatmap visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, creating placeholder")
        create_placeholder_image()
        return False
    
    print("Generating impact heatmap...")
    
    # Load change data
    file_changes = load_diff_stats()
    
    if not file_changes:
        print("No file changes to analyze")
        create_no_changes_image()
        return False
    
    # Process data
    df = pd.DataFrame(file_changes)
    df['category'] = df['file'].apply(categorize_file_impact)
    df['risk_level'] = df.apply(lambda row: calculate_risk_level(row['total'], row['category']), axis=1)
    df['directory'] = df['file'].apply(lambda x: '/'.join(Path(x).parts[:-1]) if '/' in x else 'root')
    
    # Create the heatmap visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Risk Level vs Category Heatmap
    risk_category = df.groupby(['category', 'risk_level']).size().unstack(fill_value=0)
    if not risk_category.empty:
        sns.heatmap(risk_category, annot=True, fmt='d', cmap='Reds', ax=ax1, 
                   cbar_kws={'label': 'Number of Files'})
        ax1.set_title('Impact Matrix: Category vs Risk Level')
        ax1.set_xlabel('Risk Level')
        ax1.set_ylabel('File Category')
    
    # 2. Change Intensity by Directory
    dir_changes = df.groupby('directory')['total'].sum().sort_values(ascending=False).head(10)
    if len(dir_changes) > 0:
        colors = plt.cm.viridis(np.linspace(0, 1, len(dir_changes)))
        bars = ax2.barh(range(len(dir_changes)), dir_changes.values, color=colors)
        ax2.set_yticks(range(len(dir_changes)))
        ax2.set_yticklabels(dir_changes.index, fontsize=9)
        ax2.set_xlabel('Total Lines Changed')
        ax2.set_title('Change Intensity by Directory')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width + max(dir_changes.values) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=8)
    
    # 3. Risk Distribution Pie Chart
    risk_counts = df['risk_level'].value_counts()
    colors_pie = {'High Risk': '#e74c3c', 'Medium Risk': '#f39c12', 'Low Risk': '#27ae60'}
    pie_colors = [colors_pie.get(risk, '#95a5a6') for risk in risk_counts.index]
    
    _, _, autotexts = ax3.pie(risk_counts.values, labels=risk_counts.index, 
                             autopct='%1.1f%%', colors=pie_colors, startangle=90)
    ax3.set_title('Risk Level Distribution')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # 4. Top High-Risk Files
    high_risk_files = df[df['risk_level'] == 'High Risk'].nlargest(8, 'total')
    if not high_risk_files.empty:
        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(high_risk_files)))
        bars = ax4.barh(range(len(high_risk_files)), high_risk_files['total'], color=colors)
        ax4.set_yticks(range(len(high_risk_files)))
        ax4.set_yticklabels([Path(f).name for f in high_risk_files['file']], fontsize=8)
        ax4.set_xlabel('Lines Changed')
        ax4.set_title('Top High-Risk Files')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width + max(high_risk_files['total']) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=8)
    else:
        ax4.text(0.5, 0.5, 'No High-Risk Files\nDetected', ha='center', va='center', 
                transform=ax4.transAxes, fontsize=14, fontweight='bold')
        ax4.set_title('Top High-Risk Files')
        ax4.axis('off')
    
    # Add overall statistics
    total_files = len(file_changes)
    high_risk_count = len(df[df['risk_level'] == 'High Risk'])
    fig.suptitle(f'Impact Heatmap: {total_files} files changed, {high_risk_count} high-risk', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('.code-analysis/outputs/impact_heatmap.png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Impact heatmap generated for {total_files} files")
    print(f"High-risk files: {high_risk_count}")
    
    # Save detailed results
    results = {
        'total_files': total_files,
        'high_risk_files': high_risk_count,
        'risk_distribution': risk_counts.to_dict(),
        'category_breakdown': df['category'].value_counts().to_dict(),
        'top_risk_files': high_risk_files.head(5).to_dict('records') if not high_risk_files.empty else []
    }
    
    with open('.code-analysis/outputs/impact_heatmap_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return True


def create_placeholder_image():
    """Create placeholder when matplotlib is not available"""
    print("Created impact heatmap placeholder (matplotlib not available)")
    
    with open('.code-analysis/outputs/impact_heatmap_placeholder.md', 'w') as f:
        f.write("""# Impact Heatmap Placeholder

Matplotlib is not available for generating impact heatmaps.

## To Enable Visual Heatmaps:
```bash
pip install matplotlib seaborn pandas numpy
```

## Alternative Analysis:
Check `.code-analysis/outputs/diff_stats.txt` for raw change data.
""")


def create_no_changes_image():
    """Create image when no changes are detected"""
    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.text(0.5, 0.5, 'No Changes Detected', ha='center', va='center', 
                fontsize=24, fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.3, 'This PR contains no measurable file changes', 
                ha='center', va='center', fontsize=14, style='italic', transform=ax.transAxes)
        ax.set_title('Impact Heatmap', fontsize=18, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig('.code-analysis/outputs/impact_heatmap.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    print("Created no-changes impact heatmap")


def main():
    """Main impact heatmap generation logic"""
    print("Starting impact heatmap generation...")
    
    # Ensure output directory exists
    os.makedirs('.code-analysis/outputs', exist_ok=True)
    
    success = generate_impact_heatmap()
    
    print("Impact heatmap generation complete!")
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
