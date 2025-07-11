#!/usr/bin/env python3
"""
Generate HTML performance report from collected metrics
"""

import json
import os
from datetime import datetime

def load_metrics():
    """Load all metrics from JSONL file"""
    metrics = []
    if os.path.exists('performance-metrics.jsonl'):
        with open('performance-metrics.jsonl', 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        metrics.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Warning: Skipping malformed JSON on line {line_num}: {e}")
                        print(f"   Line content: {line[:100]}...")
                        continue
    return metrics

def generate_html_report(metrics):
    """Generate HTML report from metrics"""
    
    # Calculate summary statistics
    if not metrics:
        total_tools = 0
        total_duration = 0
        avg_ratio = "N/A"
        table_rows = '<tr><td colspan="5">No performance data available. Metrics will appear after running security analysis tools.</td></tr>'
    else:
        total_tools = len(set(m['tool'] for m in metrics))
        total_duration = sum(m['duration_seconds'] for m in metrics)
        avg_ratio = f"{sum(float(m.get('performance_ratio', 0)) for m in metrics) / len(metrics):.6f}"
        
        # Generate table rows
        table_rows = ""
        for metric in metrics:
            ratio = float(metric.get('performance_ratio', 0))
            status = '🚀 Fast' if ratio < 0.001 else '⚡ Normal' if ratio < 0.01 else '🐌 Slow'
            
            # Handle different LOC data structures
            if isinstance(metric.get('lines_of_code'), dict):
                loc_total = metric['lines_of_code'].get('total', 0)
            else:
                loc_total = metric.get('lines_of_code', 0)
            
            table_rows += f'''
            <tr>
                <td><strong>{metric["tool"]}</strong></td>
                <td>{metric["duration_seconds"]}</td>
                <td>{loc_total:,}</td>
                <td>{ratio:.6f}</td>
                <td>{status}</td>
            </tr>'''

    html_template = f'''<!DOCTYPE html>
<html>
<head>
    <title>Security Tools Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .summary {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; color: #856404; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #dee2e6; }}
    </style>
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
                <div><h3>{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</h3><p>Generated</p></div>
            </div>
        </div>

        {"" if metrics else '<div class="warning"><p>⚠️ No metrics collected yet. Run the workflow to see performance data.</p></div>'}

        <div>
            <h2>🎯 Performance Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tool</th>
                        <th>Duration (s)</th>
                        <th>Lines of Code</th>
                        <th>Performance Ratio (s/LOC)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
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
</html>'''

    return html_template

def main():
    """Main function"""
    print("🔄 Generating performance report...")
    
    # Debug: Show what files exist
    print("📁 Checking for metrics files...")
    current_files = [f for f in os.listdir('.') if 'metrics' in f or f.endswith('.jsonl')]
    print(f"Current directory files: {current_files}")
    
    if os.path.exists('metrics'):
        metrics_files = os.listdir('metrics')
        print(f"Metrics directory files: {metrics_files}")
    
    # Debug: Show content of metrics file if it exists
    if os.path.exists('performance-metrics.jsonl'):
        with open('performance-metrics.jsonl', 'r') as f:
            content = f.read()
            print(f"📄 Metrics file content preview (first 500 chars):")
            print(content[:500])
            if len(content) > 500:
                print("...")
    
    # Load metrics
    metrics = load_metrics()
    
    if not metrics:
        print("⚠️  No metrics found. Creating empty report.")
    else:
        print(f"✅ Found {len(metrics)} metric entries")
        for i, metric in enumerate(metrics, 1):
            print(f"  {i}. {metric.get('tool', 'Unknown')}: {metric.get('duration_seconds', 0)}s")
    
    try:
        # Generate HTML report
        html_report = generate_html_report(metrics)
        
        # Write HTML report
        with open('performance-report.html', 'w') as f:
            f.write(html_report)
        
        # Create metrics directory
        os.makedirs('metrics', exist_ok=True)
        
        # Generate summary JSON
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tools": len(set(m['tool'] for m in metrics)) if metrics else 0,
            "total_duration": sum(m['duration_seconds'] for m in metrics) if metrics else 0,
            "metrics_count": len(metrics),
            "tools": list(set(m['tool'] for m in metrics)) if metrics else [],
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
        
        print(f"✅ Performance report generated: performance-report.html")
        print(f"📊 Total metrics collected: {len(metrics)}")
        print(f"🔧 Tools analyzed: {summary['total_tools']}")
        print("\n📍 Where to access results:")
        print("  • HTML Report: performance-report.html (download from GitHub Actions artifacts)")
        print("  • Security Findings: GitHub repo → Security tab → Code scanning alerts")
        print("  • Raw Metrics: performance-metrics.jsonl")
        print("  • Workflow Logs: GitHub repo → Actions tab → specific workflow run")
        print("  • Regression Alerts: Printed in workflow logs with 🚨 prefix")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        # Create a minimal error report
        error_html = f"<html><body><h1>Error generating report</h1><p>{e}</p><pre>{traceback.format_exc()}</pre></body></html>"
        with open('performance-report.html', 'w') as f:
            f.write(error_html)
        raise

if __name__ == "__main__":
    main()
    
    metrics = load_metrics()
    
    if not metrics:
        print("⚠️  No metrics found. Creating empty report.")
    else:
        print(f"✅ Found {len(metrics)} metric entries")
        for i, metric in enumerate(metrics):
            print(f"  {i+1}. {metric.get('tool', 'Unknown')}: {metric.get('duration_seconds', 0)}s")
    
    try:
        html_report = generate_html_report(metrics)
        
        # Write HTML report
        with open('performance-report.html', 'w') as f:
            f.write(html_report)
        
        # Create metrics directory
        os.makedirs('metrics', exist_ok=True)
        
        # Generate summary JSON
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tools": len(set(m['tool'] for m in metrics)) if metrics else 0,
            "total_duration": sum(m['duration_seconds'] for m in metrics) if metrics else 0,
            "metrics_count": len(metrics),
            "tools": list(set(m['tool'] for m in metrics)) if metrics else [],
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
        
        print(f"✅ Performance report generated: performance-report.html")
        print(f"📊 Total metrics collected: {len(metrics)}")
        print(f"🔧 Tools analyzed: {summary['total_tools']}")
        print("\n📍 Where to access results:")
        print("  • HTML Report: performance-report.html (download from GitHub Actions artifacts)")
        print("  • Security Findings: GitHub repo → Security tab → Code scanning alerts")
        print("  • Raw Metrics: performance-metrics.jsonl")
        print("  • Workflow Logs: GitHub repo → Actions tab → specific workflow run")
        print("  • Regression Alerts: Printed in workflow logs with 🚨 prefix")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        # Create a minimal report anyway
        with open('performance-report.html', 'w') as f:
            f.write(f"<html><body><h1>Error generating report</h1><p>{e}</p><pre>{traceback.format_exc()}</pre></body></html>")
        raise

if __name__ == "__main__":
    main()
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


if __name__ == "__main__":
    main()
