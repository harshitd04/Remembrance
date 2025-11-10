"""
OpenAI Text-Embedding-3-Small service for generating embeddings.
"""
import openai
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handle text embedding generation using OpenAI."""
    
    def __init__(self, api_key: str):
        """
        Initialize embedding service.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text (length: {len(text)})")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}", exc_info=True)
            raise
    
    def embed_multiple(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding error: {str(e)}", exc_info=True)
            raise
