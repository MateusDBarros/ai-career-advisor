"""Embedding generation service using IBM watsonx.ai.

This module handles converting text into vector embeddings using IBM's
embedding models (like Slate). These embeddings are used for semantic search
in the vector store.

Key concepts:
- Embeddings are numerical representations of text
- Similar texts have similar embeddings (measured by cosine similarity)
- Embeddings enable semantic search beyond keyword matching
"""

from typing import List

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using IBM watsonx.ai.
    
    This service converts text into vector embeddings that can be stored
    in a vector database and used for similarity search.
    
    TODO: Implement the following methods:
    1. __init__: Initialize the embedding model
    2. embed_text: Generate embedding for a single text
    3. embed_batch: Generate embeddings for multiple texts efficiently
    4. get_embedding_dimension: Return the dimension of embeddings
    """
    
    def __init__(self) -> None:
        """Initialize the embedding service."""
        from ibm_watsonx_ai.foundation_models import Embeddings
        
        logger.info(
            "Initializing embedding service",
            model=settings.embedding_model
        )
        
        try:
            # Set up credentials
            credentials = {
                "url": settings.ibm_watsonx_url,
                "apikey": settings.ibm_cloud_api_key
            }
            
            # Initialize the Embeddings model
            self.embeddings = Embeddings(
                model_id=settings.embedding_model,
                credentials=credentials,
                project_id=settings.ibm_watsonx_project_id
            )
            
            logger.info("Embedding service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize embedding service", error=str(e))
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Attempted to embed empty text")
            return [0.0] * settings.vector_dimension
        
        logger.debug("Generating embedding", text_length=len(text))
        
        try:
            # Generate embedding using watsonx.ai
            response = self.embeddings.embed_query(text)
            
            # Extract embedding vector from response
            # The response structure may vary, adjust based on actual API response
            if isinstance(response, list):
                embedding = response
            elif isinstance(response, dict) and "results" in response:
                embedding = response["results"][0]["embedding"]
            else:
                embedding = response
            
            # Validate dimension
            if len(embedding) != settings.vector_dimension:
                logger.warning(
                    "Embedding dimension mismatch",
                    expected=settings.vector_dimension,
                    actual=len(embedding)
                )
            
            logger.debug("Embedding generated successfully", dimension=len(embedding))
            return embedding
            
        except Exception as e:
            logger.error("Failed to generate embedding", error=str(e))
            # Return zero vector as fallback
            return [0.0] * settings.vector_dimension
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        logger.info("Generating batch embeddings", batch_size=len(texts))
        
        if not texts:
            return []
        
        try:
            # Try to use batch embedding API if available
            try:
                response = self.embeddings.embed_documents(texts)
                
                # Extract embeddings from response
                if isinstance(response, list):
                    embeddings = response
                elif isinstance(response, dict) and "results" in response:
                    embeddings = [r["embedding"] for r in response["results"]]
                else:
                    # Fallback to individual calls
                    raise AttributeError("Batch API not available")
                
                logger.info("Batch embeddings generated", count=len(embeddings))
                return embeddings
                
            except (AttributeError, KeyError):
                # Batch API not available, use individual calls
                logger.debug("Batch API not available, using individual calls")
                embeddings = []
                
                for i, text in enumerate(texts):
                    if i % 10 == 0:
                        logger.debug(f"Processing embedding {i+1}/{len(texts)}")
                    
                    embedding = self.embed_text(text)
                    embeddings.append(embedding)
                
                logger.info("Batch embeddings generated", count=len(embeddings))
                return embeddings
                
        except Exception as e:
            logger.error("Batch embedding failed", error=str(e))
            # Return zero vectors as fallback
            return [[0.0] * settings.vector_dimension for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension (e.g., 384 for Slate-125M)
            
        This is useful for:
        - Initializing vector stores with correct dimension
        - Validating embeddings
        - Debugging dimension mismatches
        """
        return settings.vector_dimension
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
            
        Note: Some embedding models have separate methods for
        queries vs documents. Check your model's documentation.
        For Slate, you might use the same method for both.
        """
        logger.debug("Generating query embedding", query=query)
        return self.embed_text(query)

# Made with Bob
