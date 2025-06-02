# data_flow_manager.py
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from google.cloud import firestore, pubsub_v1
import numpy as np
from sentence_transformers import SentenceTransformer

class FlowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ERROR = "error"
    BLOCKED = "blocked"

@dataclass
class DataFlowEvent:
    """Event in the data flow pipeline"""
    event_id: str
    event_type: str
    source_component: str
    target_component: str
    payload: Dict[str, Any]
    timestamp: float
    flow_id: str
    metadata: Dict[str, Any]

class AMEMStateManager:
    """A-MEM Architecture: Short-term and Long-term memory management"""
    
    def __init__(self, firestore_client, vector_store):
        self.db = firestore_client
        self.vector_store = vector_store
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
        
        # Store requirements vector for similarity search
        await self._store_requirements_vector(app_state)
        
        return app_state
    
    async def update_application_state(self, app_state_id: str, updates: Dict[str, Any]) -> bool:
        """Update application state"""
        try:
            updates["updated_at"] = time.time()
            
            # Update short-term memory
            if app_state_id in self.short_term_memory:
                self.short_term_memory[app_state_id].update(updates)
            
            # Update Firestore
            await self._update_in_firestore("application_states", app_state_id, updates)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update application state: {str(e)}")
            return False
    
    async def update_component_state(self, app_state_id: str, component_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific component state"""
        try:
            # Get current state
            app_state = await self.get_application_state(app_state_id)
            if not app_state:
                return False
            
            # Update component
            components = app_state.get("components", [])
            for component in components:
                if component.get("id") == component_id:
                    component.update(updates)
                    break
            else:
                # Component not found, add it
                updates["id"] = component_id
                components.append(updates)
            
            # Update application state
            return await self.update_application_state(app_state_id, {"components": components})
            
        except Exception as e:
            self.logger.error(f"Failed to update component state: {str(e)}")
            return False
    
    async def get_application_state(self, app_state_id: str) -> Optional[Dict[str, Any]]:
        """Get application state"""
        # Check short-term memory first
        if app_state_id in self.short_term_memory:
            return self.short_term_memory[app_state_id]
        
        # Check Firestore
        try:
            doc = await self._get_from_firestore("application_states", app_state_id)
            if doc:
                # Load into short-term memory
                self.short_term_memory[app_state_id] = doc
                self._manage_memory_threshold()
            return doc
        except Exception as e:
            self.logger.error(f"Failed to get application state: {str(e)}")
            return None
    
    def _estimate_duration(self, requirements: Dict[str, Any]) -> int:
        """Estimate development duration in hours"""
        complexity = requirements.get("complexity_estimate", "medium")
        word_count = requirements.get("word_count", 0)
        
        base_hours = {
            "low": 8,
            "medium": 24,
            "high": 72
        }
        
        # Adjust based on word count
        complexity_multiplier = max(1.0, word_count / 100)
        
        return int(base_hours.get(complexity, 24) * complexity_multiplier)
    
    async def _store_in_firestore(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """Store data in Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        await doc_ref.set(data)
    
    async def _update_in_firestore(self, collection: str, doc_id: str, updates: Dict[str, Any]):
        """Update data in Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        await doc_ref.update(updates)
    
    async def _get_from_firestore(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get data from Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = await doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def _store_requirements_vector(self, app_state: Dict[str, Any]):
        """Store requirements vector for similarity search"""
        # This would integrate with your vector store
        pass
    
    def _manage_memory_threshold(self):
        """Manage short-term memory threshold"""
        if len(self.short_term_memory) > self.memory_threshold:
            # Remove oldest entries
            oldest_keys = sorted(
                self.short_term_memory.keys(),
                key=lambda k: self.short_term_memory[k].get("updated_at", 0)
            )[:len(self.short_term_memory) - self.memory_threshold]
            
            for key in oldest_keys:
                del self.short_term_memory[key]
      
