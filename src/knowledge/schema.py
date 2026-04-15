"""Data models for knowledge base documents and chunks.

This module defines the structure of documents in the knowledge base.
Using Pydantic models ensures type safety and validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of documents in the knowledge base.
    
    Each type may be processed differently and have different
    metadata requirements.
    """
    
    CV = "cv"  # Your CV/resume
    CAREER_GUIDE = "career_guide"  # Career development resources
    JOB_DESCRIPTION = "job_description"  # Target job postings
    PERSONAL_NOTE = "personal_note"  # Your goals, reflections, notes
    TECH_ARTICLE = "tech_article"  # Technical articles/blog posts
    COURSE_MATERIAL = "course_material"  # Learning resources


class Document(BaseModel):
    """A document in the knowledge base.
    
    Represents a complete document before chunking.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Unique document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full document content")
    doc_type: DocumentType = Field(..., description="Type of document")
    source: str = Field(..., description="Source file path or URL")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class DocumentChunk(BaseModel):
    """A chunk of a document for vector storage.
    
    Documents are split into chunks for more precise retrieval.
    Each chunk is embedded and stored in the vector database.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Unique chunk ID")
    document_id: UUID = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Position in document")
    doc_type: DocumentType = Field(..., description="Type of parent document")
    source: str = Field(..., description="Source file path or URL")
    
    # Metadata for better retrieval
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk-specific metadata"
    )
    
    # Embedding (populated after generation)
    embedding: Optional[list[float]] = Field(
        default=None,
        description="Vector embedding of the chunk"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "content": self.content,
            "chunk_index": self.chunk_index,
            "doc_type": self.doc_type.value,
            "source": self.source,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
        }


class SearchResult(BaseModel):
    """A search result from the vector store.
    
    Represents a chunk retrieved by similarity search.
    """
    
    chunk: DocumentChunk = Field(..., description="Retrieved chunk")
    score: float = Field(..., description="Similarity score (0-1)")
    
    def to_context_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM context.
        
        Returns:
            Dictionary with relevant fields for context
        """

        return {
            "content": self.chunk.content,
            "source": self.chunk.source,
            "doc_type": self.chunk.doc_type.value,
            "score": self.score,
            "metadata": self.chunk.metadata,
        }