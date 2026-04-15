"""Milvus vector store for document embeddings.

This module provides integration with Milvus for storing and retrieving
document chunk embeddings using similarity search.
"""

from typing import List, Optional
from uuid import UUID

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from src.core.config import settings
from src.core.logging import get_logger
from src.knowledge.schema import DocumentChunk, SearchResult

logger = get_logger(__name__)


class MilvusVectorStore:
    """Vector store using Milvus for similarity search.
    
    Milvus is a high-performance vector database designed for
    similarity search and AI applications.
    """
    
    def __init__(
        self,
        collection_name: str = "document_chunks",
        host: str = "localhost",
        port: int = 19530,
    ) -> None:
        """Initialize Milvus vector store.
        
        Args:
            collection_name: Name of the Milvus collection
            host: Milvus server host
            port: Milvus server port
        """
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.collection: Optional[Collection] = None
        
        logger.info(
            "Initializing Milvus vector store",
            collection=collection_name,
            host=host,
            port=port
        )
        
        self._connect()
        self._create_collection()
    
    def _connect(self) -> None:
        """Connect to Milvus server."""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info("Connected to Milvus successfully")
        except Exception as e:
            logger.error("Failed to connect to Milvus", error=str(e))
            raise
    
    def _create_collection(self) -> None:
        """Create or load the Milvus collection."""
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                logger.info("Loading existing collection", name=self.collection_name)
                self.collection = Collection(self.collection_name)
            else:
                logger.info("Creating new collection", name=self.collection_name)
                
                # Define schema
                fields = [
                    FieldSchema(
                        name="id",
                        dtype=DataType.VARCHAR,
                        is_primary=True,
                        max_length=36,
                        description="Chunk UUID"
                    ),
                    FieldSchema(
                        name="document_id",
                        dtype=DataType.VARCHAR,
                        max_length=36,
                        description="Parent document UUID"
                    ),
                    FieldSchema(
                        name="content",
                        dtype=DataType.VARCHAR,
                        max_length=65535,
                        description="Chunk text content"
                    ),
                    FieldSchema(
                        name="chunk_index",
                        dtype=DataType.INT64,
                        description="Position in document"
                    ),
                    FieldSchema(
                        name="doc_type",
                        dtype=DataType.VARCHAR,
                        max_length=50,
                        description="Document type"
                    ),
                    FieldSchema(
                        name="source",
                        dtype=DataType.VARCHAR,
                        max_length=500,
                        description="Source file path"
                    ),
                    FieldSchema(
                        name="embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=settings.vector_dimension,
                        description="Embedding vector"
                    ),
                ]
                
                schema = CollectionSchema(
                    fields=fields,
                    description="Document chunks with embeddings"
                )
                
                # Create collection
                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema
                )
                
                # Create index for vector field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params
                )
                
                logger.info("Collection created successfully")
            
            # Load collection into memory
            self.collection.load()
            logger.info("Collection loaded into memory")
            
        except Exception as e:
            logger.error("Failed to create/load collection", error=str(e))
            raise
    
    def insert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Insert document chunks into the vector store.
        
        Args:
            chunks: List of DocumentChunk objects with embeddings
        """
        if not chunks:
            logger.warning("No chunks to insert")
            return
        
        logger.info("Inserting chunks", count=len(chunks))
        
        try:
            # Prepare data for insertion
            data = [
                [str(chunk.id) for chunk in chunks],  # id
                [str(chunk.document_id) for chunk in chunks],  # document_id
                [chunk.content for chunk in chunks],  # content
                [chunk.chunk_index for chunk in chunks],  # chunk_index
                [chunk.doc_type.value for chunk in chunks],  # doc_type
                [chunk.source for chunk in chunks],  # source
                [chunk.embedding for chunk in chunks],  # embedding
            ]
            
            # Insert data
            self.collection.insert(data)
            
            # Flush to ensure data is persisted
            self.collection.flush()
            
            logger.info("Chunks inserted successfully", count=len(chunks))
            
        except Exception as e:
            logger.error("Failed to insert chunks", error=str(e))
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_type_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            doc_type_filter: Optional filter by document type
            
        Returns:
            List of SearchResult objects
        """
        logger.info("Searching vector store", top_k=top_k, filter=doc_type_filter)
        
        try:
            # Prepare search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Build filter expression if needed
            expr = None
            if doc_type_filter:
                expr = f'doc_type == "{doc_type_filter}"'
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=[
                    "id",
                    "document_id",
                    "content",
                    "chunk_index",
                    "doc_type",
                    "source"
                ]
            )
            
            # Convert to SearchResult objects
            search_results = []
            
            for hits in results:
                for hit in hits:
                    # Reconstruct DocumentChunk
                    chunk = DocumentChunk(
                        id=UUID(hit.entity.get("id")),
                        document_id=UUID(hit.entity.get("document_id")),
                        content=hit.entity.get("content"),
                        chunk_index=hit.entity.get("chunk_index"),
                        doc_type=hit.entity.get("doc_type"),
                        source=hit.entity.get("source"),
                        metadata={}
                    )
                    
                    # Create SearchResult
                    search_result = SearchResult(
                        chunk=chunk,
                        score=float(hit.score)
                    )
                    
                    search_results.append(search_result)
            
            logger.info("Search completed", results_found=len(search_results))
            return search_results
            
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []
    
    def delete_by_document_id(self, document_id: UUID) -> None:
        """Delete all chunks belonging to a document.
        
        Args:
            document_id: Document UUID
        """
        logger.info("Deleting chunks by document_id", document_id=str(document_id))
        
        try:
            expr = f'document_id == "{str(document_id)}"'
            self.collection.delete(expr)
            self.collection.flush()
            
            logger.info("Chunks deleted successfully")
            
        except Exception as e:
            logger.error("Failed to delete chunks", error=str(e))
            raise
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = self.collection.num_entities
            
            return {
                "collection_name": self.collection_name,
                "total_chunks": stats,
                "dimension": settings.vector_dimension
            }
            
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {}
    
    def close(self) -> None:
        """Close the connection to Milvus."""
        try:
            if self.collection:
                self.collection.release()
            connections.disconnect("default")
            logger.info("Milvus connection closed")
        except Exception as e:
            logger.error("Failed to close connection", error=str(e))

# Made with Bob
