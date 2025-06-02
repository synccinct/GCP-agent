FIRESTORE_CLIENT_TEMPLATE = """
from google.cloud import firestore
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirestoreClient:
    def __init__(self, project_id: Optional[str] = None):
        self.db = firestore.Client(project=project_id)
    
    async def create_document(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
            else:
                doc_ref = self.db.collection(collection).document()
            
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            doc_ref.set(data)
            logger.info(f"Document created in {collection} with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise
    
    async def get_collection(self, collection: str, limit: Optional[int] = None, 
                           where_clauses: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        try:
            query = self.db.collection(collection)
            
            if where_clauses:
                for field, operator, value in where_clauses:
                    query = query.where(field, operator, value)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            raise
    
    async def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            data['updated_at'] = datetime.utcnow()
            doc_ref.update(data)
            logger.info(f"Document updated in {collection} with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            logger.info(f"Document deleted from {collection} with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    async def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        try:
            batch = self.db.batch()
            
            for operation in operations:
                op_type = operation['type']
                collection = operation['collection']
                doc_id = operation.get('doc_id')
                data = operation.get('data', {})
                
                if op_type == 'create':
                    doc_ref = self.db.collection(collection).document(doc_id) if doc_id else self.db.collection(collection).document()
                    data['created_at'] = datetime.utcnow()
                    data['updated_at'] = datetime.utcnow()
                    batch.set(doc_ref, data)
                elif op_type == 'update':
                    doc_ref = self.db.collection(collection).document(doc_id)
                    data['updated_at'] = datetime.utcnow()
                    batch.update(doc_ref, data)
                elif op_type == 'delete':
                    doc_ref = self.db.collection(collection).document(doc_id)
                    batch.delete(doc_ref)
            
            batch.commit()
            logger.info(f"Batch operation completed with {len(operations)} operations")
            return True
        except Exception as e:
            logger.error(f"Error in batch operation: {e}")
            raise
"""

FIRESTORE_MODELS_TEMPLATE = """
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class BaseModel:
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class User(BaseModel):
    email: str
    name: str
    role: str = "user"
    is_active: bool = True
    
@dataclass
class Project(BaseModel):
    name: str
    description: str
    owner_id: str
    status: str = "active"
    
@dataclass
class Task(BaseModel):
    title: str
    description: str
    project_id: str
    assignee_id: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    due_date: Optional[datetime] = None
"""
