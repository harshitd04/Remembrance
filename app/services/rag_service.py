"""
RAG (Retrieval-Augmented Generation) service using LangChain.
"""
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import logging
from langchain_openai import ChatOpenAI
from app.services.embedding_service import EmbeddingService
from app.services.json_storage_service import JSONStorageService

logger = logging.getLogger(__name__)


class RAGService:
    """Implement semantic search using RAG with LangChain."""
    
    def __init__(self, api_key: str, username: str = 'harshit'):
        """
        Initialize RAG service.
        
        Args:
            api_key: OpenAI API key
            username: Username for user-specific data access
        """
        self.embedding_service = EmbeddingService(api_key)
        self.storage = JSONStorageService(username=username)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
    
    def semantic_search(self, query: str, top_k: int = 5, 
                       date_range: Optional[Dict] = None) -> Dict:
        """
        Perform semantic search using embeddings and RAG.
        
        Args:
            query: Search query
            top_k: Number of results to return
            date_range: Optional dict with 'start' and 'end' dates
            
        Returns:
            Dictionary with results and AI summary
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            
            # Load all stored embeddings
            all_embeddings = self.storage.load_all_embeddings()
            
            # Calculate similarity scores
            similarities = []
            for entry_id, stored_data in all_embeddings.items():
                stored_embedding = np.array(stored_data['embedding'])
                score = self._cosine_similarity(query_embedding, stored_embedding)
                
                # Filter by date range if provided
                if date_range:
                    entry_date = datetime.fromisoformat(stored_data['date'])
                    start_date = datetime.fromisoformat(date_range['start'])
                    end_date = datetime.fromisoformat(date_range['end'])
                    
                    if not (start_date <= entry_date <= end_date):
                        continue
                
                similarities.append({
                    "entry_id": entry_id,
                    "date": stored_data['date'],
                    "similarity": float(score),
                    "text": stored_data['text_preview'],
                    "relevance_score": float(score)
                })
            
            # Sort by similarity and get top-k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            results = similarities[:top_k]
            
            # Generate contextual answer using LLM
            ai_summary = ""
            if results:
                context = "\n".join([r['text'] for r in results])
                ai_summary = self._generate_answer(query, context)
            
            logger.info(f"Semantic search completed: {len(results)} results")
            
            return {
                "results": results,
                "ai_summary": ai_summary,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}", exc_info=True)
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        vec1_arr = np.array(vec1)
        dot_product = np.dot(vec1_arr, vec2)
        norm1 = np.linalg.norm(vec1_arr)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _generate_answer(self, query: str, context: str) -> str:
        """
        Generate contextual answer using GPT-4o Mini.
        
        Args:
            query: User query
            context: Retrieved context from journal entries
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""Based on the following journal entries, answer this question:

Question: {query}

Journal entries:
{context}

Provide a concise, thoughtful answer based on the entries."""
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Answer generation error: {str(e)}", exc_info=True)
            return "Unable to generate summary at this time."
