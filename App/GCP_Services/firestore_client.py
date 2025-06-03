from google.cloud import firestore
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class FirestoreClient:
    """Firestore client with enhanced functionality"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.db = firestore.Client(project=project_id)
        self.logger = logging.getLogger(__name__)
    
    async def create_document(self, collection: str, data: Dict[str, Any], doc_id: str = None) -> str:
        """Create a document in Firestore"""
        
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
            else:
                doc_ref = self.db.collection(collection).document()
            
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            doc_ref.set(data)
            return doc_ref.id
            
        except Exception as e:
            self.logger.error(f"Failed to create document: {str(e)}")
            raise
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
            
        except Exception as e:
            self.logger.error(f"Failed to get document: {str(e)}")
            return None
    
    async def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in Firestore"""
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            data['updated_at'] = datetime.utcnow()
            doc_ref.update(data)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update document: {str(e)}")
            return False
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from Firestore"""
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    async def query_collection(self, collection: str, filters: List[tuple] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query a collection with optional filters"""
        
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed to query collection: {str(e)}")
            return []
