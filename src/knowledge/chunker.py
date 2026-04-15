"""Document chunking strategies for optimal retrieval.

Chunking is critical for RAG systems. The goal is to split documents
into pieces that are:
1. Small enough to fit in context windows
2. Large enough to contain meaningful information
3. Semantically coherent (don't split mid-sentence or mid-thought)

Different strategies work better for different content types.
"""

from typing import List
from uuid import uuid4

from src.core.config import settings
from src.core.logging import get_logger
from .schema import Document, DocumentChunk

logger = get_logger(__name__)


class DocumentChunker:
    """Split documents into chunks for vector storage.
    
    This class implements various chunking strategies to optimize
    retrieval quality. The right strategy depends on document type
    and content structure.
    
    TODO: Implement the following methods:
    1. chunk_document: Main entry point
    2. _chunk_by_tokens: Token-based chunking with overlap
    3. _chunk_by_sentences: Sentence-based chunking
    4. _chunk_by_paragraphs: Paragraph-based chunking
    5. _chunk_by_sections: Section-based chunking (for structured docs)
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ) -> None:
        """Initialize the chunker.
        
        Args:
            chunk_size: Target size of each chunk (in tokens)
            chunk_overlap: Number of tokens to overlap between chunks
            
        Overlap helps maintain context across chunk boundaries.
        For example, with chunk_size=512 and overlap=50:
        - Chunk 1: tokens 0-512
        - Chunk 2: tokens 462-974 (overlaps last 50 tokens of chunk 1)
        - Chunk 3: tokens 924-1436
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(
            "Initializing chunker",
            chunk_size=chunk_size,
            overlap=chunk_overlap
        )
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into chunks.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        from .schema import DocumentType
        
        logger.info(
            "Chunking document",
            doc_id=str(document.id),
            doc_type=document.doc_type.value,
            content_length=len(document.content)
        )
        
        # Choose chunking strategy based on document type
        if document.doc_type == DocumentType.CV:
            # Paragraph-based for CVs to preserve sections
            chunks_text = self._chunk_by_paragraphs(document.content)
        elif document.doc_type == DocumentType.CAREER_GUIDE:
            # Section-based for structured guides
            chunks_text = self._chunk_by_sections(document.content)
        elif document.doc_type == DocumentType.JOB_DESCRIPTION:
            # Paragraph-based for job descriptions
            chunks_text = self._chunk_by_paragraphs(document.content)
        else:
            # Token-based for other content types
            chunks_text = self._chunk_by_tokens(document.content)
        
        # Create DocumentChunk objects
        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=i,
                doc_type=document.doc_type,
                source=document.source,
                metadata={
                    "total_chunks": len(chunks_text),
                    "document_title": document.title,
                    **document.metadata
                }
            )
            chunks.append(chunk)
        
        logger.info(
            "Document chunked successfully",
            doc_id=str(document.id),
            num_chunks=len(chunks),
            avg_chunk_length=sum(len(c.content) for c in chunks) // len(chunks) if chunks else 0
        )
        
        return chunks
    
    def _chunk_by_tokens(self, text: str) -> List[str]:
        """Chunk text by token count with overlap.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        import tiktoken
        
        if not text or not text.strip():
            return []
        
        try:
            # Use cl100k_base encoding (used by GPT-4 and similar models)
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text)
            
            # If text is shorter than chunk size, return as single chunk
            if len(tokens) <= self.chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(tokens):
                # Calculate end position
                end = min(start + self.chunk_size, len(tokens))
                
                # Extract chunk tokens
                chunk_tokens = tokens[start:end]
                
                # Decode back to text
                chunk_text = encoding.decode(chunk_tokens)
                
                # Add chunk if it has content
                if chunk_text.strip():
                    chunks.append(chunk_text)
                
                # Move start position with overlap
                # If we're at the end, break to avoid infinite loop
                if end >= len(tokens):
                    break
                    
                start = end - self.chunk_overlap
                
                # Ensure we're making progress
                if start <= 0:
                    start = end
            
            logger.debug(
                "Token-based chunking complete",
                total_tokens=len(tokens),
                num_chunks=len(chunks),
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap
            )
            
            return chunks if chunks else [text]
            
        except Exception as e:
            logger.error("Token chunking failed, falling back to character-based", error=str(e))
            # Fallback to character-based chunking
            chunk_chars = self.chunk_size * 4
            overlap_chars = self.chunk_overlap * 4
            
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_chars
                chunks.append(text[start:end])
                start = end - overlap_chars
                if start >= len(text):
                    break
            
            return chunks if chunks else [text]
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk text by sentences, respecting chunk_size.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
            
        Steps to implement:
        1. Split text into sentences (use regex or nltk)
        2. Group sentences into chunks up to chunk_size tokens
        3. Add overlap by including last few sentences of previous chunk
        4. Preserve sentence boundaries (don't split mid-sentence)
        
        This is good for content where sentence boundaries are important.
        
        Example:
            import re
            
            # Simple sentence splitter (improve with nltk for better accuracy)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            chunks = []
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence_size = len(sentence.split())  # Rough token count
                
                if current_size + sentence_size > self.chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    # Keep last sentence for overlap
                    current_chunk = [current_chunk[-1], sentence]
                    current_size = len(current_chunk[-1].split()) + sentence_size
                else:
                    current_chunk.append(sentence)
                    current_size += sentence_size
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            return chunks
        """
        # TODO: Implement sentence-based chunking
        return self._chunk_by_tokens(text)
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunk text by paragraphs, respecting chunk_size.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
            
        Steps to implement:
        1. Split text by double newlines (paragraphs)
        2. Group paragraphs into chunks up to chunk_size
        3. Keep paragraph boundaries intact when possible
        4. If a single paragraph exceeds chunk_size, split it
        
        This is ideal for CVs and structured documents where
        paragraphs represent logical sections.
        
        Example:
            paragraphs = text.split("\n\n")
            
            chunks = []
            current_chunk = []
            current_size = 0
            
            for para in paragraphs:
                para_size = len(para.split())
                
                if current_size + para_size > self.chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [para]
                    current_size = para_size
                else:
                    current_chunk.append(para)
                    current_size += para_size
            
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            
            return chunks
        """
        # TODO: Implement paragraph-based chunking
        return self._chunk_by_tokens(text)
    
    def _chunk_by_sections(self, text: str) -> List[str]:
        """Chunk text by sections (headers).
        
        Args:
            text: Text to chunk (markdown or structured)
            
        Returns:
            List of text chunks
            
        Steps to implement:
        1. Identify section headers (markdown # headers or other markers)
        2. Split text into sections
        3. Keep each section as a chunk if it fits
        4. If section is too large, sub-chunk it
        5. Preserve section hierarchy in metadata
        
        This is best for structured documents like career guides
        where sections have clear boundaries.
        
        Example for markdown:
            import re
            
            # Split by markdown headers
            sections = re.split(r'\n(#{1,6}\s+.+)\n', text)
            
            chunks = []
            current_section = []
            
            for i, part in enumerate(sections):
                if i % 2 == 1:  # Header
                    if current_section:
                        chunks.append("\n".join(current_section))
                    current_section = [part]
                else:  # Content
                    current_section.append(part)
            
            if current_section:
                chunks.append("\n".join(current_section))
            
            return chunks
        """
        # TODO: Implement section-based chunking
        return self._chunk_by_tokens(text)
