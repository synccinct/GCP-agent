"""
Comprehensive performance test suite
"""
import asyncio
from typing import Dict, Any, List
from performance_monitor import PerformanceMonitor
from metrics_collector import PerformanceCriteriaValidator
from code_quality_analyzer import CodeQualityAnalyzer
from integration_test_framework import IntegrationTestFramework


class PerformanceTestSuite:
    """Comprehensive performance testing suite"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.validator = PerformanceCriteriaValidator()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.integration_tester = IntegrationTestFramework()
    
    async def run_comprehensive_test(self, 
                                   modules: List[Dict[str, Any]], 
                                   code_files: Dict[str, str]) -> Dict[str, Any]:
        """Run comprehensive performance and quality tests"""
        
        test_results = {
            "timestamp": asyncio.get_event_loop().time(),
            "performance_metrics": {},
            "code_quality": {},
            "integration_tests": {},
            "overall_score": 0.0,
            "meets_all_criteria": False
        }
        
        # Performance monitoring tests
        perf_results = await self._run_performance_tests(modules)
        test_results["performance_metrics"] = perf_results
        
        # Code quality analysis
        quality_results = await self.quality_analyzer.analyze_generated_code(code_files)
        test_results["code_quality"] = quality_results
        
        # Integration tests
        integration_results = await self.integration_tester.test_module_integration(modules)
        test_results["integration_tests"] = integration_results
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(test_results)
        test_results["overall_score"] = overall_score
        
        # Check if all criteria are met
        test_results["meets_all_criteria"] = self._check_all_criteria(test_results)
        
        return test_results
    
    async def _run_performance_tests(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run performance monitoring tests"""
        
        results = {}
        
        # Simulate module generation performance tests
        for i, module in enumerate(modules):
            operation_id = f"module_gen_{i}"
            self.monitor.start_operation(operation_id, "module_generation")
            
            # Simulate module generation time
            await asyncio.sleep(0.1)  # Simulate work
            
            self.monitor.end_operation(operation_id, success=True)
        
        # Get performance statistics
        module_stats = self.monitor.get_performance_stats("module_generation")
        results["module_generation"] = module_stats
        
        # Validate against criteria
        validation_results = self.validator.validate_overall_performance(self.monitor)
        results["validation"] = validation_results
        
        return results
    
    def _calculate_overall_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        
        scores = []
        
        # Performance score (30%)
        perf_validation = test_results.get("performance_metrics", {}).get("validation", {})
        perf_score = self._calculate_performance_score(perf_validation)
        scores.append(("performance", perf_score, 0.3))
        
        # Code quality score (40%)
        quality_score = test_results.get("code_quality", {}).get("overall_score", 0)
        scores.append(("quality", quality_score, 0.4))
        
        # Integration score (30%)
        integration_score = test_results.get("integration_tests", {}).get("success_rate", 0) * 100
        scores.append(("integration", integration_score, 0.3))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        return total_score
    
    def _calculate_performance_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate performance score from validation results"""
        
        if not validation_results:
            return 0.0
        
        total_checks = 0
        passed_checks = 0
        
        for category, checks in validation_results.items():
            for check, passed in checks.items():
                total_checks += 1
                if passed:
                    passed_checks += 1
        
        return (passed_checks / total_checks * 100) if total_checks > 0 else 0.0
    
    def _check_all_criteria(self, test_results: Dict[str, Any]) -> bool:
        """Check if all performance criteria are met"""
        
        # Check performance criteria
        perf_validation = test_results.get("performance_metrics", {}).get("validation", {})
        perf_criteria_met = all(
            all(checks.values()) for checks in perf_validation.values()
        ) if perf_validation else False
        
        # Check code quality criteria
        quality_criteria_met = test_results.get("code_quality", {}).get("meets_criteria", False)
        
        # Check integration criteria
        integration_criteria_met = test_results.get("integration_tests", {}).get("meets_criteria", False)
        
        return perf_criteria_met and quality_criteria_met and integration_criteria_met
    
    async def run_stress_test(self, 
                             module_count: int = 50, 
                             concurrent_operations: int = 10) -> Dict[str, Any]:
        """Run stress test with multiple concurrent operations"""
        
        stress_results = {
            "module_count": module_count,
            "concurrent_operations
