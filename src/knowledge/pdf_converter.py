"""PDF to Markdown conversion using Docling.

This module uses Docling to convert PDF documents to Markdown format,
preserving structure and formatting for better chunking and retrieval.
"""

from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class PDFToMarkdownConverter:
    """Convert PDF documents to Markdown using Docling.
    
    Docling provides high-quality PDF to Markdown conversion with:
    - Structure preservation (headers, lists, tables)
    - Layout analysis
    - Text extraction with formatting
    """
    
    def __init__(self) -> None:
        """Initialize the PDF converter."""
        logger.info("Initializing PDF to Markdown converter")
        self.converter = DocumentConverter()
    
    def convert_pdf_to_markdown(
        self,
        pdf_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """Convert a PDF file to Markdown format.
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Optional path to save the Markdown file
            
        Returns:
            Markdown content as string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If conversion fails
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info("Converting PDF to Markdown", pdf_path=str(pdf_file))
        
        try:
            # Convert PDF using Docling
            result = self.converter.convert(str(pdf_file))
            
            # Extract Markdown content
            markdown_content = result.document.export_to_markdown()
            
            # Optionally save to file
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(markdown_content, encoding='utf-8')
                logger.info("Markdown saved", output_path=str(output_file))
            
            logger.info(
                "PDF conversion successful",
                pdf_path=str(pdf_file),
                markdown_length=len(markdown_content)
            )
            
            return markdown_content
            
        except Exception as e:
            logger.error(
                "PDF conversion failed",
                pdf_path=str(pdf_file),
                error=str(e)
            )
            raise ValueError(f"Failed to convert PDF: {e}") from e
    
    def convert_pdf_directory(
        self,
        directory: str,
        output_directory: Optional[str] = None,
        recursive: bool = False
    ) -> dict[str, str]:
        """Convert all PDF files in a directory to Markdown.
        
        Args:
            directory: Path to directory containing PDFs
            output_directory: Optional directory to save Markdown files
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary mapping PDF paths to Markdown content
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        logger.info(
            "Converting PDF directory",
            directory=str(dir_path),
            recursive=recursive
        )
        
        # Find all PDF files
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(dir_path.glob(pattern))
        
        logger.info("Found PDF files", count=len(pdf_files))
        
        results = {}
        
        for pdf_file in pdf_files:
            try:
                # Determine output path if output_directory is specified
                output_path = None
                if output_directory:
                    relative_path = pdf_file.relative_to(dir_path)
                    output_path = Path(output_directory) / relative_path.with_suffix('.md')
                
                # Convert PDF
                markdown_content = self.convert_pdf_to_markdown(
                    str(pdf_file),
                    str(output_path) if output_path else None
                )
                
                results[str(pdf_file)] = markdown_content
                
            except Exception as e:
                logger.error(
                    "Failed to convert PDF",
                    pdf_file=str(pdf_file),
                    error=str(e)
                )
                # Continue with other files
                continue
        
        logger.info(
            "Directory conversion complete",
            total_files=len(pdf_files),
            successful=len(results)
        )
        
        return results

# Made with Bob
