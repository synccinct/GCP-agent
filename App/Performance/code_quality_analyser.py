"""
Code quality analysis module
"""
import asyncio
from typing import Dict, Any, List
import re


class CodeQualityAnalyzer:
    """Analyze generated code quality"""
    
    def __init__(self):
        self.quality_thresholds = {
            "cyclomatic_complexity": 10,
            "maintainability_index": 85,
            "code_coverage": 70,
            "duplication_ratio": 0.05
        }
    
    async def analyze_generated_code(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze quality of generated code"""
        
        analysis_results = {}
        
        for file_path, code_content in code_files.items():
            file_analysis = {
                "complexity": self._calculate_complexity(code_content),
                "maintainability": self._calculate_maintainability(code_content),
                "style_compliance": self._check_style_compliance(code_content, file_path),
                "security_issues": self._check_security_issues(code_content),
                "documentation_coverage": self._check_documentation(code_content)
            }
            
            analysis_results[file_path] = file_analysis
        
        # Overall quality score
        overall_score = self._calculate_overall_quality_score(analysis_results)
        
        return {
            "files": analysis_results,
            "overall_score": overall_score,
            "meets_criteria": overall_score >= self.quality_thresholds["maintainability_index"]
        }
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified complexity calculation
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'and', 'or']
        complexity = 1  # Base complexity
        
        for keyword in complexity_keywords:
            complexity += code.count(keyword)
        
        return complexity
    
    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index"""
        # Simplified maintainability calculation
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 100.0
        
        # Factors affecting maintainability
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        complexity = self._calculate_complexity(code)
        comment_ratio = sum(1 for line in lines if line.strip().startswith('#')) / len(lines)
        
        # Simplified maintainability score
        maintainability = 100 - (avg_line_length * 0.1) - (complexity * 2) + (comment_ratio * 20)
        
        return max(0, min(100, maintainability))
    
    def _check_style_compliance(self, code: str, file_path: str) -> Dict[str, Any]:
        """Check code style compliance"""
        
        issues = []
        
        # Check for PEP 8 violations (simplified)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Line length check
            if len(line) > 88:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(f"Line {i}: Trailing whitespace")
            
            # Multiple imports on one line
            if line.strip().startswith('import ') and ',' in line:
                issues.append(f"Line {i}: Multiple imports on one line")
        
        return {
            "issues": issues,
            "compliance_score": max(0, 100 - len(issues) * 5)
        }
    
    def _check_security_issues(self, code: str) -> Dict[str, Any]:
        """Check for potential security issues"""
        
        security_issues = []
        
        # Check for potential security vulnerabilities
        security_patterns = [
            (r'eval\(', "Use of eval() function"),
            (r'exec\(', "Use of exec() function"),
            (r'__import__\(', "Use of __import__() function"),
            (r'pickle\.loads?\(', "Use of pickle without proper validation"),
            (r'subprocess\.call\(.*shell=True', "Shell injection risk"),
            (r'os\.system\(', "Use of os.system()"),
            (r'input\(.*\)', "Use of input() function"),
        ]
        
        for pattern, description in security_patterns:
            if re.search(pattern, code):
                security_issues.append(description)
        
        return {
            "issues": security_issues,
            "security_score": max(0, 100 - len(security_issues) * 20)
        }
    
    def _check_documentation(self, code: str) -> Dict[str, Any]:
        """Check documentation coverage"""
        
        lines = code.split('\n')
        
        # Count functions and classes
        function_pattern = r'^\s*def\s+\w+'
        class_pattern = r'^\s*class\s+\w+'
        docstring_pattern = r'^\s*""".*"""'
        
        functions = len(re.findall(function_pattern, code, re.MULTILINE))
        classes = len(re.findall(class_pattern, code, re.MULTILINE))
        docstrings = len(re.findall(docstring_pattern, code, re.MULTILINE | re.DOTALL))
        
        total_definitions = functions + classes
        coverage = (docstrings / total_definitions * 100) if total_definitions > 0 else 100
        
        return {
            "functions": functions,
            "classes": classes,
            "docstrings": docstrings,
            "coverage_percentage": coverage
        }
    
    def _calculate_overall_quality_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        
        if not analysis_results:
            return 0.0
        
        total_score = 0.0
        file_count = len(analysis_results)
        
        for file_analysis in analysis_results.values():
            file_score = (
                file_analysis["maintainability"] * 0.4 +
                file_analysis["style_compliance"]["compliance_score"] * 0.3 +
                file_analysis["security_issues"]["security_score"] * 0.2 +
                file_analysis["documentation_coverage"]["coverage_percentage"] * 0.1
            )
            total_score += file_score
        
        return total_score / file_count
    
    def update_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update quality thresholds"""
        self.quality_thresholds.update(new_thresholds)
    
    def get_thresholds(self) -> Dict[str, Any]:
        """Get current quality thresholds"""
        return self.quality_thresholds.copy()
