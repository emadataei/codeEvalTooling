#!/usr/bin/env python3
"""
Generate PR Review Summary for Enhanced PR Visuals
Creates a simple, clear visual summary focused on what reviewers need to know
"""

import os
import sys
import json

# Try to import visualization libraries, but don't fail if they're not available
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    import io
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    print(f"Warning: Visualization libraries not available ({e}). Creating fallback.")

class PRReviewSummaryGenerator:
    def __init__(self):
        self.frame_count = 3
        self.duration = 2000  # ms per frame
        
    def load_analysis_data(self):
        """Load analysis data from the outputs directory"""
        outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
        
        # Default values
        complexity_score = 45
        tier = 1
        files_changed = 8
        high_risk_files = 0
        
        # Try to load actual data
        try:
            # Look for cognitive analysis results
            cognitive_file = os.path.join(outputs_dir, 'cognitive_analysis.json')
            if os.path.exists(cognitive_file):
                with open(cognitive_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    complexity_score = data.get('total_score', 45)
                    tier = data.get('tier', 1)
                    
            # Look for change analysis
            change_file = os.path.join(outputs_dir, 'change_analysis.json')
            if os.path.exists(change_file):
                with open(change_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    files_changed = len(data.get('files', []))
                    
            # Look for impact heatmap results
            heatmap_file = os.path.join(outputs_dir, 'impact_heatmap_results.json')
            if os.path.exists(heatmap_file):
                with open(heatmap_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    high_risk_files = data.get('high_risk_count', 0)
                    
        except Exception as e:
            print(f"Using default values due to data load error: {e}")
            
        return {
            'complexity_score': complexity_score,
            'tier': tier,
            'files_changed': files_changed,
            'high_risk_files': high_risk_files
        }
        
    def get_tier_info(self, tier):
        """Get tier description and color"""
        if tier == 0:
            return "Auto-Merge", "#4CAF50", "Ready for automatic merge"
        elif tier == 1:
            return "Standard Review", "#FF9800", "Needs peer review"
        else:
            return "Expert Review", "#F44336", "Requires expert attention"
            
    def generate_frames(self):
        """Generate simple, clear frames for PR review summary"""
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries not available, creating placeholder")
            self.create_fallback_summary()
            return []
        
        frames = []
        data = self.load_analysis_data()
        
        complexity_score = data['complexity_score']
        tier = data['tier']
        files_changed = data['files_changed']
        high_risk_files = data['high_risk_files']
        
        tier_name, tier_color, tier_desc = self.get_tier_info(tier)
        
        # Frame 1: PR Overview
        fig = plt.figure(figsize=(12, 8), facecolor='white')
        fig.suptitle('PR Review Summary', fontsize=24, fontweight='bold', y=0.95)
        
        # Create summary grid
        ax = plt.subplot(1, 1, 1)
        
        # Main metrics in a clean layout
        metrics_text = f"""
Files Changed: {files_changed}
Complexity Score: {complexity_score}/100
High-Risk Files: {high_risk_files}

Review Assignment: {tier_name}
{tier_desc}
"""
        
        ax.text(0.5, 0.6, metrics_text, ha='center', va='center', 
                fontsize=18, transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=1", facecolor=tier_color, alpha=0.1, edgecolor=tier_color))
        
        # Tier indicator
        ax.text(0.5, 0.2, tier_name, ha='center', va='center', 
                fontsize=22, fontweight='bold', color=tier_color, transform=ax.transAxes)
        
        ax.axis('off')
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).convert('RGB'))
        plt.close()
        
        # Frame 2: Complexity Breakdown
        fig = plt.figure(figsize=(12, 8), facecolor='white')
        fig.suptitle('Complexity Analysis', fontsize=24, fontweight='bold', y=0.95)
        
        ax = plt.subplot(1, 1, 1)
        
        # Simple bar chart of complexity
        categories = ['Low\n(0-35)', 'Medium\n(36-65)', 'High\n(66+)']
        values = [35, 30, 35]  # Max values for each tier
        colors = ['#4CAF50', '#FF9800', '#F44336']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.3)
        
        # Show current score
        if complexity_score <= 35:
            current_bar = 0
        elif complexity_score <= 65:
            current_bar = 1
        else:
            current_bar = 2
            
        bars[current_bar].set_alpha(0.8)
        bars[current_bar].set_edgecolor('black')
        bars[current_bar].set_linewidth(3)
        
        # Add score text
        ax.text(current_bar, complexity_score, f'{complexity_score}', 
                ha='center', va='bottom', fontsize=16, fontweight='bold')
        
        ax.set_ylabel('Complexity Score', fontsize=14)
        ax.set_title(f'Your PR: {complexity_score} points ({tier_name})', 
                     fontsize=16, color=tier_color)
        ax.set_ylim(0, 100)
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).convert('RGB'))
        plt.close()
        
        # Frame 3: Review Action
        fig = plt.figure(figsize=(12, 8), facecolor='white')
        fig.suptitle('Review Action Required', fontsize=24, fontweight='bold', y=0.95)
        
        ax = plt.subplot(1, 1, 1)
        
        # Action-oriented message
        if tier == 0:
            action_text = """✓ AUTO-MERGE READY
            
No manual review needed
CI checks will handle this PR
Merge when tests pass"""
            
        elif tier == 1:
            action_text = """📋 STANDARD REVIEW NEEDED
            
Assign 1-2 reviewers
Normal complexity changes
Expected review time: 15-30 min"""
            
        else:
            action_text = """⚠️ EXPERT REVIEW REQUIRED
            
High complexity detected
Domain expert needed
Thorough review recommended"""
        
        ax.text(0.5, 0.5, action_text, ha='center', va='center', 
                fontsize=18, transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=1", facecolor=tier_color, alpha=0.1, edgecolor=tier_color))
        
        ax.axis('off')
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='white')
        buf.seek(0)
        frames.append(Image.open(buf).convert('RGB'))
        plt.close()
        
        return frames
    
    def create_fallback_summary(self):
        """Create a text-based summary when visualization libraries aren't available"""
        outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
        
        # Load basic data
        data = self.load_analysis_data()
        tier_name, _, tier_desc = self.get_tier_info(data['tier'])
        
        # Create a simple text summary file instead of GIF
        summary_content = f"""# PR Review Summary

## Quick Overview
- **Files Changed:** {data['files_changed']}
- **Complexity Score:** {data['complexity_score']}/100
- **High-Risk Files:** {data['high_risk_files']}
- **Review Assignment:** {tier_name}
- **Description:** {tier_desc}

## Review Action Required

Based on the analysis, this PR requires **{tier_name}**.

{tier_desc}

---

*Note: Visual animation not available due to missing dependencies. Install matplotlib, numpy, and Pillow for full visual experience.*
"""
        
        # Save as markdown file
        summary_path = os.path.join(outputs_dir, 'story_arc_summary.md')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"Created fallback summary: {summary_path}")
        return True
    
    def create_gif(self, frames, output_path):
        """Create animated GIF from frames"""
        if not frames:
            print("No frames to create GIF")
            return False
            
        try:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=self.duration,
                loop=0,
                optimize=True
            )
            return True
        except Exception as e:
            print(f"Error creating GIF: {e}")
            return False


def main():
    """Main function to generate the PR review summary"""
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    generator = PRReviewSummaryGenerator()
    
    if not VISUALIZATION_AVAILABLE:
        print("Generating PR review summary (text fallback)...")
        success = generator.create_fallback_summary()
        if success:
            print("PR review summary generated successfully (text format)")
        return success
    
    print("Generating PR review summary frames...")
    frames = generator.generate_frames()
    
    if frames:
        output_path = os.path.join(outputs_dir, 'story_arc.gif')
        print(f"Creating PR review summary: {output_path}")
        
        if generator.create_gif(frames, output_path):
            print(f"Successfully created PR review summary: {output_path}")
            print(f"Generated {len(frames)} clear, actionable frames")
            return True
        else:
            print("Failed to create GIF")
            return False
    else:
        print("No frames generated")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
