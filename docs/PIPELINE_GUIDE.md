# Document Processing Pipeline Guide

This guide explains the complete document processing pipeline from PDF to vector embeddings.

## Overview

The pipeline consists of four main stages:

```
PDF → Markdown → Chunks → Embeddings → Vector Store
```

1. **PDF to Markdown**: Convert PDFs to structured Markdown using Docling
2. **Chunking**: Split documents into overlapping chunks for optimal retrieval
3. **Embedding**: Generate vector embeddings using IBM watsonx.ai
4. **Storage**: Store embeddings in Milvus vector database

## Components

### 1. PDF to Markdown Converter (`src/knowledge/pdf_converter.py`)

Uses Docling to convert PDFs to Markdown with structure preservation.

**Features:**
- High-quality text extraction
- Layout analysis
- Structure preservation (headers, lists, tables)
- Batch processing support

**Usage:**
```python
from src.knowledge.pdf_converter import PDFToMarkdownConverter

converter = PDFToMarkdownConverter()

# Convert single PDF
markdown = converter.convert_pdf_to_markdown("document.pdf")

# Convert directory
results = converter.convert_pdf_directory("./pdfs", recursive=True)
```

### 2. Document Chunker (`src/knowledge/chunker.py`)

Splits documents into chunks with configurable size and overlap.

**Features:**
- Token-based chunking using tiktoken
- Configurable chunk size and overlap
- Multiple chunking strategies (token, sentence, paragraph, section)
- Automatic strategy selection based on document type

**Configuration:**
```python
from src.knowledge.chunker import DocumentChunker

chunker = DocumentChunker(
    chunk_size=512,      # Target size in tokens
    chunk_overlap=50     # Overlap between chunks
)

chunks = chunker.chunk_document(document)
```

**Why Overlap?**
Overlap ensures context continuity across chunk boundaries. For example:
- Chunk 1: tokens 0-512
- Chunk 2: tokens 462-974 (overlaps last 50 tokens of chunk 1)
- Chunk 3: tokens 924-1436

### 3. Embedding Service (`src/llm/embeddings.py`)

Generates vector embeddings using IBM watsonx.ai models.

**Features:**
- Single and batch embedding generation
- Automatic fallback handling
- Dimension validation
- Query-specific embeddings

**Usage:**
```python
from src.llm.embeddings import EmbeddingService

service = EmbeddingService()

# Single embedding
embedding = service.embed_text("Your text here")

# Batch embeddings (more efficient)
embeddings = service.embed_batch(["text1", "text2", "text3"])

# Query embedding
query_embedding = service.embed_query("search query")
```

### 4. Milvus Vector Store (`src/retrieval/vector_store.py`)

Stores and retrieves embeddings using Milvus.

**Features:**
- Automatic collection creation
- COSINE similarity search
- Metadata filtering
- Batch insertion
- Collection statistics

**Schema:**
- `id`: Chunk UUID (primary key)
- `document_id`: Parent document UUID
- `content`: Chunk text content
- `chunk_index`: Position in document
- `doc_type`: Document type
- `source`: Source file path
- `embedding`: Vector embedding (384 dimensions for Slate)

**Usage:**
```python
from src.retrieval.vector_store import MilvusVectorStore

store = MilvusVectorStore(
    collection_name="document_chunks",
    host="localhost",
    port=19530
)

# Insert chunks
store.insert_chunks(chunks)

# Search
results = store.search(
    query_embedding=embedding,
    top_k=5,
    doc_type_filter="cv"
)

# Get stats
stats = store.get_collection_stats()
```

### 5. Pipeline Orchestrator (`src/knowledge/pipeline.py`)

Orchestrates the complete pipeline end-to-end.

**Features:**
- Single PDF processing
- Directory batch processing
- Markdown file processing
- Semantic search
- Automatic error handling

**Usage:**
```python
from src.knowledge.pipeline import DocumentProcessingPipeline
from src.knowledge.schema import DocumentType

# Initialize pipeline
pipeline = DocumentProcessingPipeline(
    chunk_size=512,
    chunk_overlap=50,
    milvus_host="localhost",
    milvus_port=19530
)

# Process a PDF
chunks = pipeline.process_pdf(
    pdf_path="document.pdf",
    doc_type=DocumentType.CV
)

# Process directory
results = pipeline.process_pdf_directory(
    directory="./pdfs",
    recursive=True
)

# Search
results = pipeline.search(
    query="machine learning experience",
    top_k=5
)

# Cleanup
pipeline.close()
```

## Example Script

The `examples/process_documents.py` script demonstrates the complete pipeline:

### Process a Single PDF
```bash
python examples/process_documents.py --pdf document.pdf
```

### Process a Directory
```bash
# Non-recursive
python examples/process_documents.py --directory ./data/raw

# Recursive
python examples/process_documents.py --directory ./data/raw --recursive
```

### Search Documents
```bash
python examples/process_documents.py --search "machine learning"
```

### Show Statistics
```bash
python examples/process_documents.py --stats
```

### Custom Configuration
```bash
python examples/process_documents.py \
  --pdf document.pdf \
  --chunk-size 1024 \
  --chunk-overlap 100 \
  --milvus-host localhost \
  --milvus-port 19530
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# IBM watsonx.ai
IBM_CLOUD_API_KEY=your_api_key
IBM_WATSONX_PROJECT_ID=your_project_id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Models
EMBEDDING_MODEL=ibm/slate-125m-english-rtrvr
VECTOR_DIMENSION=384

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Milvus Setup

#### Using Docker
```bash
# Start Milvus standalone
docker-compose up -d

# Or use docker run
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest \
  milvus run standalone
```

#### Using Milvus Lite (for development)
```bash
pip install milvus
```

## Best Practices

### Chunk Size Selection

- **Small chunks (256-512 tokens)**: Better for precise retrieval, more chunks
- **Medium chunks (512-1024 tokens)**: Balanced approach (recommended)
- **Large chunks (1024-2048 tokens)**: More context, fewer chunks

### Overlap Configuration

- **Small overlap (25-50 tokens)**: Minimal redundancy
- **Medium overlap (50-100 tokens)**: Recommended for most cases
- **Large overlap (100-200 tokens)**: Maximum context preservation

### Document Types

Choose appropriate document types for better organization:

- `DocumentType.CV`: Resumes and CVs
- `DocumentType.JOB_DESCRIPTION`: Job postings
- `DocumentType.CAREER_GUIDE`: Career development resources
- `DocumentType.PERSONAL_NOTE`: Personal notes and goals
- `DocumentType.TECH_ARTICLE`: Technical articles
- `DocumentType.COURSE_MATERIAL`: Learning resources

## Performance Tips

1. **Batch Processing**: Use `embed_batch()` instead of individual `embed_text()` calls
2. **Milvus Indexing**: Use appropriate index type (IVF_FLAT for <1M vectors)
3. **Chunk Size**: Balance between context and retrieval precision
4. **Connection Pooling**: Reuse pipeline instances when processing multiple files

## Troubleshooting

### Docling Installation Issues
```bash
# Install with all dependencies
pip install docling[all]
```

### Milvus Connection Errors
```bash
# Check if Milvus is running
docker ps | grep milvus

# Check logs
docker logs milvus-standalone
```

### Embedding Dimension Mismatch
Ensure `VECTOR_DIMENSION` in `.env` matches your embedding model:
- Slate-125M: 384 dimensions
- Slate-30M: 384 dimensions

### Memory Issues with Large PDFs
- Reduce chunk size
- Process files individually instead of batch
- Increase system memory allocation

## Architecture Diagram

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Docling Converter  │  ← Convert to Markdown
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Document Object    │  ← Create Document
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Document Chunker   │  ← Split into chunks
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Embedding Service   │  ← Generate embeddings
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Milvus Vector DB   │  ← Store & retrieve
└─────────────────────┘
```

## Next Steps

1. Process your documents using the example script
2. Experiment with different chunk sizes and overlaps
3. Integrate the pipeline into your application
4. Set up monitoring and logging
5. Optimize for your specific use case

## References

- [Docling Documentation](https://github.com/DS4SD/docling)
- [Milvus Documentation](https://milvus.io/docs)
- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [tiktoken Documentation](https://github.com/openai/tiktoken)