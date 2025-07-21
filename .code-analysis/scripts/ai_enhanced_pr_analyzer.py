#!/usr/bin/env python3
"""
AI-Enhanced PR Analysis Integration
Combines intent classification and impact prediction with existing analysis tools.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# Add .code-analysis to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.intent_classifier import IntentClassifier, get_file_changes_from_git
    from scripts.impact_predictor import ImpactPredictor
    ANALYSIS_TOOLS_AVAILABLE = True
except ImportError:
    ANALYSIS_TOOLS_AVAILABLE = False

class AIEnhancedPRAnalyzer:
    """Integrates AI-powered analysis tools for comprehensive PR review"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.intent_classifier = IntentClassifier() if ANALYSIS_TOOLS_AVAILABLE else None
        self.impact_predictor = ImpactPredictor(repo_path) if ANALYSIS_TOOLS_AVAILABLE else None
        
    def analyze_pr(self, pr_title: str = "", pr_description: str = "",
                  base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> Dict[str, Any]:
        """Perform comprehensive PR analysis combining all AI tools"""
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'pr_metadata': {
                'title': pr_title,
                'description': pr_description,
                'base_ref': base_ref,
                'head_ref': head_ref
            },
            'file_changes': [],
            'intent_classification': None,
            'impact_prediction': None,
            'recommendations': [],
            'summary': "",
            'error_messages': []
        }
        
        try:
            # Get file changes from git
            file_changes = get_file_changes_from_git(str(self.repo_path), base_ref, head_ref)
            
            if not file_changes:
                analysis_results['error_messages'].append("No file changes detected")
                return analysis_results
            
            # Convert file changes to dict format
            file_changes_dict = []
            for change in file_changes:
                file_changes_dict.append({
                    'file_path': change.file_path,
                    'change_type': change.change_type,
                    'lines_added': change.lines_added,
                    'lines_removed': change.lines_removed,
                    'file_type': change.file_type,
                    'is_test_file': change.is_test_file
                })
            
            analysis_results['file_changes'] = file_changes_dict
            
            # Perform intent classification
            if self.intent_classifier:
                try:
                    intent_result = self.intent_classifier.analyze_pr_intent(
                        pr_title, pr_description, file_changes
                    )
                    
                    analysis_results['intent_classification'] = {
                        'primary_intent': intent_result.primary_intent.value,
                        'confidence': intent_result.confidence,
                        'secondary_intents': [
                            (intent.value, conf) 
                            for intent, conf in intent_result.secondary_intents
                        ],
                        'reasoning': intent_result.reasoning,
                        'affected_areas': intent_result.affected_areas,
                        'business_impact': intent_result.business_impact,
                        'technical_details': intent_result.technical_details
                    }
                    
                except Exception as e:
                    analysis_results['error_messages'].append(f"Intent classification failed: {e}")
            
            # Perform impact prediction
            if self.impact_predictor:
                try:
                    pr_context = {
                        'title': pr_title,
                        'description': pr_description
                    }
                    
                    impact_result = self.impact_predictor.analyze_change_impact(
                        file_changes_dict, pr_context
                    )
                    
                    analysis_results['impact_prediction'] = {
                        'overall_risk_score': impact_result.overall_risk_score,
                        'deployment_readiness': impact_result.deployment_readiness,
                        'summary': impact_result.summary,
                        'impacts': [
                            {
                                'category': impact.category.value,
                                'severity': impact.severity.value,
                                'description': impact.description,
                                'confidence': impact.confidence,
                                'affected_components': impact.affected_components,
                                'recommended_actions': impact.recommended_actions,
                                'risk_factors': impact.risk_factors,
                                'mitigation_strategies': impact.mitigation_strategies
                            }
                            for impact in impact_result.impacts
                        ],
                        'test_recommendations': [
                            {
                                'test_type': rec.test_type,
                                'priority': rec.priority,
                                'description': rec.description,
                                'specific_tests': rec.specific_tests,
                                'reasoning': rec.reasoning
                            }
                            for rec in impact_result.test_recommendations
                        ],
                        'monitoring_suggestions': impact_result.monitoring_suggestions,
                        'rollback_considerations': impact_result.rollback_considerations
                    }
                    
                except Exception as e:
                    analysis_results['error_messages'].append(f"Impact prediction failed: {e}")
            
            # Generate integrated recommendations
            analysis_results['recommendations'] = self._generate_integrated_recommendations(analysis_results)
            
            # Generate summary
            analysis_results['summary'] = self._generate_comprehensive_summary(analysis_results)
            
        except Exception as e:
            analysis_results['error_messages'].append(f"Analysis failed: {e}")
        
        return analysis_results
    
    def _generate_integrated_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integrated recommendations based on all analysis results"""
        
        recommendations = []
        
        # Add intent-based recommendations
        recommendations.extend(self._get_intent_recommendations(analysis_results))
        
        # Add impact-based recommendations
        recommendations.extend(self._get_impact_recommendations(analysis_results))
        
        # Add file pattern-based recommendations
        recommendations.extend(self._get_file_pattern_recommendations(analysis_results))
        
        return recommendations
    
    def _get_intent_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on intent classification"""
        recommendations = []
        intent_data = analysis_results.get('intent_classification')
        
        if not intent_data:
            return recommendations
            
        intent = intent_data.get('primary_intent')
        confidence = intent_data.get('confidence', 0)
        
        if intent == 'security' or confidence > 0.8:
            recommendations.append({
                'type': 'review_priority',
                'priority': 'high',
                'title': 'Security Review Required',
                'description': 'This PR involves security-related changes that require careful review.',
                'source': 'intent_classification'
            })
        
        if intent == 'refactor' and confidence > 0.7:
            recommendations.append({
                'type': 'testing',
                'priority': 'medium',
                'title': 'Comprehensive Testing Needed',
                'description': 'Refactoring changes require thorough regression testing.',
                'source': 'intent_classification'
            })
        
        return recommendations
    
    def _get_impact_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on impact prediction"""
        recommendations = []
        impact_data = analysis_results.get('impact_prediction')
        
        if not impact_data:
            return recommendations
            
        risk_score = impact_data.get('overall_risk_score', 0)
        
        if risk_score > 0.7:
            recommendations.append({
                'type': 'deployment',
                'priority': 'high',
                'title': 'High-Risk Deployment',
                'description': f'Risk score of {risk_score:.1%} suggests staged deployment approach.',
                'source': 'impact_prediction'
            })
        
        # Add test recommendations
        for test_rec in impact_data.get('test_recommendations', []):
            if test_rec['priority'] == 'high':
                recommendations.append({
                    'type': 'testing',
                    'priority': test_rec['priority'],
                    'title': f'{test_rec["test_type"].title()} Testing Required',
                    'description': test_rec['description'],
                    'source': 'impact_prediction'
                })
        
        return recommendations
    
    def _get_file_pattern_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on file patterns"""
        recommendations = []
        file_changes = analysis_results.get('file_changes', [])
        
        if not file_changes:
            return recommendations
        
        # Check for database changes
        db_files = [f for f in file_changes if self._is_database_file(f['file_path'])]
        if db_files:
            recommendations.append({
                'type': 'database',
                'priority': 'high',
                'title': 'Database Migration Review',
                'description': f'Found {len(db_files)} database-related files. Ensure migration safety.',
                'source': 'file_analysis'
            })
        
        # Check for large changes
        large_files = [f for f in file_changes if f['lines_added'] + f['lines_removed'] > 100]
        if large_files:
            recommendations.append({
                'type': 'review_scope',
                'priority': 'medium',
                'title': 'Large Change Set',
                'description': f'Found {len(large_files)} files with significant changes. Consider breaking into smaller PRs.',
                'source': 'file_analysis'
            })
        
        return recommendations
    
    def _is_database_file(self, file_path: str) -> bool:
        """Check if a file is database-related"""
        db_patterns = ['/migration', '.sql', '/schema', '/model']
        return any(pattern in file_path.lower() for pattern in db_patterns)
    
    def _generate_comprehensive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of the PR analysis"""
        
        summary_parts = []
        
        # Add intent summary
        summary_parts.extend(self._get_intent_summary_parts(analysis_results))
        
        # Add impact summary
        summary_parts.extend(self._get_impact_summary_parts(analysis_results))
        
        # Add file changes summary
        summary_parts.extend(self._get_file_changes_summary_parts(analysis_results))
        
        # Add recommendations summary
        summary_parts.extend(self._get_recommendations_summary_parts(analysis_results))
        
        # Add error summary
        summary_parts.extend(self._get_error_summary_parts(analysis_results))
        
        if not summary_parts:
            return "✅ Analysis completed with no significant findings."
        
        return "\n\n".join(summary_parts)
    
    def _get_intent_summary_parts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get intent classification summary parts"""
        parts = []
        intent_data = analysis_results.get('intent_classification')
        
        if intent_data:
            intent = intent_data.get('primary_intent', 'unknown')
            confidence = intent_data.get('confidence', 0)
            affected_areas = intent_data.get('affected_areas', [])
            
            parts.append(f"🎯 **Intent**: {intent.title()} ({confidence:.0%} confidence)")
            
            if affected_areas:
                parts.append(f"📍 **Affected Areas**: {', '.join(affected_areas)}")
        
        return parts
    
    def _get_impact_summary_parts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get impact prediction summary parts"""
        parts = []
        impact_data = analysis_results.get('impact_prediction')
        
        if impact_data:
            risk_score = impact_data.get('overall_risk_score', 0)
            deployment_readiness = impact_data.get('deployment_readiness', 'Unknown')
            
            risk_emoji = self._get_risk_emoji(risk_score)
            parts.append(f"{risk_emoji} **Risk Level**: {risk_score:.0%} - {deployment_readiness}")
            
            impacts = impact_data.get('impacts', [])
            if impacts:
                high_impacts = [i for i in impacts if i['severity'] in ['high', 'critical']]
                if high_impacts:
                    impact_categories = {i['category'] for i in high_impacts}
                    parts.append(f"⚠️ **Key Concerns**: {', '.join(impact_categories)}")
        
        return parts
    
    def _get_file_changes_summary_parts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get file changes summary parts"""
        parts = []
        file_changes = analysis_results.get('file_changes', [])
        
        if file_changes:
            total_files = len(file_changes)
            total_lines_added = sum(f['lines_added'] for f in file_changes)
            total_lines_removed = sum(f['lines_removed'] for f in file_changes)
            
            parts.append(f"📊 **Changes**: {total_files} files, +{total_lines_added}/-{total_lines_removed} lines")
        
        return parts
    
    def _get_recommendations_summary_parts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get recommendations summary parts"""
        parts = []
        recommendations = analysis_results.get('recommendations', [])
        
        if recommendations:
            high_priority = [r for r in recommendations if r['priority'] == 'high']
            if high_priority:
                parts.append(f"🔥 **Action Required**: {len(high_priority)} high-priority recommendations")
        
        return parts
    
    def _get_error_summary_parts(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get error summary parts"""
        parts = []
        errors = analysis_results.get('error_messages', [])
        
        if errors:
            parts.append(f"⚠️ **Issues**: {len(errors)} analysis errors occurred")
        
        return parts
    
    def _get_risk_emoji(self, risk_score: float) -> str:
        """Get emoji for risk score"""
        if risk_score < 0.3:
            return "🟢"
        elif risk_score < 0.7:
            return "🟡"
        else:
            return "🔴"
    
    def generate_markdown_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a formatted markdown report"""
        
        report_lines = [
            "# 🤖 AI-Enhanced PR Analysis Report",
            f"*Generated: {analysis_results.get('timestamp', 'Unknown')}*",
            "",
            "## 📋 Summary",
            analysis_results.get('summary', 'No summary available'),
            ""
        ]
        
        # Intent Classification Section
        intent_data = analysis_results.get('intent_classification')
        if intent_data:
            report_lines.extend([
                "## 🎯 Intent Classification",
                f"**Primary Intent**: {intent_data.get('primary_intent', 'Unknown').title()}",
                f"**Confidence**: {intent_data.get('confidence', 0):.0%}",
                ""
            ])
            
            if intent_data.get('reasoning'):
                report_lines.extend([
                    "**Reasoning**:",
                    intent_data['reasoning'],
                    ""
                ])
            
            if intent_data.get('business_impact'):
                report_lines.extend([
                    "**Business Impact**:",
                    intent_data['business_impact'],
                    ""
                ])
        
        # Impact Prediction Section
        impact_data = analysis_results.get('impact_prediction')
        if impact_data:
            report_lines.extend([
                "## 📊 Impact Analysis",
                f"**Overall Risk Score**: {impact_data.get('overall_risk_score', 0):.0%}",
                f"**Deployment Readiness**: {impact_data.get('deployment_readiness', 'Unknown')}",
                ""
            ])
            
            impacts = impact_data.get('impacts', [])
            if impacts:
                report_lines.extend(["### Predicted Impacts", ""])
                
                for impact in impacts:
                    severity_emoji = {
                        'low': '🟢',
                        'medium': '🟡', 
                        'high': '🟠',
                        'critical': '🔴'
                    }.get(impact['severity'], '⚪')
                    
                    report_lines.extend([
                        f"{severity_emoji} **{impact['category'].title()}** ({impact['severity'].title()})",
                        f"- {impact['description']}",
                        f"- Confidence: {impact['confidence']:.0%}",
                        ""
                    ])
            
            test_recs = impact_data.get('test_recommendations', [])
            if test_recs:
                report_lines.extend(["### Testing Recommendations", ""])
                for rec in test_recs:
                    priority_emoji = {'high': '🔥', 'medium': '⚡', 'low': '💡'}.get(rec['priority'], '📝')
                    report_lines.extend([
                        f"{priority_emoji} **{rec['test_type'].title()} Testing** ({rec['priority']} priority)",
                        f"- {rec['description']}",
                        f"- Reasoning: {rec['reasoning']}",
                        ""
                    ])
        
        # Recommendations Section
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            report_lines.extend(["## 💡 Recommendations", ""])
            
            for rec in recommendations:
                priority_emoji = {'high': '🔥', 'medium': '⚡', 'low': '💡'}.get(rec['priority'], '📝')
                report_lines.extend([
                    f"{priority_emoji} **{rec['title']}** ({rec['priority']} priority)",
                    f"- {rec['description']}",
                    f"- Source: {rec['source']}",
                    ""
                ])
        
        # File Changes Section
        file_changes = analysis_results.get('file_changes', [])
        if file_changes:
            report_lines.extend(["## 📁 File Changes", ""])
            
            # Group by change type
            by_type = {}
            for change in file_changes:
                change_type = change['change_type']
                if change_type not in by_type:
                    by_type[change_type] = []
                by_type[change_type].append(change)
            
            for change_type, changes in by_type.items():
                report_lines.extend([f"### {change_type.title()} Files ({len(changes)})", ""])
                
                for change in changes[:10]:  # Limit display
                    lines_change = f"+{change['lines_added']}/-{change['lines_removed']}"
                    report_lines.append(f"- `{change['file_path']}` ({lines_change})")
                
                if len(changes) > 10:
                    report_lines.append(f"- ... and {len(changes) - 10} more files")
                
                report_lines.append("")
        
        # Errors Section
        errors = analysis_results.get('error_messages', [])
        if errors:
            report_lines.extend(["## ⚠️ Analysis Issues", ""])
            for error in errors:
                report_lines.append(f"- {error}")
            report_lines.append("")
        
        return "\n".join(report_lines)

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Enhanced PR Analysis')
    parser.add_argument('--repo', required=True, help='Repository path')
    parser.add_argument('--title', default='', help='PR title')
    parser.add_argument('--description', default='', help='PR description')
    parser.add_argument('--base', default='HEAD~1', help='Base commit/branch')
    parser.add_argument('--head', default='HEAD', help='Head commit/branch')
    parser.add_argument('--output-json', help='Output JSON file')
    parser.add_argument('--output-md', help='Output Markdown report file')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], default='both',
                       help='Output format')
    
    args = parser.parse_args()
    
    if not ANALYSIS_TOOLS_AVAILABLE:
        print("Error: Analysis tools not available. Check dependencies.")
        return 1
    
    # Perform analysis
    analyzer = AIEnhancedPRAnalyzer(args.repo)
    results = analyzer.analyze_pr(args.title, args.description, args.base, args.head)
    
    # Output results
    if args.format in ['json', 'both']:
        json_output = args.output_json or 'pr_analysis.json'
        with open(json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"JSON analysis written to {json_output}")
    
    if args.format in ['markdown', 'both']:
        md_output = args.output_md or 'pr_analysis.md'
        markdown_report = analyzer.generate_markdown_report(results)
        with open(md_output, 'w') as f:
            f.write(markdown_report)
        print(f"Markdown report written to {md_output}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("PR ANALYSIS SUMMARY")
    print("="*60)
    print(results.get('summary', 'No summary available'))
    
    if results.get('error_messages'):
        print(f"\nErrors encountered: {len(results['error_messages'])}")
        for error in results['error_messages']:
            print(f"  - {error}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
