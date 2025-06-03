import asyncio
import time
from typing import Dict, List, Any, Optional
import logging
from google.cloud import firestore

class AMEMStateManager:
    """A-MEM Architecture: Short-term and Long-term memory management"""
    
    def __init__(self, firestore_client):
        self.db = firestore_client
        self.short_term_memory: Dict[str, Any] = {}  # Active development
        self.memory_threshold = 100  # Max items in short-term memory
        self.logger = logging.getLogger(__name__)
    
    async def create_application_state(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create new application state"""
        
        app_state_id = f"app_{project_id}_{int(time.time())}"
        
        app_state = {
            "app_state_id": app_state_id,
            "project_id": project_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "initializing",
            "requirements": requirements,
            "components": [],
            "integration_status": "pending",
            "deployment_status": "pending",
            "metadata": {
                "complexity": requirements.get("complexity_estimate", "medium"),
                "estimated_duration": self._estimate_duration(requirements)
            }
        }
        
        # Store in short-term memory for active development
        self.short_term_memory[app_state_id] = app_state
        
        # Store in Firestore for persistence
        await self._store_in_firestore("application_states", app_state_id, app_state)
        
        self.logger.info(f"Created application state: {app_state_id}")
        return app_state
    
    async def update_application_state(self, app_state_id: str, updates: Dict[str, Any]) -> bool:
        """Update application state"""
        
        try:
            # Update short-term memory if present
            if app_state_id in self.short_term_memory:
                self.short_term_memory[app_state_id].update(updates)
                self.short_term_memory[app_state_id]["updated_at"] = time.time()
            
            # Update Firestore
            updates["updated_at"] = time.time()
            await self._update_in_firestore("application_states", app_state_id, updates)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update application state {app_state_id}: {str(e)}")
            return False
    
    async def get_application_state(self, app_state_id: str) -> Optional[Dict[str, Any]]:
        """Get application state from memory or storage"""
        
        # Check short-term memory first
        if app_state_id in self.short_term_memory:
            return self.short_term_memory[app_state_id]
        
        # Check Firestore
        state = await self._get_from_firestore("application_states", app_state_id)
        
        if state:
            # Load into short-term memory if space available
            if len(self.short_term_memory) < self.memory_threshold:
                self.short_term_memory[app_state_id] = state
        
        return state
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        return await self._get_from_firestore("task_status", task_id)
    
    async def update_task_status(self, task_id: str, status_update: Dict[str, Any]):
        """Update task status"""
        await self._update_in_firestore("task_status", task_id, status_update)
    
    async def _store_in_firestore(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """Store data in Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.set(data)
    
    async def _update_in_firestore(self, collection: str, doc_id: str, updates: Dict[str, Any]):
        """Update data in Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.update(updates)
    
    async def _get_from_firestore(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get data from Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def _estimate_duration(self, requirements: Dict[str, Any]) -> int:
        """Estimate duration in minutes"""
        complexity = requirements.get("complexity_estimate", "medium")
        feature_count = len(requirements.get("features", []))
        
        base_time = {"low": 10, "medium": 20, "high": 40, "very_high": 60}
        return base_time.get(complexity, 20) + (feature_count * 2)
  
