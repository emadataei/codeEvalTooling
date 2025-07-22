"""
Chart Generator for PR Comment Visual Enhancements
Generates simple ASCII charts and basic HTML charts for impact visualization
"""

def generate_ascii_bar_chart(data, title="Chart", max_width=30):
    """
    Generate simple ASCII bar chart
    
    Args:
        data: Dict of {label: value} pairs
        title: Chart title
        max_width: Maximum width of bars in characters
    
    Returns:
        String containing ASCII chart
    """
    if not data:
        return f"{title}\nNo data available"
    
    max_value = max(data.values()) if data.values() else 1
    chart_lines = [f"{title}", "=" * len(title), ""]
    
    for label, value in data.items():
        # Calculate bar length
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length
        
        # Format with value
        chart_lines.append(f"{label:15} |{bar:<{max_width}} {value}")
    
    return "\n".join(chart_lines)

def generate_risk_breakdown_chart(risk_categories):
    """
    Generate risk breakdown visualization
    
    Args:
        risk_categories: Dict of {category: risk_level} pairs
    
    Returns:
        String containing visual risk breakdown
    """
    if not risk_categories:
        return "Risk Breakdown\nNo categories analyzed"
    
    # Count occurrences of each risk level
    level_counts = {}
    for category, level in risk_categories.items():
        level_counts[level] = level_counts.get(level, 0) + 1
    
    return generate_ascii_bar_chart(level_counts, "Risk Level Distribution")

def generate_complexity_chart(complexity_data):
    """
    Generate complexity metrics visualization
    
    Args:
        complexity_data: Dict of complexity metrics
    
    Returns:
        String containing complexity chart
    """
    if not complexity_data:
        return "Complexity Metrics\nNo data available"
    
    # Filter and format complexity data
    chart_data = {}
    for key, value in complexity_data.items():
        if isinstance(value, (int, float)) and value > 0:
            # Shorten long keys for display
            display_key = key.replace('_', ' ').title()
            if len(display_key) > 15:
                display_key = display_key[:12] + "..."
            chart_data[display_key] = value
    
    return generate_ascii_bar_chart(chart_data, "Complexity Metrics")

def generate_file_type_chart(file_categories):
    """
    Generate file type distribution chart
    
    Args:
        file_categories: Dict of {category: [files]} pairs
    
    Returns:
        String containing file type distribution
    """
    if not file_categories:
        return "File Distribution\nNo files categorized"
    
    # Count files in each category
    category_counts = {}
    for category, files in file_categories.items():
        if files and len(files) > 0:
            category_counts[category.title()] = len(files)
    
    return generate_ascii_bar_chart(category_counts, "File Type Distribution")

def generate_dependency_stats_chart(dependency_data):
    """
    Generate dependency statistics chart
    
    Args:
        dependency_data: Dict containing dependency statistics
    
    Returns:
        String containing dependency stats visualization  
    """
    if not dependency_data:
        return "Dependency Stats\nNo data available"
    
    stats = {}
    
    # Extract relevant stats
    if 'changes' in dependency_data:
        stats['Total Changes'] = len(dependency_data['changes'])
    
    if 'high_impact_changes' in dependency_data:
        stats['High Impact'] = len(dependency_data['high_impact_changes'])
    
    if 'circular_dependencies' in dependency_data:
        stats['Circular Deps'] = len(dependency_data['circular_dependencies'])
    
    if 'total_files_analyzed' in dependency_data:
        stats['Files Analyzed'] = dependency_data['total_files_analyzed']
    
    return generate_ascii_bar_chart(stats, "Dependency Analysis")

def generate_trend_indicator(current_value, threshold_low, threshold_high):
    """
    Generate simple trend/level indicator
    
    Args:
        current_value: Current metric value
        threshold_low: Low threshold
        threshold_high: High threshold
    
    Returns:
        String with visual indicator
    """
    if current_value >= threshold_high:
        return "🔴 HIGH"
    elif current_value >= threshold_low:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"

def generate_progress_bar(value, max_value, width=20):
    """
    Generate ASCII progress bar
    
    Args:
        value: Current value
        max_value: Maximum value
        width: Width of progress bar
    
    Returns:
        String containing progress bar
    """
    if max_value == 0:
        percentage = 0
    else:
        percentage = min(100, (value / max_value) * 100)
    
    filled = int((percentage / 100) * width)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage:.1f}%"

if __name__ == "__main__":
    # Example usage
    sample_risk_data = {
        'SECURITY': 'HIGH',
        'PERFORMANCE': 'MEDIUM', 
        'TESTING': 'LOW',
        'COMPATIBILITY': 'MEDIUM'
    }
    
    sample_complexity = {
        'cyclomatic_complexity': 15,
        'nesting_depth': 4,
        'function_count': 8,
        'line_count': 250
    }
    
    sample_files = {
        'ui': ['file1.tsx', 'file2.tsx'],
        'api': ['route1.ts', 'route2.ts', 'route3.ts'],
        'test': ['test1.spec.ts']
    }
    
    print(generate_risk_breakdown_chart(sample_risk_data))
    print("\n" + "="*50 + "\n")
    print(generate_complexity_chart(sample_complexity))
    print("\n" + "="*50 + "\n") 
    print(generate_file_type_chart(sample_files))
