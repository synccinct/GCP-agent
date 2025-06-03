"""Vector-based pattern matching and similarity search using Firestore."""

import asyncio
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from google.cloud import firestore
from sentence_transformers import SentenceTransformer

class FirestoreVectorStore:
    """Vector store for pattern matching and similarity search."""
    
    def __init__(self, firestore_client, collection_name: str = "vector_patterns"):
        self.db = firestore_client
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentence transformer for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Vector dimensions
        self.vector_dim = 384  # all-MiniLM-L6-v2 output dimension
        
        # Cache for frequently accessed vectors
        self.vector_cache: Dict[str, np.ndarray] = {}
        self.cache_max_size = 1000
    
    async def store_pattern(self, pattern_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Store a pattern with its vector embedding."""
        
        try:
            # Generate embedding
            embedding = self.encoder.encode(content)
            
            # Prepare document
            doc_data = {
                "pattern_id": pattern_id,
                "content": content,
                "embedding": embedding.tolist(),
                "metadata": metadata or {},
                "created_at": time.time(),
                "updated_at": time.time(),
                "access_count": 0
            }
            
            # Store in Firestore
            doc_ref = self.db.collection(self.collection_name).document(pattern_id)
            doc_ref.set(doc_data)
            
            # Update cache
            self.vector_cache[pattern_id] = embedding
            self._manage_cache_size()
            
            self.logger.debug(f"Stored pattern: {pattern_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store pattern {pattern_id}: {str(e)}")
            return False
    
    async def find_similar_patterns(self, query: str, top_k: int = 5, 
                                  threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find similar patterns using vector similarity search."""
        
        try:
            # Generate query embedding
            query_embedding = self.encoder.encode(query)
            
            # Get all patterns from Firestore
            patterns_ref = self.db.collection(self.collection_name)
            docs = patterns_ref.stream()
            
            similarities = []
            
            for doc in docs:
                doc_data = doc.to_dict()
                pattern_embedding = np.array(doc_data["embedding"])
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, pattern_embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        "pattern_id": doc_data["pattern_id"],
                        "content": doc_data["content"],
                        "similarity": similarity,
                        "metadata": doc_data.get("metadata", {}),
                        "access_count": doc_data.get("access_count", 0)
                    })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:top_k]
            
            # Update access counts for returned patterns
            await self._update_access_counts([r["pattern_id"] for r in results])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to find similar patterns: {str(e)}")
            return []
    
    async def store_application_pattern(self, app_id: str, requirements: str, 
                                      architecture: Dict[str, Any], success_metrics: Dict[str, Any]) -> bool:
        """Store successful application pattern for future reference."""
        
        try:
            # Create pattern content for embedding
            pattern_content = f"""
            Requirements: {requirements}
            Architecture: {architecture.get('description', '')}
            Components: {', '.join([c.get('component_type', '') for c in architecture.get('components', [])])}
            Frameworks: {', '.join([c.get('framework', '') for c in architecture.get('components', [])])}
            """
            
            metadata = {
                "type": "application_pattern",
                "app_id": app_id,
                "architecture": architecture,
                "success_metrics": success_metrics,
                "component_count": len(architecture.get('components', [])),
                "complexity": architecture.get('complexity', 'medium')
            }
            
            pattern_id = f"app_pattern_{app_id}"
            return await self.store_pattern(pattern_id, pattern_content.strip(), metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to store application pattern: {str(e)}")
            return False
    
    async def find_similar_applications(self, requirements: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find similar applications based on requirements."""
        
        # Add context to improve matching
        query_content = f"Requirements: {requirements}"
        
        patterns = await self.find_similar_patterns(query_content, top_k, threshold=0.6)
        
        # Filter for application patterns only
        app_patterns = [p for p in patterns if p.get("metadata", {}).get("type") == "application_pattern"]
        
        return app_patterns
    
    async def store_error_pattern(self, error_signature: str, error_context: Dict[str, Any], 
                                solution: Dict[str, Any]) -> bool:
        """Store error pattern and its solution."""
        
        try:
            pattern_content = f"""
            Error: {error_signature}
            Context: {error_context.get('component', '')} {error_context.get('operation', '')}
            Solution: {solution.get('description', '')}
            """
            
            metadata = {
                "type": "error_pattern",
                "error_signature": error_signature,
                "error_context": error_context,
                "solution": solution,
                "resolution_success_rate": solution.get("success_rate", 0.0)
            }
            
            pattern_id = f"error_pattern_{hash(error_signature)}"
            return await self.store_pattern(pattern_id, pattern_content.strip(), metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to store error pattern: {str(e)}")
            return False
    
    async def find_error_solutions(self, error_signature: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find solutions for similar errors."""
        
        query_content = f"Error: {error_signature} Context: {context.get('component', '')}"
        
        patterns = await self.find_similar_patterns(query_content, top_k=5, threshold=0.8)
        
        # Filter for error patterns and sort by success rate
        error_patterns = [p for p in patterns if p.get("metadata", {}).get("type") == "error_pattern"]
        error_patterns.sort(key=lambda x: x.get("metadata", {}).get("solution", {}).get("success_rate", 0), reverse=True)
        
        return error_patterns
    
    async def store_code_pattern(self, pattern_type: str, code_snippet: str, 
                               framework: str, use_case: str) -> bool:
        """Store reusable code patterns."""
        
        try:
            pattern_content = f"""
            Type: {pattern_type}
            Framework: {framework}
            Use Case: {use_case}
            Code: {code_snippet[:500]}  # Truncate for embedding
            """
            
            metadata = {
                "type": "code_pattern",
                "pattern_type": pattern_type,
                "framework": framework,
                "use_case": use_case,
                "code_snippet": code_snippet,
                "code_length": len(code_snippet)
            }
            
            pattern_id = f"code_pattern_{pattern_type}_{framework}_{hash(code_snippet)}"
            return await self.store_pattern(pattern_id, pattern_content.strip(), metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to store code pattern: {str(e)}")
            return False
    
    async def find_code_patterns(self, pattern_type: str, framework: str, 
                               use_case: str = None) -> List[Dict[str, Any]]:
        """Find relevant code patterns."""
        
        query_parts = [f"Type: {pattern_type}", f"Framework: {framework}"]
        if use_case:
            query_parts.append(f"Use Case: {use_case}")
        
        query_content = " ".join(query_parts)
        
        patterns = await self.find_similar_patterns(query_content, top_k=10, threshold=0.7)
        
        # Filter for code patterns
        code_patterns = [p for p in patterns if p.get("metadata", {}).get("type") == "code_pattern"]
        
        return code_patterns
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _manage_cache_size(self):
        """Manage vector cache size."""
        
        if len(self.vector_cache) > self.cache_max_size:
            # Remove oldest entries (simple LRU)
            items_to_remove = len(self.vector_cache) - self.cache_max_size + 100
            keys_to_remove = list(self.vector_cache.keys())[:items_to_remove]
            
            for key in keys_to_remove:
                del self.vector_cache[key]
    
    async def _update_access_counts(self, pattern_ids: List[str]):
        """Update access counts for patterns."""
        
        try:
            batch = self.db.batch()
            
            for pattern_id in pattern_ids:
                doc_ref = self.db.collection(self.collection_name).document(pattern_id)
                batch.update(doc_ref, {
                    "access_count": firestore.Increment(1),
                    "last_accessed": time.time()
                })
            
            batch.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update access counts: {str(e)}")
    
    async def get_popular_patterns(self, pattern_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular patterns by access count."""
        
        try:
            query = self.db.collection(self.collection_name)
            
            if pattern_type:
                query = query.where("metadata.type", "==", pattern_type)
            
            query = query.order_by("access_count", direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            
            patterns = []
            for doc in docs:
                doc_data = doc.to_dict()
                patterns.append({
                    "pattern_id": doc_data["pattern_id"],
                    "content": doc_data["content"],
                    "metadata": doc_data.get("metadata", {}),
                    "access_count": doc_data.get("access_count", 0),
                    "created_at": doc_data.get("created_at")
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to get popular patterns: {str(e)}")
            return []
    
    async def cleanup_old_patterns(self, max_age_days: int = 90) -> int:
        """Clean up old, unused patterns."""
        
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            
            # Find old patterns with low access counts
            query = self.db.collection(self.collection_name).where("created_at", "<", cutoff_time).where("access_count", "<", 5)
            
            docs = query.stream()
            deleted_count = 0
            
            batch = self.db.batch()
            batch_count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                batch_count += 1
                deleted_count += 1
                
                # Commit in batches of 500
                if batch_count >= 500:
                    batch.commit()
                    batch = self.db.batch()
                    batch_count = 0
            
            # Commit remaining
            if batch_count > 0:
                batch.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old patterns")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old patterns: {str(e)}")
            return 0
                  
