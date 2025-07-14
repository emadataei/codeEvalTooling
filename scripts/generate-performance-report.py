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
        with open('performance-metrics.jsonl', 'r', encoding='utf-8') as f:
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
    """Generate HTML report from metrics including security findings"""
    
    # Calculate summary statistics
    if not metrics:
        total_tools = 0
        total_duration = 0
        avg_ratio = "N/A"
        total_vulnerabilities = 0
        security_table_rows = '<tr><td colspan="6">No security data available. Results will appear after running security analysis tools.</td></tr>'
        performance_table_rows = '<tr><td colspan="5">No performance data available. Metrics will appear after running security analysis tools.</td></tr>'
    else:
        total_tools = len(set(m['tool'] for m in metrics))
        total_duration = sum(m['duration_seconds'] for m in metrics)
        avg_ratio = f"{sum(float(m.get('performance_ratio', 0)) for m in metrics) / len(metrics):.6f}"
        
        # Calculate total vulnerabilities
        total_vulnerabilities = 0
        for metric in metrics:
            findings = metric.get('security_findings', {})
            if isinstance(findings.get('total_vulnerabilities'), int):
                total_vulnerabilities += findings['total_vulnerabilities']
        
        # Generate security findings table
        security_table_rows = ""
        for metric in metrics:
            findings = metric.get('security_findings', {})
            total_vulns = findings.get('total_vulnerabilities', 'N/A')
            high_vulns = findings.get('high_severity', 'N/A')
            med_vulns = findings.get('medium_severity', 'N/A')
            low_vulns = findings.get('low_severity', 'N/A')
            top_issues = findings.get('top_issues', '').replace(';', '<br>') if findings.get('top_issues') else 'None detected'
            
            # Handle special values
            if total_vulns == 'github_stored':
                total_vulns = '<a href="../../security/code-scanning" target="_blank">View in Security Tab</a>'
                high_vulns = med_vulns = low_vulns = '-'
                top_issues = 'Results stored in GitHub Security tab'
            elif total_vulns == 'sonarcloud_stored':
                total_vulns = '<a href="https://sonarcloud.io" target="_blank">View in SonarCloud</a>'
                high_vulns = med_vulns = low_vulns = '-'
                top_issues = 'Results stored in SonarCloud'
            
            security_table_rows += f'''
            <tr>
                <td><strong>{metric["tool"]}</strong></td>
                <td>{total_vulns}</td>
                <td>{high_vulns}</td>
                <td>{med_vulns}</td>
                <td>{low_vulns}</td>
                <td style="max-width: 300px; word-wrap: break-word;">{top_issues[:200]}...</td>
            </tr>'''
        
        # Generate performance table rows
        performance_table_rows = ""
        for metric in metrics:
            ratio = float(metric.get('performance_ratio', 0))
            status = '🚀 Fast' if ratio < 0.001 else '⚡ Normal' if ratio < 0.01 else '🐌 Slow'
            
            # Handle different LOC data structures
            if isinstance(metric.get('lines_of_code'), dict):
                loc_total = metric['lines_of_code'].get('total', 0)
            else:
                loc_total = metric.get('lines_of_code', 0)
            
            performance_table_rows += f'''
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
    <title>Security Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .summary {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; color: #856404; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #dee2e6; }}
        .security-section {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545; }}
        .high-severity {{ color: #dc3545; font-weight: bold; }}
        .medium-severity {{ color: #fd7e14; font-weight: bold; }}
        .low-severity {{ color: #6f42c1; }}
        .tab {{ display: none; }}
        .tab.active {{ display: block; }}
        .tab-buttons {{ margin: 20px 0; }}
        .tab-button {{ background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-right: 5px; border-radius: 5px; }}
        .tab-button.active {{ background: #0056b3; }}
    </style>
    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="showTab('${{tabName}}')"]`).classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🔒 Security Analysis Report</h1>
        
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div><h3>{total_tools}</h3><p>Tools Analyzed</p></div>
                <div><h3>{total_duration}s</h3><p>Total Analysis Time</p></div>
                <div><h3 class="high-severity">{total_vulnerabilities if isinstance(total_vulnerabilities, int) else 'N/A'}</h3><p>Total Vulnerabilities</p></div>
                <div><h3>{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</h3><p>Generated</p></div>
            </div>
        </div>

        {"" if metrics else '<div class="warning"><p>⚠️ No metrics collected yet. Run the workflow to see security analysis data.</p></div>'}

        <div class="tab-buttons">
            <button class="tab-button active" onclick="showTab('security')">🔒 Security Findings</button>
            <button class="tab-button" onclick="showTab('performance')">⚡ Performance</button>
        </div>

        <div id="security" class="tab active">
            <div class="security-section">
                <h2>🔒 Security Findings</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Tool</th>
                            <th>Total Issues</th>
                            <th class="high-severity">High Severity</th>
                            <th class="medium-severity">Medium Severity</th>
                            <th class="low-severity">Low Severity</th>
                            <th>Top Issues</th>
                        </tr>
                    </thead>
                    <tbody>
                        {security_table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="performance" class="tab">
            <h2>⚡ Performance Overview</h2>
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
                    {performance_table_rows}
                </tbody>
            </table>
            
            <div class="chart-container">
                <h3>📋 Performance Benchmarks</h3>
                <p><strong>🚀 Fast:</strong> &lt; 0.001 sec/LOC | <strong>⚡ Normal:</strong> 0.001-0.01 sec/LOC | <strong>🐌 Slow:</strong> &gt; 0.01 sec/LOC</p>
            </div>
        </div>

        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <h4>📍 Access Instructions:</h4>
            <ul>
                <li><strong>GitHub Security Tab:</strong> SARIF results appear in repository Security → Code scanning</li>
                <li><strong>SonarCloud:</strong> Detailed code quality metrics at sonarcloud.io</li>
                <li><strong>Artifacts:</strong> Download full reports from GitHub Actions artifacts</li>
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
        with open('performance-metrics.jsonl', 'r', encoding='utf-8') as f:
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
        with open('performance-report.html', 'w', encoding='utf-8') as f:
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
        
        with open('metrics/performance-summary.json', 'w', encoding='utf-8') as f:
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
        with open('performance-report.html', 'w', encoding='utf-8') as f:
            f.write(error_html)
        raise

if __name__ == "__main__":
    main()