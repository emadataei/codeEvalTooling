import ast
import re
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from .ai_client_factory import AIClientFactory

@dataclass
class CognitiveScore:
    static_score: int
    impact_score: int
    ai_score: int
    total_score: int
    tier: int
    reasoning: str

class CognitiveAnalyzer:
    def __init__(self):
        # Validate configuration
        AIClientFactory.validate_config()
        
        # Initialize AI Foundry client
        self.ai_client = AIClientFactory.create_client()
        
        self.file_impact_weights = {
            'migration': 10, 'schema': 10, 'api': 8, 'config': 6,
            'security': 8, 'payment': 9, 'test': 2, 'doc': 1
        }
    
    def _get_model_name(self) -> str:
        """Get the model deployment name"""
        return AIClientFactory.get_model_name()
    
    def analyze_pr(self, pr_files: List[Dict]) -> CognitiveScore:
        """Main entry point for analyzing a PR's cognitive complexity"""
        static_score = self._calculate_static_score(pr_files)
        impact_score = self._calculate_impact_score(pr_files)
        ai_score = self._calculate_ai_score(pr_files)
        
        total_score = static_score + impact_score + ai_score
        tier = self._assign_tier(total_score)
        reasoning = self._generate_reasoning(static_score, impact_score, ai_score)
        
        return CognitiveScore(
            static_score=static_score,
            impact_score=impact_score,
            ai_score=ai_score,
            total_score=total_score,
            tier=tier,
            reasoning=reasoning
        )
    
    def _calculate_static_score(self, pr_files: List[Dict]) -> int:
        """Calculate complexity from static analysis"""
        total_score = 0
        
        for file_info in pr_files:
            if file_info['language'] == 'python':
                score = self._analyze_python_complexity(file_info['content'])
            elif file_info['language'] in ['javascript', 'typescript']:
                score = self._analyze_js_complexity(file_info['content'])
            else:
                score = self._analyze_generic_complexity(file_info['content'])
            
            total_score += min(score, 40)  # Cap per file
        
        return min(total_score, 40)  # Cap total static score
    
    def _analyze_python_complexity(self, content: str) -> int:
        """Analyze Python-specific complexity metrics"""
        try:
            tree = ast.parse(content)
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    # Count nested levels
                    depth = self._calculate_nesting_depth(node)
                    complexity += depth
                    
                    # Function length penalty
                    lines = len(content.splitlines())
                    if lines > 50:
                        complexity += 3
                    elif lines > 20:
                        complexity += 1
            
            return complexity
        except Exception:
            return self._analyze_generic_complexity(content)
    
    def _calculate_impact_score(self, pr_files: List[Dict]) -> int:
        """Calculate impact based on files changed and blast radius"""
        impact_score = 0
        
        for file_info in pr_files:
            file_path = file_info['path'].lower()
            
            # File type impact
            for pattern, weight in self.file_impact_weights.items():
                if pattern in file_path:
                    impact_score += weight
                    break
            
            # Cross-module dependencies
            imports = self._count_imports(file_info['content'])
            impact_score += min(imports // 5, 5)  # 1 point per 5 imports, max 5
            
            # Database/API changes
            if any(keyword in file_info['content'].lower() 
                   for keyword in ['database', 'db.', 'api.', 'fetch(', 'axios']):
                impact_score += 3
        
        return min(impact_score, 30)
    
    def _calculate_ai_score(self, pr_files: List[Dict]) -> int:
        """Use AI Foundry to assess code comprehension difficulty"""
        if not self.ai_client:
            return self._heuristic_ai_score(pr_files)
            
        try:
            # Combine all changed code for analysis
            combined_code = "\n".join([f['content'] for f in pr_files[:3]])  # Limit for API
            
            prompt = f"""
            Analyze this code change for cognitive complexity. Rate 0-30 based on:
            - How difficult is this to understand?
            - Are there complex business rules or algorithms?
            - Does this use unusual patterns or anti-patterns?
            - How much domain knowledge is required?
            
            Code:
            {combined_code[:2000]}  # Truncate for API limits
            
            Respond with just a number 0-30.
            """
            
            # Make AI Foundry request
            from azure.ai.inference.models import UserMessage
            messages = [UserMessage(prompt)]
            model_name = self._get_model_name()
            
            response = self.ai_client.complete(
                messages=messages,
                model=model_name,
                max_tokens=10,
                temperature=0.1
            )
            
            score = int(re.search(r'\d+', response.choices[0].message.content).group())
            return min(max(score, 0), 30)
            
        except Exception as e:
            print(f"AI analysis failed: {e}, falling back to heuristic scoring")
            return self._heuristic_ai_score(pr_files)
    
    def _heuristic_ai_score(self, pr_files: List[Dict]) -> int:
        """Fallback heuristic scoring when AI is unavailable"""
        score = 0
        
        for file_info in pr_files:
            content = file_info['content'].lower()
            
            # Complex patterns that indicate higher cognitive load
            if any(pattern in content for pattern in [
                'algorithm', 'recursive', 'optimization', 'performance',
                'threading', 'async', 'promise', 'callback'
            ]):
                score += 5
            
            # Business logic indicators
            if any(pattern in content for pattern in [
                'pricing', 'payment', 'billing', 'discount', 'tax',
                'inventory', 'order', 'subscription'
            ]):
                score += 3
                
            # Complex data structures
            if any(pattern in content for pattern in [
                'nested', 'recursive', 'tree', 'graph', 'matrix'
            ]):
                score += 2
        
        return min(score, 30)
    
    def _assign_tier(self, total_score: int) -> int:
        """Assign tier based on total cognitive score"""
        if total_score <= 25:
            return 0
        elif total_score <= 65:
            return 1
        else:
            return 2
    
    def _calculate_nesting_depth(self, node) -> int:
        """Calculate maximum nesting depth in AST node"""
        max_depth = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                depth = 1
                parent = child
                while hasattr(parent, 'parent'):
                    if isinstance(parent.parent, (ast.If, ast.For, ast.While, ast.With)):
                        depth += 1
                    parent = parent.parent
                max_depth = max(max_depth, depth)
        return max_depth
    
    def _analyze_js_complexity(self, content: str) -> int:
        """Analyze JavaScript/TypeScript complexity"""
        complexity = 0
        
        # Count control structures
        complexity += len(re.findall(r'\b(if|for|while|switch|try|catch)\b', content))
        
        # Count functions
        complexity += len(re.findall(r'\bfunction\b|\b=>\b', content))
        
        # Nested callbacks
        complexity += len(re.findall(r'\.then\(|\.catch\(|callback\(', content))
        
        return complexity
    
    def _analyze_generic_complexity(self, content: str) -> int:
        """Generic complexity analysis for other languages"""
        complexity = 0
        
        # Count control structures
        complexity += len(re.findall(r'\b(if|for|while|switch|try|catch)\b', content, re.IGNORECASE))
        
        # Count brackets (nested structures)
        complexity += content.count('{') // 3  # Rough estimate
        
        # Line count penalty
        lines = len(content.splitlines())
        if lines > 100:
            complexity += 5
        elif lines > 50:
            complexity += 2
        
        return complexity
    
    def _count_imports(self, content: str) -> int:
        """Count import statements in code"""
        import_patterns = [
            r'^\s*import\s+',  # Python/JS imports
            r'^\s*from\s+.*\s+import',  # Python from imports
            r'^\s*#include\s+',  # C/C++ includes
            r'^\s*using\s+',  # C# using
            r'^\s*require\s*\(',  # Node.js requires
        ]
        
        count = 0
        for line in content.splitlines():
            for pattern in import_patterns:
                if re.match(pattern, line):
                    count += 1
                    break
        
        return count
    
    def _generate_reasoning(self, static: int, impact: int, ai: int) -> str:
        """Generate human-readable explanation of scoring"""
        reasons = []
        
        if static > 20:
            reasons.append(f"High static complexity ({static}/40)")
        if impact > 15:
            reasons.append(f"Significant impact surface ({impact}/30)")
        if ai > 20:
            reasons.append(f"AI flagged as complex ({ai}/30)")
            
        if not reasons:
            return "Low complexity change, suitable for automated review"
        
        return "Requires human review: " + ", ".join(reasons)
