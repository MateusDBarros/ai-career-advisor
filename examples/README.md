# Examples

This directory contains example scripts demonstrating how to use the document processing pipeline.

## Quick Start

### 1. Install Dependencies

```bash
cd ai-career-advisor
poetry install
```

### 2. Set Up Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
IBM_CLOUD_API_KEY=your_api_key
IBM_WATSONX_PROJECT_ID=your_project_id
```

### 3. Start Milvus

Using Docker:
```bash
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest \
  milvus run standalone
```

### 4. Run Examples

#### Process a Single PDF
```bash
python examples/process_documents.py --pdf ../025962631-EN-GB-4.pdf
```

#### Process Multiple PDFs
```bash
python examples/process_documents.py --directory ../data/raw --recursive
```

#### Search Documents
```bash
python examples/process_documents.py --search "machine learning"
```

#### View Statistics
```bash
python examples/process_documents.py --stats
```

## Available Scripts

### `process_documents.py`

Complete document processing pipeline demonstration.

**Features:**
- PDF to Markdown conversion using Docling
- Document chunking with overlap
- Embedding generation with IBM watsonx.ai
- Vector storage in Milvus
- Semantic search

**Options:**
```
--pdf PATH              Process a single PDF file
--directory PATH        Process all PDFs in directory
--recursive             Search subdirectories
--search QUERY          Search for relevant chunks
--top-k N               Number of search results (default: 5)
--stats                 Show pipeline statistics
--chunk-size N          Chunk size in tokens (default: 512)
--chunk-overlap N       Chunk overlap in tokens (default: 50)
--milvus-host HOST      Milvus server host (default: localhost)
--milvus-port PORT      Milvus server port (default: 19530)
```

## Example Workflows

### Workflow 1: Process and Search

```bash
# 1. Process documents
python examples/process_documents.py --directory ./data/raw --recursive

# 2. Search for relevant content
python examples/process_documents.py --search "python programming"

# 3. Check statistics
python examples/process_documents.py --stats
```

### Workflow 2: Custom Configuration

```bash
# Process with larger chunks and more overlap
python examples/process_documents.py \
  --pdf document.pdf \
  --chunk-size 1024 \
  --chunk-overlap 100
```

### Workflow 3: Batch Processing

```bash
# Process all PDFs in multiple directories
python examples/process_documents.py --directory ./data/cvs
python examples/process_documents.py --directory ./data/guides
python examples/process_documents.py --directory ./data/articles
```

## Output Examples

### Processing Output
```
🚀 Initializing document processing pipeline...
✓ Pipeline initialized successfully

============================================================
Processing PDF: document.pdf
============================================================

✓ Successfully processed PDF
  - Created 15 chunks
  - Average chunk length: 450 characters

📄 First chunk preview:
  This document contains information about...
```

### Search Output
```
============================================================
Searching for: machine learning
============================================================

Found 5 results:

Result 1 (score: 0.8542)
  Source: data/raw/ml_guide.pdf
  Type: career_guide
  Content: Machine learning is a subset of artificial intelligence...

Result 2 (score: 0.7891)
  Source: data/raw/cv.pdf
  Type: cv
  Content: Experience with machine learning frameworks including...
```

### Statistics Output
```
============================================================
Pipeline Statistics
============================================================

Collection: document_chunks
Total chunks: 247
Vector dimension: 384
```

## Troubleshooting

### Issue: "Failed to connect to Milvus"
**Solution:** Ensure Milvus is running:
```bash
docker ps | grep milvus
```

### Issue: "IBM API authentication failed"
**Solution:** Check your `.env` file has correct credentials:
```bash
cat .env | grep IBM_CLOUD_API_KEY
```

### Issue: "Docling import error"
**Solution:** Install with all dependencies:
```bash
poetry add docling
```

### Issue: "Out of memory"
**Solution:** Process files individually or reduce chunk size:
```bash
python examples/process_documents.py --pdf file.pdf --chunk-size 256
```

## Next Steps

1. Review the [Pipeline Guide](../docs/PIPELINE_GUIDE.md) for detailed documentation
2. Customize the pipeline for your use case
3. Integrate into your application
4. Set up monitoring and logging

## Additional Resources

- [Docling Documentation](https://github.com/DS4SD/docling)
- [Milvus Documentation](https://milvus.io/docs)
- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)