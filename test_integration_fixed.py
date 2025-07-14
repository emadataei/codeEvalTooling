#!/usr/bin/env python3
"""
Test script to demonstrate the Quality Gate + Cognitive Analysis integration.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scoring.quality_gate import QualityGate

# Try to import cognitive analyzer, fallback if AI dependencies missing
try:
    from scoring.cognitive_analyzer import CognitiveAnalyzer
    COGNITIVE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Cognitive Analyzer not available: {e}")
    print("Quality Gate tests will still run, but cognitive analysis will be skipped.")
    COGNITIVE_AVAILABLE = False


def test_integration():
    """Test the integration between Quality Gate and Cognitive Analysis."""
    
    # Sample code with quality issues
    bad_code = '''
import os

# TODO fix this later
def process_data(data):
    print("Processing data...")  # Debug statement
    password = "hardcoded123"  # Security issue
    
    result = []
    for item in data:
        if item:
            if item.type == "special":
                if item.value > 100:
                    if item.category == "premium":
                        if item.status == "active":
                            if item.verified:
                                # Very nested logic - complexity issue
                                result.append(item.value * 2)
    
    # Long function continues...
    # ... (imagine 100+ more lines)
    
    return result
'''
    
    # Sample good code
    good_code = '''
def calculate_total(items: List[Item]) -> int:
    """Calculate total value of active items.
    
    Args:
        items: List of items to calculate total for
        
    Returns:
        Total value of all active items
    """
    return sum(item.value for item in items if item.is_active())


def process_items(items: List[Item]) -> Dict[str, int]:
    """Process items and return summary statistics.
    
    Args:
        items: List of items to process
        
    Returns:
        Dictionary with summary statistics
    """
    return {
        "total": calculate_total(items),
        "count": len(items),
        "active_count": sum(1 for item in items if item.is_active())
    }
'''

    # Simulate file changes
    pr_files_bad = [
        {
            'path': 'src/bad_module.py',
            'content': bad_code,
            'language': 'python'
        }
    ]
    
    pr_files_good = [
        {
            'path': 'src/good_module.py',
            'content': good_code,
            'language': 'python'
        }
    ]
    
    print("TESTING: Quality Gate + Cognitive Analysis Integration\n")
    
    # Test bad code
    print("=" * 60)
    print("TESTING BAD CODE (should fail quality gate)")
    print("=" * 60)
    
    quality_gate = QualityGate()
    bad_quality_result = quality_gate.analyze_pr(pr_files_bad)
    
    print(f"Quality Gate Result: {bad_quality_result.summary}")
    print(f"Quality Score: {bad_quality_result.quality_score}/100")
    print(f"Quality Penalty: {bad_quality_result.quality_penalty}")
    print(f"Blocking Issues: {len(bad_quality_result.blocking_issues)}")
    print(f"Warning Issues: {len(bad_quality_result.warning_issues)}")
    
    if bad_quality_result.blocking_issues:
        print("\nBLOCKING Issues:")
        for issue in bad_quality_result.blocking_issues:
            print(f"  - {issue.category}: {issue.message}")
    
    if not bad_quality_result.passed:
        print("\nQuality Gate FAILED - Cognitive analysis would be BLOCKED")
    else:
        print("\nQuality Gate passed - proceeding to cognitive analysis")
        
        if COGNITIVE_AVAILABLE:
            try:
                cognitive_analyzer = CognitiveAnalyzer()
                bad_cognitive_result = cognitive_analyzer.analyze_pr(
                    pr_files_bad, 
                    quality_penalty=bad_quality_result.quality_penalty
                )
                
                print("\nCognitive Analysis:")
                print(f"  Tier: {bad_cognitive_result.tier}")
                print(f"  Total Score: {bad_cognitive_result.total_score}")
                print(f"  Quality Penalty: {bad_cognitive_result.quality_penalty}")
                print(f"  Reasoning: {bad_cognitive_result.reasoning}")
                
            except Exception as e:
                print(f"\nWARNING: Cognitive analysis failed (likely AI client issue): {e}")
        else:
            print("\nWARNING: Cognitive analysis skipped (dependencies not available)")
            print("   In CI/CD, this would calculate a tier based on static analysis")
    
    # Test good code
    print("\n" + "=" * 60)
    print("TESTING GOOD CODE (should pass quality gate)")
    print("=" * 60)
    
    good_quality_result = quality_gate.analyze_pr(pr_files_good)
    
    print(f"Quality Gate Result: {good_quality_result.summary}")
    print(f"Quality Score: {good_quality_result.quality_score}/100")
    print(f"Quality Penalty: {good_quality_result.quality_penalty}")
    print(f"Blocking Issues: {len(good_quality_result.blocking_issues)}")
    print(f"Warning Issues: {len(good_quality_result.warning_issues)}")
    
    if good_quality_result.passed:
        print("\nQuality Gate PASSED - proceeding to cognitive analysis")
        
        if COGNITIVE_AVAILABLE:
            try:
                cognitive_analyzer = CognitiveAnalyzer()
                good_cognitive_result = cognitive_analyzer.analyze_pr(
                    pr_files_good, 
                    quality_penalty=good_quality_result.quality_penalty
                )
                
                print("\nCognitive Analysis:")
                print(f"  Tier: {good_cognitive_result.tier}")
                print(f"  Total Score: {good_cognitive_result.total_score}")
                print(f"  Quality Penalty: {good_cognitive_result.quality_penalty}")
                print(f"  Reasoning: {good_cognitive_result.reasoning}")
                
            except Exception as e:
                print(f"\nWARNING: Cognitive analysis failed (likely AI client issue): {e}")
                print("This is expected if AI_FOUNDRY_* environment variables are not set")
        else:
            print("\nWARNING: Cognitive analysis skipped (dependencies not available)")
            print("   In CI/CD, this would calculate a tier based on static analysis")
    
    print("\n" + "=" * 60)
    print("Integration Test Complete!")
    print("=" * 60)
    print("\nKey Points:")
    print("1. Quality Gate runs FIRST and can block cognitive analysis")
    print("2. Quality penalty is added to cognitive score")
    print("3. Poor quality code gets higher tier assignment")
    print("4. Good quality code gets lower tier assignment")
    print("\nIntegration in CI/CD:")
    print("- Quality Gate failures → PR blocked, cannot merge")
    print("- Quality Gate warnings → Cognitive penalty, higher review tier")
    print("- Both pass → Appropriate tier assignment for review")


if __name__ == '__main__':
    test_integration()
