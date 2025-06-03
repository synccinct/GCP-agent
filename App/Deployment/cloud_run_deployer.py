import asyncio
import json
import time
from typing import Dict, List, Any, Optional
import logging
from google.cloud import run_v2
from google.cloud import artifactregistry_v1
from google.cloud import cloudbuild_v1

class CloudRunDeployer:
    """Advanced Cloud Run deployment with contextual error recovery"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.client = run_v2.ServicesClient()
        self.build_client = cloudbuild_v1.CloudBuildClient()
        self.logger = logging.getLogger(__name__)
    
    async def deploy_application(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy application to Cloud Run with fault tolerance"""
        
        deployment_result = {
            "success": False,
            "service_urls": {},
            "deployment_details": {},
            "errors": [],
            "recovery_actions": []
        }
        
        try:
            # Build container images with exponential backoff
            build_results = await self._build_container_images_with_retry(app_config)
            if not build_results["success"]:
                return self._handle_build_failure(build_results, deployment_result)
            
            # Deploy services with circuit breaker pattern
            for service_config in app_config.get("services", []):
                service_result = await self._deploy_service_with_circuit_breaker(
                    service_config, build_results["images"]
                )
                
                if service_result["success"]:
                    deployment_result["service_urls"][service_config["name"]] = service_result["url"]
                    deployment_result["deployment_details"][service_config["name"]] = service_result
                else:
                    deployment_result["errors"].append(service_result["error"])
                    # Attempt contextual recovery
                    recovery_result = await self._attempt_service_recovery(service_config, service_result)
                    deployment_result["recovery_actions"].append(recovery_result)
            
            # Configure traffic and networking
            networking_result = await self._configure_networking(app_config, deployment_result)
            deployment_result["networking"] = networking_result
            
            # Set up monitoring and alerts
            monitoring_result = await self._setup_monitoring(app_config, deployment_result)
            deployment_result["monitoring"] = monitoring_result
            
            deployment_result["success"] = len(deployment_result["errors"]) == 0
            
        except Exception as e:
            self.logger.error(f"Cloud Run deployment failed: {str(e)}")
            deployment_result["errors"].append(str(e))
            
            # Attempt system-level recovery
            recovery_result = await self._attempt_system_recovery(e, app_config)
            deployment_result["recovery_actions"].append(recovery_result)
        
        return deployment_result
    
    async def _build_container_images_with_retry(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build container images with exponential backoff retry logic"""
        
        build_result = {
            "success": False,
            "images": {},
            "build_logs": []
        }
        
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                for service in app_config.get("services", []):
                    # Generate Dockerfile
                    dockerfile = await self._generate_dockerfile(service)
                    
                    # Create Cloud Build configuration
                    build_config = {
                        "steps": [
                            {
                                "name": "gcr.io/cloud-builders/docker",
                                "args": [
                                    "build",
                                    "-t", f"gcr.io/{self.project_id}/{service['name']}:latest",
                                    "."
                                ]
                            },
                            {
                                "name": "gcr.io/cloud-builders/docker",
                                "args": [
                                    "push",
                                    f"gcr.io/{self.project_id}/{service['name']}:latest"
                                ]
                            }
                        ],
                        "images": [f"gcr.io/{self.project_id}/{service['name']}:latest"]
                    }
                    
                    # Submit build
                    build_operation = await self._submit_build(build_config, service['name'])
                    
                    if build_operation:
                        build_result["images"][service['name']] = f"gcr.io/{self.project_id}/{service['name']}:latest"
                    else:
                        raise Exception(f"Build failed for service: {service['name']}")
                
                build_result["success"] = True
                break
                
            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + (time.time() % 1)
                    self.logger.warning(f"Build attempt {attempt + 1} failed, retrying in {delay:.2f}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Container build failed after {max_retries} attempts: {str(e)}")
                    build_result["error"] = str(e)
        
        return build_result
    
    async def _deploy_service_with_circuit_breaker(self, service_config: Dict[str, Any], 
                                                  images: Dict[str, str]) -> Dict[str, Any]:
        """Deploy individual service with circuit breaker pattern"""
        
        circuit_breaker_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        failure_count = 0
        failure_threshold = 3
        recovery_timeout = 60
        last_failure_time = 0
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            # Check circuit breaker state
            if circuit_breaker_state == "OPEN":
                if time.time() - last_failure_time > recovery_timeout:
                    circuit_breaker_state = "HALF_OPEN"
                    self.logger.info(f"Circuit breaker for {service_config['name']} moved to HALF_OPEN")
                else:
                    return {
                        "success": False,
                        "error": f"Circuit breaker OPEN for service {service_config['name']}",
                        "service_name": service_config["name"],
                        "circuit_breaker_state": circuit_breaker_state
                    }
            
            try:
                # Create Cloud Run service configuration
                service = self._create_service_config(service_config, images)
                
                # Deploy service
                parent = f"projects/{self.project_id}/locations/{self.region}"
                operation = self.client.create_service(parent=parent, service=service)
                
                # Wait for operation to complete
                result = operation.result(timeout=300)  # 5 minutes timeout
                
                # Success - reset circuit breaker
                if circuit_breaker_state == "HALF_OPEN":
                    circuit_breaker_state = "CLOSED"
                    failure_count = 0
                    self.logger.info(f"Circuit breaker for {service_config['name']} reset to CLOSED")
                
                return {
                    "success": True,
                    "url": result.status.url,
                    "service_name": service_config["name"],
                    "retry_count": retry_count,
                    "circuit_breaker_state": circuit_breaker_state
                }
                
            except Exception as e:
                retry_count += 1
                failure_count += 1
                last_failure_time = time.time()
                
                self.logger.warning(f"Service deployment attempt {retry_count} failed: {str(e)}")
                
                # Update circuit breaker state
                if failure_count >= failure_threshold:
                    circuit_breaker_state = "OPEN"
                    self.logger.warning(f"Circuit breaker for {service_config['name']} moved to OPEN")
                
                if retry_count < max_retries and circuit_breaker_state != "OPEN":
                    # Exponential backoff with jitter
                    wait_time = (2 ** retry_count) + (time.time() % 1)
                    await asyncio.sleep(wait_time)
                    
                    # Contextual recovery: adjust configuration based on error
                    service_config = await self._adjust_config_for_retry(service_config, e)
                else:
                    return {
                        "success": False,
                        "error": str(e),
                        "service_name": service_config["name"],
                        "retry_count": retry_count,
                        "circuit_breaker_state": circuit_breaker_state
                    }
    
    def _create_service_config(self, service_config: Dict[str, Any], images: Dict[str, str]) -> run_v2.Service:
        """Create Cloud Run service configuration"""
        
        service = run_v2.Service()
        service.metadata.name = service_config["name"]
        
        # Container configuration
        container = run_v2.Container()
        container.image = images.get(service_config["name"])
        container.ports = [run_v2.ContainerPort(container_port=8080)]
        
        # Resource limits
        resources = run_v2.ResourceRequirements()
        resources.limits = {
            "cpu": "1",
            "memory": "2Gi"
        }
        container.resources = resources
        
        # Service template
        template = run_v2.RevisionTemplate()
        template.spec.containers = [container]
        template.spec.max_instance_request_concurrency = 100
        
        service.spec.template = template
        
        return service
      
