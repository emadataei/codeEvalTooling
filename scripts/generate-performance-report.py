#!/usr/bin/env python3
"""
Generate HTML performance report from collected metrics
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_metrics():
    """Load all metrics from JSONL file"""
    metrics = []
    if os.path.exists('performance-metrics.jsonl'):
        with open('performance-metrics.jsonl', 'r') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
    return metrics

def load_historical_metrics():
    """Load historical metrics for trend analysis"""
    historical = []
    if os.path.exists('metrics/historical-metrics.jsonl'):
        with open('metrics/historical-metrics.jsonl', 'r') as f:
            for line in f:
                if line.strip():
                    historical.append(json.loads(line))
    return historical

def calculate_trends(current_metrics, historical_metrics):
    """Calculate performance trends and regressions"""
    trends = {}
    
    for current in current_metrics:
        tool = current['tool']
        current_duration = current['duration_seconds']
        current_ratio = float(current.get('performance_ratio', 0))
        
        # Find recent historical data for this tool (last 5 runs)
        tool_history = [h for h in historical_metrics if h['tool'] == tool]
        tool_history = sorted(tool_history, key=lambda x: x['timestamp'], reverse=True)[:5]
        
        if tool_history:
            avg_duration = sum(h['duration_seconds'] for h in tool_history) / len(tool_history)
            avg_ratio = sum(float(h.get('performance_ratio', 0)) for h in tool_history) / len(tool_history)
            
            duration_change = ((current_duration - avg_duration) / avg_duration) * 100 if avg_duration > 0 else 0
            ratio_change = ((current_ratio - avg_ratio) / avg_ratio) * 100 if avg_ratio > 0 else 0
            
            trends[tool] = {
                'duration_change': duration_change,
                'ratio_change': ratio_change,
                'historical_runs': len(tool_history),
                'avg_duration': avg_duration,
                'avg_ratio': avg_ratio
            }
    
    return trends

def generate_html_report(metrics):
    """Generate HTML report from metrics"""
    
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Security Tools Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007cba; }}
        .summary {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; color: #856404; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; color: #155724; }}
        .error {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; color: #721c24; }}
        .trend-up {{ color: #dc3545; font-weight: bold; }}
        .trend-down {{ color: #28a745; font-weight: bold; }}
        .trend-stable {{ color: #6c757d; }}
        .nav-tabs {{ list-style: none; padding: 0; margin: 20px 0; border-bottom: 2px solid #dee2e6; }}
        .nav-tabs li {{ display: inline-block; margin-right: 10px; }}
        .nav-tabs a {{ display: block; padding: 10px 20px; text-decoration: none; color: #495057; border: 1px solid transparent; border-radius: 5px 5px 0 0; }}
        .nav-tabs a.active {{ background: #007cba; color: white; border-color: #007cba; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .regression-alert {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .improvement-alert {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #dee2e6; }}
    </style>
    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            var contents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            // Remove active class from all tabs
            var tabs = document.getElementsByClassName('nav-link');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Show selected tab content and mark tab as active
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🔒 Security Analysis Tools Performance Report</h1>
        
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div><h3>{total_tools}</h3><p>Tools Analyzed</p></div>
                <div><h3>{total_duration}s</h3><p>Total Analysis Time</p></div>
                <div><h3>{avg_ratio}</h3><p>Avg Performance Ratio</p></div>
                <div><h3>{timestamp}</h3><p>Generated</p></div>
            </div>
        </div>

        {alerts_section}

        <div id="overview" class="tab-content active">
            <h2>🎯 Performance Overview</h2>
            {table_content}
        </div>

        <div class="chart-container">
            <h3>📋 Performance Benchmarks</h3>
            <p><strong>🚀 Fast:</strong> &lt; 0.001 sec/LOC | <strong>⚡ Normal:</strong> 0.001-0.01 sec/LOC | <strong>🐌 Slow:</strong> &gt; 0.01 sec/LOC</p>
        </div>

        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <h4>📍 Access Instructions:</h4>
            <ul>
                <li><strong>GitHub Actions Artifacts:</strong> Download 'performance-metrics-report' from workflow run</li>
                <li><strong>Security Tab:</strong> SARIF results appear in repository Security tab</li>
                <li><strong>Workflow Logs:</strong> Real-time metrics in action logs</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

    # Process metrics or show empty state
    if not metrics:
        return html_template.format(
            total_tools=0,
            total_duration=0,
            avg_ratio="N/A",
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            alerts_section='<div class="warning"><p>⚠️ No metrics collected yet. Run the workflow to see performance data.</p></div>',
            table_content='<p>No performance data available. Metrics will appear after running security analysis tools.</p>'
        )

    # Calculate summary statistics
    total_tools = len(set(m['tool'] for m in metrics))
    total_duration = sum(m['duration_seconds'] for m in metrics)
    avg_ratio = sum(float(m.get('performance_ratio', 0)) for m in metrics) / len(metrics)

    # Generate table content
    table_content = '<table><thead><tr><th>Tool</th><th>Duration (s)</th><th>Lines of Code</th><th>Status</th></tr></thead><tbody>'
    
    for metric in metrics:
        ratio = float(metric.get('performance_ratio', 0))
        status = '🚀 Fast' if ratio < 0.001 else '⚡ Normal' if ratio < 0.01 else '🐌 Slow'
        loc_total = metric.get('lines_of_code', {}).get('total', 0) if isinstance(metric.get('lines_of_code'), dict) else metric.get('lines_of_code', 0)
        
        table_content += f'<tr><td>{metric["tool"]}</td><td>{metric["duration_seconds"]}</td><td>{loc_total:,}</td><td>{status}</td></tr>'
    
    table_content += '</tbody></table>'

    return html_template.format(
        total_tools=total_tools,
        total_duration=total_duration,
        avg_ratio=f"{avg_ratio:.6f}",
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        alerts_section="",
        table_content=table_content
    )

def main():
    """Main function"""
    print("🔄 Generating performance report...")
    
    # Debug: Show what files exist
    print("📁 Checking for metrics files...")
    current_files = os.listdir('.')
    print(f"Current directory files: {[f for f in current_files if 'metrics' in f or f.endswith('.jsonl')]}")
    
    if os.path.exists('metrics'):
        metrics_files = os.listdir('metrics')
        print(f"Metrics directory files: {metrics_files}")
    
    metrics = load_metrics()
    
    if not metrics:
        print("⚠️  No metrics found. Creating empty report.")
    else:
        print(f"✅ Found {len(metrics)} metric entries")
    
    try:
        html_report = generate_html_report(metrics)
        
        # Write HTML report
        with open('performance-report.html', 'w') as f:
            f.write(html_report)
        
        # Create metrics directory
        os.makedirs('metrics', exist_ok=True)
        
        print(f"✅ Performance report generated: performance-report.html")
        print(f"📊 Total metrics collected: {len(metrics)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        # Create a minimal report anyway
        with open('performance-report.html', 'w') as f:
            f.write(f"<html><body><h1>Error generating report</h1><p>{e}</p></body></html>")
        raise
    
    if improvements:
        alerts_section += '<div class="improvement-alert"><h3>🚀 Performance Improvements</h3><ul>'
        for tool in improvements:
            change = abs(trends[tool]['duration_change'])
            alerts_section += f'<li><strong>{tool}:</strong> {change:.1f}% faster than baseline</li>'
        alerts_section += '</ul></div>'

    # Generate table rows with trends
    table_rows = ""
    detailed_metrics = ""  # Initialize detailed_metrics
    
    for metric in metrics:
        ratio = float(metric.get('performance_ratio', 0))
        tool = metric['tool']
        
        # Determine status based on performance
        if ratio < 0.001:
            status = '<span class="success">🚀 Fast</span>'
        elif ratio < 0.01:
            status = '<span>⚡ Normal</span>'
        else:
            status = '<span class="warning">🐌 Slow</span>'
        
        # Add trend information
        trend_info = "📊 New"
        if tool in trends:
            change = trends[tool]['duration_change']
            if change > 10:
                trend_info = f'<span class="trend-up">📈 +{change:.1f}%</span>'
            elif change < -10:
                trend_info = f'<span class="trend-down">📉 {change:.1f}%</span>'
            else:
                trend_info = f'<span class="trend-stable">➡️ {change:.1f}%</span>'
        
        loc_total = metric.get('lines_of_code', {}).get('total', 0) if isinstance(metric.get('lines_of_code'), dict) else metric.get('lines_of_code', 0)
        files_total = metric.get('files_analyzed', {}).get('total', 0) if isinstance(metric.get('files_analyzed'), dict) else metric.get('files_analyzed', 0)
        
        table_rows += f"""
            <tr>
                <td><strong>{tool}</strong></td>
                <td>{metric['duration_seconds']}</td>
                <td>{loc_total:,}</td>
                <td>{files_total:,}</td>
                <td>{ratio:.6f}</td>
                <td>{status}</td>
                <td>{trend_info}</td>
            </tr>
        """
        
        # Generate detailed metrics for each tool
        detailed_metrics += f"""
        <div class="metric-card">
            <h3>🔧 {tool}</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div>
                    <p><strong>⏱️ Duration:</strong> {metric['duration_seconds']} seconds</p>
                    <p><strong>📝 Lines of Code:</strong> {loc_total:,}</p>
                    <p><strong>📁 Files Analyzed:</strong> {files_total:,}</p>
                </div>
                <div>
                    <p><strong>📊 Performance Ratio:</strong> {ratio:.6f} s/LOC</p>
                    <p><strong>💾 Repository Size:</strong> {metric.get('repository_size_kb', 0):,} KB</p>
                    <p><strong>🌿 Branch:</strong> {metric.get('branch', 'unknown')}</p>
                </div>
                <div>
                    <p><strong>🕒 Timestamp:</strong> {metric['timestamp']}</p>
                    <p><strong>🔗 Commit:</strong> {metric.get('commit_sha', 'unknown')[:8]}...</p>
                    <p><strong>🏃 Workflow Run:</strong> {metric.get('workflow_run_id', 'unknown')}</p>
                </div>
            </div>
        </div>
        """

    # Generate trends section
    trends_section = ""
    if trends:
        trends_section += '<div class="chart-container">'
        for tool, trend in trends.items():
            trend_class = "error" if trend['duration_change'] > 25 else "warning" if trend['duration_change'] > 10 else "success"
            trends_section += f"""
            <div class="metric-card">
                <h4>{tool}</h4>
                <div class="{trend_class}">
                    <p><strong>Duration Change:</strong> {trend['duration_change']:+.1f}% vs baseline ({trend['historical_runs']} runs)</p>
                    <p><strong>Efficiency Change:</strong> {trend['ratio_change']:+.1f}%</p>
                    <p><strong>Baseline:</strong> {trend['avg_duration']:.1f}s avg duration</p>
                </div>
            </div>
            """
        trends_section += '</div>'
    else:
        trends_section = '<p>No historical data available for trend analysis. Run more builds to see trends.</p>'

    # Generate recommendations
    recommendations_section = """
    <div class="metric-card">
        <h4>🎯 Optimization Recommendations</h4>
        <ul>
            <li><strong>CodeQL:</strong> Use targeted query packs for faster analysis</li>
            <li><strong>SonarQube:</strong> Configure exclusions for large files or third-party code</li>
            <li><strong>Semgrep:</strong> Optimize rule selection based on your tech stack</li>
            <li><strong>Snyk:</strong> Cache dependencies between runs</li>
        </ul>
    </div>
    """

    return html_template.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        total_tools=total_tools,
        total_duration=total_duration,
        avg_ratio=f"{avg_ratio:.6f}",
        table_rows=table_rows,
        detailed_metrics=detailed_metrics,
        alerts_section=alerts_section,
        trends_section=trends_section,
        recommendations_section=recommendations_section
    )

def main():
    """Main function"""
    print("🔄 Generating performance report...")
    
    metrics = load_metrics()
    
    if not metrics:
        print("⚠️  No metrics found. Creating empty report.")
        metrics = []
    
    html_report = generate_html_report(metrics)
    
    # Write HTML report
    with open('performance-report.html', 'w') as f:
        f.write(html_report)
    
    # Create metrics directory
    os.makedirs('metrics', exist_ok=True)
    
    # Generate summary JSON with access instructions
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tools": len(set(m['tool'] for m in metrics)),
        "total_duration": sum(m['duration_seconds'] for m in metrics),
        "metrics_count": len(metrics),
        "tools": list(set(m['tool'] for m in metrics)),
        "access_instructions": {
            "html_report": "performance-report.html",
            "raw_metrics": "performance-metrics.jsonl",
            "github_artifacts": "Download 'performance-metrics-report' from Actions tab",
            "security_results": "Check repository Security tab for SARIF uploads",
            "regression_alerts": "Check workflow logs for regression warnings"
        }
    }
    
    with open('metrics/performance-summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print access information
    print(f"✅ Performance report generated: performance-report.html")
    print(f"📊 Total metrics collected: {len(metrics)}")
    print(f"🔧 Tools analyzed: {summary['total_tools']}")
    print("\n📍 Where to access results:")
    print("  • HTML Report: performance-report.html (download from GitHub Actions artifacts)")
    print("  • Security Findings: GitHub repo → Security tab → Code scanning alerts")
    print("  • Raw Metrics: performance-metrics.jsonl")
    print("  • Workflow Logs: GitHub repo → Actions tab → specific workflow run")
    print("  • Regression Alerts: Printed in workflow logs with 🚨 prefix")

if __name__ == "__main__":
    main()
