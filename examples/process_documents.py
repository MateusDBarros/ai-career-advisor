"""Example script demonstrating the document processing pipeline.

This script shows how to:
1. Convert PDFs to Markdown using Docling
2. Chunk documents with overlap
3. Generate embeddings
4. Store in Milvus vector database
5. Perform semantic search

Usage:
    python examples/process_documents.py --pdf path/to/document.pdf
    python examples/process_documents.py --directory path/to/pdfs --recursive
    python examples/process_documents.py --search "your query here"
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import get_logger
from src.knowledge.pipeline import DocumentProcessingPipeline
from src.knowledge.schema import DocumentType

logger = get_logger(__name__)


def process_single_pdf(pipeline: DocumentProcessingPipeline, pdf_path: str) -> None:
    """Process a single PDF file.
    
    Args:
        pipeline: Document processing pipeline
        pdf_path: Path to PDF file
    """
    print(f"\n{'='*60}")
    print(f"Processing PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        chunks = pipeline.process_pdf(
            pdf_path=pdf_path,
            doc_type=DocumentType.PERSONAL_NOTE
        )
        
        print(f"✓ Successfully processed PDF")
        print(f"  - Created {len(chunks)} chunks")
        print(f"  - Average chunk length: {sum(len(c.content) for c in chunks) // len(chunks)} characters")
        
        # Show first chunk as example
        if chunks:
            print(f"\n📄 First chunk preview:")
            print(f"  {chunks[0].content[:200]}...")
        
    except Exception as e:
        print(f"✗ Failed to process PDF: {e}")
        logger.error("PDF processing failed", error=str(e))


def process_directory(
    pipeline: DocumentProcessingPipeline,
    directory: str,
    recursive: bool = False
) -> None:
    """Process all PDFs in a directory.
    
    Args:
        pipeline: Document processing pipeline
        directory: Path to directory
        recursive: Whether to search subdirectories
    """
    print(f"\n{'='*60}")
    print(f"Processing directory: {directory}")
    print(f"Recursive: {recursive}")
    print(f"{'='*60}\n")
    
    try:
        results = pipeline.process_pdf_directory(
            directory=directory,
            doc_type=DocumentType.PERSONAL_NOTE,
            recursive=recursive
        )
        
        print(f"✓ Successfully processed directory")
        print(f"  - Processed {len(results)} PDFs")
        
        total_chunks = sum(len(chunks) for chunks in results.values())
        print(f"  - Created {total_chunks} total chunks")
        
        # Show summary for each file
        print(f"\n📊 Per-file summary:")
        for pdf_path, chunks in results.items():
            print(f"  - {Path(pdf_path).name}: {len(chunks)} chunks")
        
    except Exception as e:
        print(f"✗ Failed to process directory: {e}")
        logger.error("Directory processing failed", error=str(e))


def search_documents(pipeline: DocumentProcessingPipeline, query: str, top_k: int = 5) -> None:
    """Search for relevant document chunks.
    
    Args:
        pipeline: Document processing pipeline
        query: Search query
        top_k: Number of results to return
    """
    print(f"\n{'='*60}")
    print(f"Searching for: {query}")
    print(f"{'='*60}\n")
    
    try:
        results = pipeline.search(query=query, top_k=top_k)
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"Result {i} (score: {result.score:.4f})")
            print(f"  Source: {result.chunk.source}")
            print(f"  Type: {result.chunk.doc_type.value}")
            print(f"  Content: {result.chunk.content[:200]}...")
            print()
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        logger.error("Search failed", error=str(e))


def show_stats(pipeline: DocumentProcessingPipeline) -> None:
    """Show pipeline statistics.
    
    Args:
        pipeline: Document processing pipeline
    """
    print(f"\n{'='*60}")
    print("Pipeline Statistics")
    print(f"{'='*60}\n")
    
    stats = pipeline.get_stats()
    
    print(f"Collection: {stats.get('collection_name', 'N/A')}")
    print(f"Total chunks: {stats.get('total_chunks', 0)}")
    print(f"Vector dimension: {stats.get('dimension', 0)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Document processing pipeline example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single PDF
  python examples/process_documents.py --pdf document.pdf
  
  # Process all PDFs in a directory
  python examples/process_documents.py --directory ./data/raw
  
  # Process PDFs recursively
  python examples/process_documents.py --directory ./data/raw --recursive
  
  # Search for relevant chunks
  python examples/process_documents.py --search "machine learning"
  
  # Show statistics
  python examples/process_documents.py --stats
        """
    )
    
    parser.add_argument(
        "--pdf",
        type=str,
        help="Path to a single PDF file to process"
    )
    
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to directory containing PDFs"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively"
    )
    
    parser.add_argument(
        "--search",
        type=str,
        help="Search query"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of search results to return (default: 5)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show pipeline statistics"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Chunk size in tokens (default: 512)"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Chunk overlap in tokens (default: 50)"
    )
    
    parser.add_argument(
        "--milvus-host",
        type=str,
        default="localhost",
        help="Milvus server host (default: localhost)"
    )
    
    parser.add_argument(
        "--milvus-port",
        type=int,
        default=19530,
        help="Milvus server port (default: 19530)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.pdf, args.directory, args.search, args.stats]):
        parser.print_help()
        sys.exit(1)
    
    # Initialize pipeline
    print("\n🚀 Initializing document processing pipeline...")
    
    try:
        pipeline = DocumentProcessingPipeline(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            milvus_host=args.milvus_host,
            milvus_port=args.milvus_port
        )
        
        print("✓ Pipeline initialized successfully\n")
        
        # Execute requested operation
        if args.pdf:
            process_single_pdf(pipeline, args.pdf)
        
        if args.directory:
            process_directory(pipeline, args.directory, args.recursive)
        
        if args.search:
            search_documents(pipeline, args.search, args.top_k)
        
        if args.stats:
            show_stats(pipeline)
        
        # Cleanup
        pipeline.close()
        print("\n✓ Pipeline closed successfully")
        
    except Exception as e:
        print(f"\n✗ Pipeline initialization failed: {e}")
        logger.error("Pipeline initialization failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
