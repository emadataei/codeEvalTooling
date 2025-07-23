#!/usr/bin/env python3
"""
Demo script for AI-Enhanced PR Analysis Tools
Shows how to use intent classification and impact prediction.
"""

import os
import sys
import json
from pathlib import Path

# Add .code-analysis to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.ai_enhanced_pr_analyzer import AIEnhancedPRAnalyzer
    from scripts.dependency_graph_generator import DependencyGraphGenerator
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Tools not available: {e}")
    TOOLS_AVAILABLE = False

def demo_intent_classification():
    """Demo intent classification functionality"""
    print("\n" + "="*60)
    print("🎯 INTENT CLASSIFICATION DEMO")
    print("="*60)
    
    # Example PR scenarios
    scenarios = [
        {
            'title': 'Fix authentication bypass vulnerability in login endpoint',
            'description': 'Addresses CVE-2024-1234 by adding proper input validation and session verification.',
            'expected_intent': 'security'
        },
        {
            'title': 'Add real-time notifications feature for user messages',
            'description': 'Implements WebSocket-based notifications with push notification fallback.',
            'expected_intent': 'feature'
        },
        {
            'title': 'Refactor user service to improve maintainability',
            'description': 'Extracts common logic into utility functions and improves error handling.',
            'expected_intent': 'refactor'
        },
        {
            'title': 'Update dependencies and fix package vulnerabilities',
            'description': 'Updates React to v18, fixes security vulnerabilities in npm packages.',
            'expected_intent': 'dependency'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['title'][:50]}...")
        print(f"Expected Intent: {scenario['expected_intent']}")
        
        if TOOLS_AVAILABLE:
            # For demo purposes, we'll simulate this without actual file changes
            print("   → AI Analysis: [Would analyze with actual file changes]")
        else:
            print("   → AI Analysis: Not available (missing dependencies)")
        
        print(f"   → Description: {scenario['description'][:80]}...")

def demo_impact_prediction():
    """Demo impact prediction functionality"""
    print("\n" + "="*60)
    print("📊 IMPACT PREDICTION DEMO")
    print("="*60)
    
    # Example change scenarios
    scenarios = [
        {
            'name': 'Database Schema Migration',
            'files': ['migrations/001_add_user_preferences.sql', 'models/user.py'],
            'expected_impacts': ['data_integrity', 'reliability']
        },
        {
            'name': 'API Endpoint Changes',
            'files': ['api/users.py', 'api/auth.py'],
            'expected_impacts': ['compatibility', 'security']
        },
        {
            'name': 'Frontend Component Update',
            'files': ['components/UserProfile.tsx', 'components/SearchBar.tsx'],
            'expected_impacts': ['user_experience', 'performance']
        },
        {
            'name': 'Configuration Changes',
            'files': ['config/database.yml', 'dockerfile', '.env.example'],
            'expected_impacts': ['deployment', 'reliability']
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📁 Scenario {i}: {scenario['name']}")
        print(f"Files: {', '.join(scenario['files'])}")
        print(f"Expected Impact Areas: {', '.join(scenario['expected_impacts'])}")
        
        if TOOLS_AVAILABLE:
            print("   → AI Analysis: [Would predict specific impacts and risks]")
        else:
            print("   → AI Analysis: Not available (missing dependencies)")

def demo_dependency_visualization():
    """Demo dependency graph visualization"""
    print("\n" + "="*60)
    print("🕸️ DEPENDENCY GRAPH DEMO")
    print("="*60)
    
    print("Dependency graph visualization shows:")
    print("  • Before/after architectural changes")
    print("  • Impact scope of modifications")
    print("  • Breaking change detection")
    print("  • Circular dependency identification")
    
    if TOOLS_AVAILABLE:
        print("\n📈 Output formats available:")
        print("  • Interactive HTML with D3.js force-directed graph")
        print("  • Graphviz DOT files for publication-quality diagrams")
        print("  • JSON data for integration with other tools")
    else:
        print("\n⚠️ Visualization tools not available (missing dependencies)")

def demo_comprehensive_analysis():
    """Demo comprehensive PR analysis workflow"""
    print("\n" + "="*60)
    print("🤖 COMPREHENSIVE ANALYSIS DEMO")
    print("="*60)
    
    example_pr = {
        'title': 'Implement user authentication with OAuth2 and JWT tokens',
        'description': '''
        This PR implements a complete authentication system:
        - OAuth2 integration with Google and GitHub
        - JWT token generation and validation
        - User session management
        - API endpoint protection
        - Database schema for user accounts
        ''',
        'files_changed': [
            'src/auth/oauth.py',
            'src/auth/jwt_utils.py', 
            'src/api/auth_routes.py',
            'src/models/user.py',
            'migrations/001_create_users.sql',
            'tests/test_auth.py'
        ]
    }
    
    print(f"📝 Example PR: {example_pr['title']}")
    print(f"📁 Files changed: {len(example_pr['files_changed'])}")
    
    print("\n🔍 Analysis Pipeline:")
    print("  1. 🎯 Intent Classification")
    print("     → Primary: FEATURE (authentication system)")
    print("     → Secondary: SECURITY (OAuth2, JWT)")
    print("     → Confidence: 95%")
    
    print("\n  2. 📊 Impact Prediction")
    print("     → Security: HIGH (new auth system)")
    print("     → Compatibility: MEDIUM (new API endpoints)")
    print("     → Data Integrity: HIGH (user schema changes)")
    print("     → Overall Risk: 70% (high-impact change)")
    
    print("\n  3. 🧪 Test Recommendations")
    print("     → Security testing: HIGH priority")
    print("     → Integration testing: HIGH priority")
    print("     → Database migration testing: HIGH priority")
    
    print("\n  4. 📋 Review Recommendations")
    print("     → Security review required")
    print("     → Database migration review")
    print("     → Staged deployment recommended")
    
    print("\n  5. 🚀 Deployment Readiness")
    print("     → Status: CAUTION - High risk deployment")
    print("     → Recommendation: Staged rollout with monitoring")

def demo_integration_workflow():
    """Demo integration with existing GitHub Actions workflow"""
    print("\n" + "="*60)
    print("⚙️ GITHUB ACTIONS INTEGRATION DEMO")
    print("="*60)
    
    workflow_steps = [
        "1. PR opened/updated trigger",
        "2. Extract PR metadata (title, description, files)",
        "3. Run AI-enhanced analysis tools",
        "4. Generate dependency graph visualization",
        "5. Create comprehensive analysis report",
        "6. Post results as PR comment",
        "7. Update PR labels based on analysis",
        "8. Set review requirements based on risk score"
    ]
    
    print("🔄 Automated Workflow Steps:")
    for step in workflow_steps:
        print(f"   {step}")
    
    print("\n📤 Output Artifacts:")
    print("   • Markdown analysis report")
    print("   • JSON data for integrations")
    print("   • Interactive dependency graph (HTML)")
    print("   • Risk assessment summary")
    print("   • Test recommendations")

def main():
    """Run all demos"""
    print("🚀 AI-ENHANCED PR ANALYSIS TOOLS DEMO")
    print("This demo showcases the new AI-powered features for PR analysis")
    
    if not TOOLS_AVAILABLE:
        print("\n⚠️ Note: Tools are not fully available due to missing dependencies.")
        print("Install requirements: pip install -r requirements.txt")
        print("Set up AI environment variables for full functionality.\n")
    
    demo_intent_classification()
    demo_impact_prediction()
    demo_dependency_visualization()
    demo_comprehensive_analysis()
    demo_integration_workflow()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)
    print("Next steps:")
    print("1. Set up AI environment variables (AI_FOUNDRY_ENDPOINT, AI_FOUNDRY_TOKEN)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Test with real PR: python ai_enhanced_pr_analyzer.py --repo .")
    print("4. Integrate with GitHub Actions workflow")
    print("5. Customize analysis rules for your project needs")

if __name__ == "__main__":
    main()
