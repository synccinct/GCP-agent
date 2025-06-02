"""
Integration testing framework for module compatibility
"""
import asyncio
from typing import List, Dict, Any


class IntegrationTestFramework:
    """Framework for testing module integration"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_module_integration(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test integration between modules"""
        
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Test API compatibility
        api_test_result = await self._test_api_compatibility(modules)
        test_results["test_details"].append(api_test_result)
        test_results["total_tests"] += 1
        if api_test_result["passed"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Test data flow
        data_flow_result = await self._test_data_flow(modules)
        test_results["test_details"].append(data_flow_result)
        test_results["total_tests"] += 1
        if data_flow_result["passed"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Test authentication flow
        auth_test_result = await self._test_authentication_flow(modules)
        test_results["test_details"].append(auth_test_result)
        test_results["total_tests"] += 1
        if auth_test_result["passed"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Test dependency resolution
        dependency_test_result = await self._test_dependency_resolution(modules)
        test_results["test_details"].append(dependency_test_result)
        test_results["total_tests"] += 1
        if dependency_test_result["passed"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Calculate success rate
        test_results["success_rate"] = test_results["passed_tests"] / test_results["total_tests"]
        test_results["meets_criteria"] = test_results["success_rate"] >= 0.90
        
        return test_results
    
    async def _test_api_compatibility(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test API compatibility between modules"""
        
        try:
            # Check if frontend can communicate with backend
            frontend_modules = [m for m in modules if m.get("type") == "frontend"]
            backend_modules = [m for m in modules if m.get("type") == "backend"]
            
            compatibility_issues = []
            
            for frontend in frontend_modules:
                for backend in backend_modules:
                    # Check API contract compatibility
                    if not self._check_api_contract_compatibility(frontend, backend):
                        compatibility_issues.append(
                            f"API incompatibility between {frontend.get('name', 'unknown')} "
                            f"and {backend.get('name', 'unknown')}"
                        )
            
            return {
                "test_name": "API Compatibility",
                "passed": len(compatibility_issues) == 0,
                "issues": compatibility_issues
            }
            
        except Exception as e:
            return {
                "test_name": "API Compatibility",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_data_flow(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test data flow between modules"""
        
        try:
            data_flow_issues = []
            
            # Check data format compatibility
            for i, module_a in enumerate(modules):
                for module_b in modules[i+1:]:
                    if not self._check_data_format_compatibility(module_a, module_b):
                        data_flow_issues.append(
                            f"Data format incompatibility between {module_a.get('name', 'unknown')} "
                            f"and {module_b.get('name', 'unknown')}"
                        )
            
            return {
                "test_name": "Data Flow",
                "passed": len(data_flow_issues) == 0,
                "issues": data_flow_issues
            }
            
        except Exception as e:
            return {
                "test_name": "Data Flow",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_authentication_flow(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test authentication flow between modules"""
        
        try:
            auth_issues = []
            
            # Check if authentication modules are compatible
            auth_modules = [m for m in modules if m.get("type") == "auth" or "auth" in m.get("features", [])]
            
            if auth_modules:
                for auth_module in auth_modules:
                    if not self._validate_auth_module(auth_module):
                        auth_issues.append(f"Authentication module {auth_module.get('name', 'unknown')} validation failed")
            
            return {
                "test_name": "Authentication Flow",
                "passed": len(auth_issues) == 0,
                "issues": auth_issues
            }
            
        except Exception as e:
            return {
                "test_name": "Authentication Flow",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_dependency_resolution(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test dependency resolution between modules"""
        
        try:
            dependency_issues = []
            
            # Check for circular dependencies
            if self._has_circular_dependencies(modules):
                dependency_issues.append("Circular dependencies detected")
            
            # Check for missing dependencies
            missing_deps = self._find_missing_dependencies(modules)
            if missing_deps:
                dependency_issues.extend([f"Missing dependency: {dep}" for dep in missing_deps])
            
            return {
                "test_name": "Dependency Resolution",
                "passed": len(dependency_issues) == 0,
                "issues": dependency_issues
            }
            
        except Exception as e:
            return {
                "test_name": "Dependency Resolution",
                "passed": False,
                "error": str(e)
            }
    
    def _check_api_contract_compatibility(self, frontend: Dict[str, Any], backend: Dict[str, Any]) -> bool:
        """Check API contract compatibility between frontend and backend"""
        
        # Simplified compatibility check
        frontend_api = frontend.get("api_requirements", {})
        backend_api = backend.get("api_endpoints", {})
        
        # Check if required endpoints exist
        for endpoint in frontend_api.get("required_endpoints", []):
            if endpoint not in backend_api.get("available_endpoints", []):
                return False
        
        return True
    
    def _check_data_format_compatibility(self, module_a: Dict[str, Any], module_b: Dict[str, Any]) -> bool:
        """Check data format compatibility between modules"""
        
        # Simplified data format check
        output_format_a = module_a.get("output_format", "json")
        input_format_b = module_b.get("input_format", "json")
        
        return output_format_a == input_format_b
    
    def _validate_auth_module(self, auth_module: Dict[str, Any]) -> bool:
        """Validate authentication module"""
        
        required_features = ["login", "logout", "token_validation"]
        available_features = auth_module.get("features", [])
        
        return all(feature in available_features for feature in required_features)
    
    def _has_circular_dependencies(self, modules: List[Dict[str, Any]]) -> bool:
        """Check for circular dependencies"""
        
        # Simplified circular dependency check
        dependency_graph = {}
        
        for module in modules:
            module_name = module.get("name", "unknown")
            dependencies = module.get("dependencies", [])
            dependency_graph[module_name] = dependencies
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependency_graph:
            if has_cycle(node):
                return True
        
        return False
    
    def _find_missing_dependencies(self, modules: List[Dict[str, Any]]) -> List[str]:
        """Find missing dependencies"""
        
        available_modules = {module.get("name", "unknown") for module in modules}
        missing_deps = []
        
        for module in modules:
            dependencies = module.get("dependencies", [])
            for dep in dependencies:
                if dep not in available_modules:
                    missing_deps.append(dep)
        
        return list(set(missing_deps))
