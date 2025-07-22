"""
Visual Heatmap Generator for GitHub PR Descriptions
Creates actual image heatmaps and animated visualizations using libraries
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import json
from pathlib import Path

# Category constants
FEATURE_DEV = 'Feature Development'
BUG_FIXES = 'Bug Fixes'
CODE_QUALITY = 'Code Quality'
TESTING = 'Testing'
INFRASTRUCTURE = 'Infrastructure'
DOCUMENTATION = 'Documentation'

def create_impact_heatmap(impact_areas, output_path='impact_heatmap.png'):
    """
    Create a visual heatmap for impact areas using matplotlib/seaborn
    
    Args:
        impact_areas: Dict of {area: count} pairs
        output_path: Path to save the heatmap image
    
    Returns:
        Path to generated image file
    """
    if not impact_areas or not any(impact_areas.values()):
        return None
    
    try:
        # Prepare data for heatmap
        areas = list(impact_areas.keys())
        values = list(impact_areas.values())
        
        # Create a grid layout for the heatmap
        grid_size = int(np.ceil(np.sqrt(len(areas))))
        heatmap_data = np.zeros((grid_size, grid_size))
        labels = np.full((grid_size, grid_size), '', dtype=object)
        
        # Fill the grid
        for i, (area, value) in enumerate(zip(areas, values)):
            row = i // grid_size
            col = i % grid_size
            heatmap_data[row, col] = value
            labels[row, col] = area
        
        # Create the plot
        plt.figure(figsize=(8, 6))
        
        # Create heatmap with custom colormap
        mask = heatmap_data == 0
        sns.heatmap(heatmap_data, 
                   mask=mask,
                   annot=labels, 
                   fmt='',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Impact Level'},
                   square=True,
                   linewidths=0.5)
        
        plt.title('Code Impact Areas Heatmap', fontsize=14, fontweight='bold')
        plt.xticks([])
        plt.yticks([])
        
        # Save with high DPI for GitHub
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Impact heatmap generated: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return None

def create_story_arc_gif(commits_by_intent, output_path='story_arc.gif'):
    """
    Create an animated GIF showing the development story arc
    
    Args:
        commits_by_intent: Dict of {intent: [commits]} pairs
        output_path: Path to save the GIF
    
    Returns:
        Path to generated GIF file
    """
    if not commits_by_intent:
        return None
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Prepare data
        intents = list(commits_by_intent.keys())
        intent_counts = {intent: len(commits) for intent, commits in commits_by_intent.items()}
        
        # Create frames for animation
        frames = []
        width, height = 600, 200
        
        # Colors for different intent types
        intent_colors = {
            'setup': '#6366f1',      # Indigo
            'feature': '#10b981',    # Emerald
            'fix': '#f59e0b',        # Amber
            'refactor': '#8b5cf6',   # Violet
            'test': '#06b6d4',       # Cyan
            'docs': '#84cc16',       # Lime
            'style': '#ec4899',      # Pink
            'config': '#64748b',     # Slate
            'infra': '#dc2626',      # Red
            'workflow': '#7c3aed',   # Purple
            'other': '#6b7280'       # Gray
        }
        
        # Create each frame showing progressive development
        for frame_idx in range(len(intents) + 1):
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except (OSError, IOError):
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw title
            draw.text((10, 10), "Development Story Arc", fill='black', font=font)
            
            # Draw progress bar background
            progress_y = 50
            draw.rectangle([50, progress_y, width-50, progress_y+30], outline='#e5e7eb', width=2)
            
            # Draw completed intents
            x_pos = 50
            segment_width = (width - 100) / len(intents)
            
            for i, intent in enumerate(intents[:frame_idx]):
                # Draw segment
                color = intent_colors.get(intent, '#6b7280')
                draw.rectangle([x_pos, progress_y, x_pos + segment_width, progress_y + 30], 
                             fill=color, outline='white', width=1)
                
                # Draw label
                label = f"{intent.title()}({intent_counts[intent]})"
                label_x = x_pos + segment_width/2 - len(label)*3
                draw.text((label_x, progress_y + 35), label, fill='black', font=small_font)
                
                x_pos += segment_width
            
            # Add frame to list
            frames.append(img)
        
        # Save as GIF
        if frames:
            frames[0].save(output_path, save_all=True, append_images=frames[1:], 
                          duration=800, loop=0)
            print(f"Story arc GIF generated: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error generating story arc GIF: {e}")
        return None

def create_development_flow_chart(commits_by_intent, output_path='development_flow.png'):
    """
    Create a static development flow chart with better categorization
    
    Args:
        commits_by_intent: Dict of {intent: [commits]} pairs
        output_path: Path to save the chart
    
    Returns:
        Path to generated chart file
    """
    if not commits_by_intent:
        return None
    
    try:
        # Enhanced categorization
        enhanced_categories = categorize_intents(commits_by_intent)
        
        # Create a horizontal flow chart
        plt.figure(figsize=(12, 6))
        
        categories = list(enhanced_categories.keys())
        counts = list(enhanced_categories.values())
        colors = ['#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#dc2626', '#6b7280']
        
        # Create horizontal bar chart
        bars = plt.barh(categories, counts, color=colors[:len(categories)])
        
        # Customize the chart
        plt.title('Development Flow Breakdown', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Number of Changes', fontsize=12)
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            if count > 0:
                plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        str(count), va='center', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Development flow chart generated: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating flow chart: {e}")
        return None

def categorize_intents(commits_by_intent):
    """
    Categorize intents into more meaningful groups
    
    Args:
        commits_by_intent: Dict of {intent: [commits]} pairs
    
    Returns:
        Dict of enhanced categories with counts
    """
    categories = {
        FEATURE_DEV: 0,
        BUG_FIXES: 0,
        CODE_QUALITY: 0,
        TESTING: 0,
        INFRASTRUCTURE: 0,
        DOCUMENTATION: 0
    }
    
    intent_mapping = {
        'feature': FEATURE_DEV,
        'feat': FEATURE_DEV,
        'add': FEATURE_DEV,
        'implement': FEATURE_DEV,
        
        'fix': BUG_FIXES,
        'bug': BUG_FIXES,
        'hotfix': BUG_FIXES,
        'patch': BUG_FIXES,
        
        'refactor': CODE_QUALITY,
        'style': CODE_QUALITY,
        'cleanup': CODE_QUALITY,
        'improve': CODE_QUALITY,
        
        'test': TESTING,
        'spec': TESTING,
        'coverage': TESTING,
        
        'infra': INFRASTRUCTURE,
        'deploy': INFRASTRUCTURE,
        'config': INFRASTRUCTURE,
        'setup': INFRASTRUCTURE,
        'workflow': INFRASTRUCTURE,
        'ci': INFRASTRUCTURE,
        'cd': INFRASTRUCTURE,
        
        'docs': DOCUMENTATION,
        'doc': DOCUMENTATION,
        'readme': DOCUMENTATION,
        'comment': DOCUMENTATION
    }
    
    for intent, commits in commits_by_intent.items():
        category = intent_mapping.get(intent.lower(), CODE_QUALITY)
        categories[category] += len(commits)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v > 0}

def encode_image_for_github(image_path):
    """
    Encode image as base64 for GitHub display
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Base64 encoded string for embedding in markdown
    """
    try:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    sample_impact = {
        'UI Components': 5,
        'API Routes': 3,
        'Database': 2,
        'Tests': 4,
        'Documentation': 1
    }
    
    sample_commits = {
        'feature': ['commit1', 'commit2', 'commit3'],
        'fix': ['commit4'],
        'test': ['commit5', 'commit6'],
        'docs': ['commit7']
    }
    
    # Generate visualizations
    create_impact_heatmap(sample_impact)
    create_development_flow_chart(sample_commits)
    create_story_arc_gif(sample_commits)
