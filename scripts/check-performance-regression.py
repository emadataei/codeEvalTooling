#!/usr/bin/env python3
"""
Check for performance regressions in security analysis tools
"""

import json
import argparse
import sys
import os
from datetime import datetime, timedelta

def load_current_metrics(filepath):
    """Load current run metrics"""
    metrics = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
    return metrics

def load_historical_metrics():
    """Load historical metrics from previous runs"""
    # In a real implementation, this would fetch from a database or artifact storage
    # For now, we'll simulate with a simple file-based approach
    historical_file = 'metrics/historical-metrics.jsonl'
    
    if not os.path.exists(historical_file):
        return []
    
    metrics = []
    with open(historical_file, 'r') as f:
        for line in f:
            if line.strip():
                metrics.append(json.loads(line))
    
    return metrics

def calculate_baseline(historical_metrics, tool_name, days=7):
    """Calculate baseline performance for a tool"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    relevant_metrics = [
        m for m in historical_metrics 
        if m['tool'] == tool_name and 
        datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > cutoff_date
    ]
    
    if not relevant_metrics:
        return None
    
    avg_duration = sum(m['duration_seconds'] for m in relevant_metrics) / len(relevant_metrics)
    avg_ratio = sum(float(m.get('performance_ratio', 0)) for m in relevant_metrics) / len(relevant_metrics)
    
    return {
        'avg_duration': avg_duration,
        'avg_ratio': avg_ratio,
        'sample_count': len(relevant_metrics)
    }

def check_regression(current_metrics, historical_metrics, threshold_percent):
    """Check for performance regressions"""
    regressions = []
    improvements = []
    
    for metric in current_metrics:
        tool_name = metric['tool']
        current_duration = metric['duration_seconds']
        current_ratio = float(metric.get('performance_ratio', 0))
        
        baseline = calculate_baseline(historical_metrics, tool_name)
        
        if baseline is None:
            print(f"ℹ️  No baseline data for {tool_name} - establishing baseline")
            continue
        
        # Check duration regression
        duration_change = ((current_duration - baseline['avg_duration']) / baseline['avg_duration']) * 100
        ratio_change = ((current_ratio - baseline['avg_ratio']) / baseline['avg_ratio']) * 100
        
        if duration_change > threshold_percent:
            regressions.append({
                'tool': tool_name,
                'type': 'duration',
                'current': current_duration,
                'baseline': baseline['avg_duration'],
                'change_percent': duration_change,
                'baseline_samples': baseline['sample_count']
            })
        elif duration_change < -threshold_percent:
            improvements.append({
                'tool': tool_name,
                'type': 'duration',
                'current': current_duration,
                'baseline': baseline['avg_duration'],
                'change_percent': duration_change,
                'baseline_samples': baseline['sample_count']
            })
        
        # Check ratio regression
        if ratio_change > threshold_percent:
            regressions.append({
                'tool': tool_name,
                'type': 'efficiency',
                'current': current_ratio,
                'baseline': baseline['avg_ratio'],
                'change_percent': ratio_change,
                'baseline_samples': baseline['sample_count']
            })
    
    return regressions, improvements

def main():
    parser = argparse.ArgumentParser(description='Check for performance regressions')
    parser.add_argument('--current-metrics', required=True, help='Path to current metrics file')
    parser.add_argument('--threshold', type=float, default=20.0, help='Regression threshold percentage')
    parser.add_argument('--fail-on-regression', action='store_true', help='Exit with error code on regression')
    
    args = parser.parse_args()
    
    print(f"🔍 Checking for performance regressions (threshold: {args.threshold}%)")
    
    current_metrics = load_current_metrics(args.current_metrics)
    historical_metrics = load_historical_metrics()
    
    if not current_metrics:
        print("⚠️  No current metrics found")
        return 0
    
    regressions, improvements = check_regression(current_metrics, historical_metrics, args.threshold)
    
    # Report results
    if regressions:
        print(f"🚨 Performance regressions detected ({len(regressions)}):")
        for reg in regressions:
            print(f"  - {reg['tool']} ({reg['type']}): {reg['change_percent']:.1f}% slower")
            print(f"    Current: {reg['current']:.3f}, Baseline: {reg['baseline']:.3f}")
    else:
        print("✅ No performance regressions detected")
    
    if improvements:
        print(f"🚀 Performance improvements detected ({len(improvements)}):")
        for imp in improvements:
            print(f"  - {imp['tool']} ({imp['type']}): {abs(imp['change_percent']):.1f}% faster")
    
    # Store current metrics as historical for future runs
    os.makedirs('metrics', exist_ok=True)
    with open('metrics/historical-metrics.jsonl', 'a') as f:
        for metric in current_metrics:
            f.write(json.dumps(metric) + '\n')
    
    if regressions and args.fail_on_regression:
        print("❌ Failing due to performance regressions")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
