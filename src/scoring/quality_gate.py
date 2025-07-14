"""
Quality Gate system for PR analysis.

This module implements a quality gate that runs before cognitive scoring
to catch fundamental code quality issues and provide early feedback.
"""

import ast
import re
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


# Constants for repeated strings
CATEGORY_CODE_QUALITY = "Code Quality"
CATEGORY_SECURITY = "Security"
CATEGORY_COMPLEXITY = "Complexity"
CATEGORY_DOCUMENTATION = "Documentation"
CATEGORY_TYPE_SAFETY = "Type Safety"

SUGGESTION_BREAK_FUNCTIONS = "Consider breaking into smaller functions"
SUGGESTION_USE_ENV_VARS = "Use environment variables or secure vault for secrets"
SUGGESTION_USE_PARAMETERIZED = "Use parameterized queries or safe alternatives"


class QualityLevel(Enum):
    """Quality issue severity levels."""
    BLOCKING = "blocking"  # Red flag - must fix
    WARNING = "warning"   # Quality penalty
    ADVISORY = "advisory"  # Suggestion only


@dataclass
class QualityIssue:
    """Represents a single quality issue."""
    level: QualityLevel
    category: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class QualityGateResult:
    """Result of quality gate analysis."""
    passed: bool
    quality_score: int  # 0-100, higher is better
    blocking_issues: List[QualityIssue]
    warning_issues: List[QualityIssue]
    advisory_issues: List[QualityIssue]
    summary: str
    quality_penalty: int  # Penalty to add to cognitive score


class QualityGate:
    """
    Quality gate analyzer that checks fundamental code quality.
    
    This runs before cognitive scoring to catch basic quality issues
    and provide early feedback to developers.
    """
    
    def __init__(self):
        self.security_patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']'
            ],
            'unsafe_eval': [
                r'\beval\s*\(',
                r'\bexec\s*\('
            ]
        }
        
        self.code_smell_patterns = {
            'unused_imports': r'^import\s+\w+(?:\s+as\s+\w+)?$',
            'todo_fixme': r'#\s*(TODO|FIXME|HACK|XXX)',
            'print_debug': r'\bprint\s*\(',
            'console_log': r'\bconsole\.(log|debug|info)\s*\('
        }
    
    def analyze_pr(self, pr_files: List[Dict]) -> QualityGateResult:
        """
        Main entry point for quality gate analysis.
        
        Args:
            pr_files: List of file dictionaries with 'path', 'content', 'language'
            
        Returns:
            QualityGateResult with analysis results
        """
        blocking_issues = []
        warning_issues = []
        advisory_issues = []
        
        for file_info in pr_files:
            file_path = file_info['path']
            content = file_info['content']
            language = file_info.get('language', 'unknown')
            
            # Security checks
            security_issues = self._check_security(file_path, content)
            blocking_issues.extend([i for i in security_issues if i.level == QualityLevel.BLOCKING])
            warning_issues.extend([i for i in security_issues if i.level == QualityLevel.WARNING])
            
            # Code smell checks
            smell_issues = self._check_code_smells(file_path, content, language)
            blocking_issues.extend([i for i in smell_issues if i.level == QualityLevel.BLOCKING])
            warning_issues.extend([i for i in smell_issues if i.level == QualityLevel.WARNING])
            advisory_issues.extend([i for i in smell_issues if i.level == QualityLevel.ADVISORY])
            
            # Function complexity checks
            complexity_issues = self._check_function_complexity(file_path, content, language)
            warning_issues.extend(complexity_issues)
            
            # Documentation checks
            doc_issues = self._check_documentation(file_path, content, language)
            advisory_issues.extend(doc_issues)
        
        # Calculate overall quality score and determine if gate passes
        quality_score = self._calculate_quality_score(blocking_issues, warning_issues, advisory_issues)
        passed = len(blocking_issues) == 0 and quality_score >= 60
        quality_penalty = self._calculate_quality_penalty(blocking_issues, warning_issues)
        
        summary = self._generate_summary(passed, quality_score, blocking_issues, warning_issues)
        
        return QualityGateResult(
            passed=passed,
            quality_score=quality_score,
            blocking_issues=blocking_issues,
            warning_issues=warning_issues,
            advisory_issues=advisory_issues,
            summary=summary,
            quality_penalty=quality_penalty
        )
    
    def _check_security(self, file_path: str, content: str) -> List[QualityIssue]:
        """Check for security vulnerabilities."""
        issues = []
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    
                    if category == 'hardcoded_secrets':
                        issues.append(QualityIssue(
                            level=QualityLevel.BLOCKING,
                            category=CATEGORY_SECURITY,
                            message="Potential hardcoded secret detected",
                            file_path=file_path,
                            line_number=line_no,
                            suggestion=SUGGESTION_USE_ENV_VARS
                        ))
                    elif category in ['sql_injection', 'unsafe_eval']:
                        issues.append(QualityIssue(
                            level=QualityLevel.BLOCKING,
                            category=CATEGORY_SECURITY,
                            message=f"Potential {category.replace('_', ' ')} vulnerability",
                            file_path=file_path,
                            line_number=line_no,
                            suggestion=SUGGESTION_USE_PARAMETERIZED
                        ))
        
        return issues
    
    def _check_code_smells(self, file_path: str, content: str, language: str) -> List[QualityIssue]:
        """Check for code smells."""
        issues = []
        
        # Check TODO/FIXME comments for ticket references
        todo_matches = re.finditer(self.code_smell_patterns['todo_fixme'], content, re.IGNORECASE)
        for match in todo_matches:
            line_no = content[:match.start()].count('\n') + 1
            line_content = content.split('\n')[line_no - 1]
            
            # Check if TODO has a ticket reference (JIRA, GitHub issue, etc.)
            if not re.search(r'(JIRA-\d+|#\d+|TICKET-\d+)', line_content, re.IGNORECASE):
                issues.append(QualityIssue(
                    level=QualityLevel.WARNING,
                    category=CATEGORY_CODE_QUALITY,
                    message="TODO/FIXME comment without ticket reference",
                    file_path=file_path,
                    line_number=line_no,
                    suggestion="Add ticket reference or remove comment if resolved"
                ))
        
        # Debug print statements
        if language == 'python':
            print_matches = re.finditer(self.code_smell_patterns['print_debug'], content)
            for match in print_matches:
                line_no = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_no - 1] if line_no <= len(content.split('\n')) else ""
                
                # Skip print statements that are clearly legitimate (not debug)
                if any(keyword in line_content.lower() for keyword in [
                    'result', 'output', 'summary', 'analysis', 'warning', 'error',
                    'github', 'quality gate', 'cognitive', 'failed', 'passed',
                    'location:', 'suggestion:', 'blocking', 'found', 'could not',
                    'no valid', 'complete'
                ]):
                    continue
                    
                issues.append(QualityIssue(
                    level=QualityLevel.WARNING,
                    category=CATEGORY_CODE_QUALITY,
                    message="Debug print statement found",
                    file_path=file_path,
                    line_number=line_no,
                    suggestion="Remove debug prints or use proper logging"
                ))
        
        elif language in ['javascript', 'typescript']:
            console_matches = re.finditer(self.code_smell_patterns['console_log'], content)
            for match in console_matches:
                line_no = content[:match.start()].count('\n') + 1
                issues.append(QualityIssue(
                    level=QualityLevel.WARNING,
                    category=CATEGORY_CODE_QUALITY,
                    message="Console log statement found",
                    file_path=file_path,
                    line_number=line_no,
                    suggestion="Remove console logs or use proper logging"
                ))
        
        return issues
    
    def _check_function_complexity(self, file_path: str, content: str, language: str) -> List[QualityIssue]:
        """Check for overly complex functions."""
        issues = []
        
        if language == 'python':
            issues.extend(self._check_python_functions(file_path, content))
        else:
            issues.extend(self._check_generic_functions(file_path, content))
        
        return issues
    
    def _check_python_functions(self, file_path: str, content: str) -> List[QualityIssue]:
        """Check Python-specific function complexity."""
        issues = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    issues.extend(self._check_single_python_function(file_path, node))
        
        except SyntaxError:
            # File has syntax errors, will be caught by other tools
            pass
        
        return issues
    
    def _check_single_python_function(self, file_path: str, node: ast.FunctionDef) -> List[QualityIssue]:
        """Check a single Python function for issues."""
        issues = []
        
        # Calculate function length
        func_lines = node.end_lineno - node.lineno + 1
        
        if func_lines > 100:
            issues.append(QualityIssue(
                level=QualityLevel.WARNING,
                category=CATEGORY_COMPLEXITY,
                message=f"Function '{node.name}' is too long ({func_lines} lines)",
                file_path=file_path,
                line_number=node.lineno,
                suggestion=SUGGESTION_BREAK_FUNCTIONS
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            issues.append(QualityIssue(
                level=QualityLevel.ADVISORY,
                category=CATEGORY_DOCUMENTATION,
                message=f"Function '{node.name}' missing docstring",
                file_path=file_path,
                line_number=node.lineno,
                suggestion="Add docstring describing function purpose and parameters"
            ))
        
        return issues
    
    def _check_generic_functions(self, file_path: str, content: str) -> List[QualityIssue]:
        """Check function complexity for non-Python languages."""
        issues = []
        lines = content.split('\n')
        in_function = False
        func_start = 0
        func_name = "unknown"
        
        for i, line in enumerate(lines):
            # Simple heuristic for function detection
            func_match = re.match(r'\s*(function|def|func|fn)\s+(\w+)', line)
            if func_match:
                if in_function and i - func_start > 100:
                    issues.append(QualityIssue(
                        level=QualityLevel.WARNING,
                        category=CATEGORY_COMPLEXITY,
                        message=f"Function '{func_name}' is too long ({i - func_start} lines)",
                        file_path=file_path,
                        line_number=func_start + 1,
                        suggestion=SUGGESTION_BREAK_FUNCTIONS
                    ))
                
                in_function = True
                func_start = i
                func_name = func_match.group(2)
            elif in_function and re.match(r'^(def|function|func|fn|\s*class|\s*})', line):
                if i - func_start > 100:
                    issues.append(QualityIssue(
                        level=QualityLevel.WARNING,
                        category=CATEGORY_COMPLEXITY,
                        message=f"Function '{func_name}' is too long ({i - func_start} lines)",
                        file_path=file_path,
                        line_number=func_start + 1,
                        suggestion=SUGGESTION_BREAK_FUNCTIONS
                    ))
                in_function = False
        
        return issues
    
    def _check_documentation(self, file_path: str, content: str, language: str) -> List[QualityIssue]:
        """Check for documentation quality."""
        issues = []
        
        # Check for type hints in Python
        if language == 'python':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function has type hints
                        has_return_annotation = node.returns is not None
                        has_arg_annotations = any(arg.annotation for arg in node.args.args)
                        
                        if not has_return_annotation and not has_arg_annotations:
                            issues.append(QualityIssue(
                                level=QualityLevel.ADVISORY,
                                category=CATEGORY_TYPE_SAFETY,
                                message=f"Function '{node.name}' missing type hints",
                                file_path=file_path,
                                line_number=node.lineno,
                                suggestion="Add type hints for better code clarity"
                            ))
            except SyntaxError:
                pass
        
        return issues
    
    def _calculate_quality_score(self, blocking: List[QualityIssue], 
                                warning: List[QualityIssue], 
                                advisory: List[QualityIssue]) -> int:
        """Calculate overall quality score (0-100)."""
        base_score = 100
        
        # Heavy penalty for blocking issues
        base_score -= len(blocking) * 30
        
        # Moderate penalty for warnings
        base_score -= len(warning) * 5
        
        # Light penalty for advisory
        base_score -= len(advisory) * 1
        
        return max(0, min(100, base_score))
    
    def _calculate_quality_penalty(self, blocking: List[QualityIssue], 
                                 warning: List[QualityIssue]) -> int:
        """Calculate penalty to add to cognitive score."""
        penalty = 0
        
        # Add penalty for quality issues that make code harder to review
        penalty += len(blocking) * 20  # Blocking issues add significant cognitive load
        penalty += len(warning) * 5   # Warnings add moderate cognitive load
        
        return min(penalty, 40)  # Cap penalty to avoid overwhelming cognitive score
    
    def _generate_summary(self, passed: bool, quality_score: int,
                         blocking: List[QualityIssue], 
                         warning: List[QualityIssue]) -> str:
        """Generate human-readable summary."""
        if not passed:
            return f"Quality gate FAILED (Score: {quality_score}/100) - {len(blocking)} blocking issues must be fixed"
        elif quality_score < 80:
            return f"Quality gate passed with warnings (Score: {quality_score}/100) - {len(warning)} issues to address"
        else:
            return f"Quality gate passed (Score: {quality_score}/100) - Good code quality"
