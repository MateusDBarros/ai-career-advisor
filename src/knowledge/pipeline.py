"""Document processing pipeline orchestrator.

This module orchestrates the complete pipeline from PDF to vector store:
1. PDF to Markdown conversion (using Docling)
2. Document chunking
3. Embedding generation
4. Vector store insertion
"""

from pathlib import Path
from typing import List, Optional

from src.core.config import settings
from src.core.logging import get_logger
from src.knowledge.chunker import DocumentChunker
from src.knowledge.pdf_converter import PDFToMarkdownConverter
from src.knowledge.schema import Document, DocumentChunk, DocumentType
from src.llm.embeddings import EmbeddingService
from src.retrieval.vector_store import MilvusVectorStore

logger = get_logger(__name__)


class DocumentProcessingPipeline:
    """Orchestrates the complete document processing pipeline.
    
    This pipeline handles:
    - PDF to Markdown conversion
    - Document chunking with overlap
    - Embedding generation
    - Vector store insertion
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        milvus_host: str = "localhost",
        milvus_port: int = 19530,
    ) -> None:
        """Initialize the pipeline.
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of tokens to overlap between chunks
            milvus_host: Milvus server host
            milvus_port: Milvus server port
        """
        logger.info(
            "Initializing document processing pipeline",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Initialize components
        self.pdf_converter = PDFToMarkdownConverter()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_service = EmbeddingService()
        self.vector_store = MilvusVectorStore(
            host=milvus_host,
            port=milvus_port
        )
        
        logger.info("Pipeline initialized successfully")
    
    def process_pdf(
        self,
        pdf_path: str,
        doc_type: DocumentType = DocumentType.PERSONAL_NOTE,
        title: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """Process a single PDF through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            doc_type: Type of document
            title: Optional document title (uses filename if None)
            
        Returns:
            List of processed DocumentChunk objects with embeddings
        """
        logger.info("Processing PDF", pdf_path=pdf_path, doc_type=doc_type.value)
        
        try:
            # Step 1: Convert PDF to Markdown
            logger.info("Step 1: Converting PDF to Markdown")
            markdown_content = self.pdf_converter.convert_pdf_to_markdown(pdf_path)
            
            # Step 2: Create Document object
            pdf_file = Path(pdf_path)
            document = Document(
                title=title or pdf_file.stem,
                content=markdown_content,
                doc_type=doc_type,
                source=str(pdf_path)
            )
            
            logger.info(
                "Document created",
                doc_id=str(document.id),
                content_length=len(markdown_content)
            )
            
            # Step 3: Chunk the document
            logger.info("Step 2: Chunking document")
            chunks = self.chunker.chunk_document(document)
            
            logger.info("Document chunked", num_chunks=len(chunks))
            
            # Step 4: Generate embeddings for chunks
            logger.info("Step 3: Generating embeddings")
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_batch(chunk_texts)
            
            # Attach embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            
            logger.info("Embeddings generated", count=len(embeddings))
            
            # Step 5: Insert into vector store
            logger.info("Step 4: Inserting into vector store")
            self.vector_store.insert_chunks(chunks)
            
            logger.info(
                "PDF processing complete",
                pdf_path=pdf_path,
                chunks_created=len(chunks)
            )
            
            return chunks
            
        except Exception as e:
            logger.error("PDF processing failed", pdf_path=pdf_path, error=str(e))
            raise
    
    def process_pdf_directory(
        self,
        directory: str,
        doc_type: DocumentType = DocumentType.PERSONAL_NOTE,
        recursive: bool = False,
    ) -> dict[str, List[DocumentChunk]]:
        """Process all PDFs in a directory.
        
        Args:
            directory: Path to directory containing PDFs
            doc_type: Type for all documents
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary mapping PDF paths to their chunks
        """
        logger.info(
            "Processing PDF directory",
            directory=directory,
            recursive=recursive
        )
        
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all PDF files
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(dir_path.glob(pattern))
        
        logger.info("Found PDF files", count=len(pdf_files))
        
        results = {}
        
        for pdf_file in pdf_files:
            try:
                chunks = self.process_pdf(
                    str(pdf_file),
                    doc_type=doc_type
                )
                results[str(pdf_file)] = chunks
                
            except Exception as e:
                logger.error(
                    "Failed to process PDF",
                    pdf_file=str(pdf_file),
                    error=str(e)
                )
                # Continue with other files
                continue
        
        logger.info(
            "Directory processing complete",
            total_files=len(pdf_files),
            successful=len(results)
        )
        
        return results
    
    def process_markdown(
        self,
        markdown_path: str,
        doc_type: DocumentType = DocumentType.PERSONAL_NOTE,
        title: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """Process a Markdown file through the pipeline.
        
        Args:
            markdown_path: Path to the Markdown file
            doc_type: Type of document
            title: Optional document title
            
        Returns:
            List of processed DocumentChunk objects with embeddings
        """
        logger.info("Processing Markdown", markdown_path=markdown_path)
        
        try:
            # Read Markdown content
            md_file = Path(markdown_path)
            
            if not md_file.exists():
                raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
            
            markdown_content = md_file.read_text(encoding='utf-8')
            
            # Create Document object
            document = Document(
                title=title or md_file.stem,
                content=markdown_content,
                doc_type=doc_type,
                source=str(markdown_path)
            )
            
            # Chunk the document
            chunks = self.chunker.chunk_document(document)
            
            # Generate embeddings
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_batch(chunk_texts)
            
            # Attach embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            
            # Insert into vector store
            self.vector_store.insert_chunks(chunks)
            
            logger.info(
                "Markdown processing complete",
                markdown_path=markdown_path,
                chunks_created=len(chunks)
            )
            
            return chunks
            
        except Exception as e:
            logger.error(
                "Markdown processing failed",
                markdown_path=markdown_path,
                error=str(e)
            )
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type_filter: Optional[str] = None,
    ) -> List:
        """Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            doc_type_filter: Optional filter by document type
            
        Returns:
            List of SearchResult objects
        """
        logger.info("Searching", query=query, top_k=top_k)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                doc_type_filter=doc_type_filter
            )
            
            logger.info("Search complete", results_found=len(results))
            return results
            
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []
    
    def get_stats(self) -> dict:
        """Get pipeline statistics.
        
        Returns:
            Dictionary with pipeline statistics
        """
        return self.vector_store.get_collection_stats()
    
    def close(self) -> None:
        """Close all connections."""
        logger.info("Closing pipeline connections")
        self.vector_store.close()

# Made with Bob
