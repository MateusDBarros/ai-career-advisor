# Implementation Roadmap

This document provides a detailed, step-by-step guide for implementing each component of the AI Career Advisor. Follow this roadmap to build the system methodically.

## Overview

The project is structured in 4 phases, each building on the previous one. Each phase should take approximately 1 week of part-time work.

---

## Phase 1: Core Infrastructure (Week 1)

### Goal
Set up the foundation: configuration, logging, and LLM integration.

### Tasks

#### 1.1 Complete Core Configuration
**File:** `src/core/logging.py`

**What to implement:**
- The `configure_logging()` function
- Test that logs appear correctly in console

**How to test:**
```python
from src.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

logger.info("Testing logging", test_value=123)
logger.error("Testing error", error="sample error")
```

**Expected output:** Colored, structured logs in development mode

---

#### 1.2 Implement Granite LLM Client
**File:** `src/llm/client.py`

**What to implement:**
1. `__init__`: Initialize watsonx.ai Model
2. `generate`: Send prompts and get responses
3. `generate_with_context`: RAG-aware generation
4. `_format_prompt`: Combine system prompt + context + query

**Key IBM SDK code:**
```python
from ibm_watsonx_ai.foundation_models import Model

credentials = {
    "url": settings.ibm_watsonx_url,
    "apikey": settings.ibm_cloud_api_key
}

self.model = Model(
    model_id=settings.llm_model,
    credentials=credentials,
    project_id=settings.ibm_watsonx_project_id
)

# Generate
response = self.model.generate(
    prompt=prompt,
    params={
        "max_new_tokens": max_tokens,
        "temperature": temperature,
        "decoding_method": "sample"
    }
)

text = response["results"][0]["generated_text"]
```

**How to test:**
```python
from src.llm.client import GraniteLLMClient

client = GraniteLLMClient()
response = client.generate("What are the key skills for a backend engineer?")
print(response)
```

---

#### 1.3 Implement Embedding Service
**File:** `src/llm/embeddings.py`

**What to implement:**
1. `__init__`: Initialize Embeddings model
2. `embed_text`: Generate single embedding
3. `embed_batch`: Generate multiple embeddings efficiently

**Key IBM SDK code:**
```python
from ibm_watsonx_ai.foundation_models import Embeddings

self.embeddings = Embeddings(
    model_id=settings.embedding_model,
    credentials=credentials,
    project_id=settings.ibm_watsonx_project_id
)

# Embed single text
result = self.embeddings.embed_query(text)
embedding = result["results"][0]["embedding"]

# Embed multiple texts
results = self.embeddings.embed_documents(texts)
embeddings = [r["embedding"] for r in results["results"]]
```

**How to test:**
```python
from src.llm.embeddings import EmbeddingService

service = EmbeddingService()
embedding = service.embed_text("Python backend development")
print(f"Dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

---

## Phase 2: Knowledge Base (Week 2)

### Goal
Load, process, and chunk documents for the knowledge base.

### Tasks

#### 2.1 Implement Document Loader
**File:** `src/knowledge/document_loader.py`

**What to implement:**
1. `load_document`: Main loading function
2. `_load_pdf`: Extract text from PDFs
3. `_load_text`: Load plain text files
4. `_load_markdown`: Load markdown files
5. `_infer_document_type`: Auto-detect document type

**Key libraries:**
```python
# PDF
from pypdf import PdfReader
reader = PdfReader(path)
text = "\n\n".join([page.extract_text() for page in reader.pages])

# Text
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Markdown (keep as-is or convert)
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()
```

**How to test:**
```python
from src.knowledge.document_loader import DocumentLoader
from src.knowledge.schema import DocumentType

loader = DocumentLoader()

# Load your CV
cv = loader.load_document(
    "data/raw/cv.pdf",
    doc_type=DocumentType.CV,
    title="My CV"
)

print(f"Loaded: {cv.title}")
print(f"Type: {cv.doc_type}")
print(f"Length: {len(cv.content)} characters")
print(f"Preview: {cv.content[:200]}...")
```

---

#### 2.2 Implement Document Chunker
**File:** `src/knowledge/chunker.py`

**What to implement:**
1. `chunk_document`: Main chunking function
2. `_chunk_by_tokens`: Token-based chunking with overlap
3. `_chunk_by_paragraphs`: Paragraph-based chunking

**Chunking strategy:**
```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
tokens = encoding.encode(text)

chunks = []
start = 0
while start < len(tokens):
    end = start + self.chunk_size
    chunk_tokens = tokens[start:end]
    chunk_text = encoding.decode(chunk_tokens)
    chunks.append(chunk_text)
    start = end - self.chunk_overlap  # Overlap for context

return chunks
```

**How to test:**
```python
from src.knowledge.chunker import DocumentChunker

chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
chunks = chunker.chunk_document(cv)

print(f"Created {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i} ---")
    print(chunk.content[:200] + "...")
```

---

#### 2.3 Set Up Vector Store
**File:** `src/retrieval/vector_store.py` (create this)

**What to implement:**
1. Choose FAISS (easiest) or Milvus (your experience)
2. Create VectorStore class with:
   - `add_chunks`: Store chunks with embeddings
   - `search`: Find similar chunks
   - `delete`: Remove chunks
   - `save/load`: Persist to disk

**FAISS implementation:**
```python
import faiss
import numpy as np
import pickle
from pathlib import Path

class FAISSVectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []  # Store chunk metadata
    
    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        # Convert to numpy array
        vectors = np.array(embeddings, dtype='float32')
        
        # Add to FAISS index
        self.index.add(vectors)
        
        # Store chunk metadata
        self.chunks.extend(chunks)
    
    def search(self, query_embedding: List[float], top_k: int = 5):
        # Convert query to numpy
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        # Return chunks with scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                score = 1 / (1 + distances[0][i])  # Convert distance to similarity
                results.append({
                    "chunk": self.chunks[idx],
                    "score": score
                })
        
        return results
    
    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.chunks", 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load(self, path: str):
        self.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.chunks", 'rb') as f:
            self.chunks = pickle.load(f)
```

**How to test:**
```python
from src.retrieval.vector_store import FAISSVectorStore
from src.llm.embeddings import EmbeddingService

# Create store
store = FAISSVectorStore(dimension=384)  # Adjust for your model

# Generate embeddings
embedding_service = EmbeddingService()
embeddings = embedding_service.embed_batch([c.content for c in chunks])

# Add to store
for chunk, embedding in zip(chunks, embeddings):
    chunk.embedding = embedding

store.add_chunks(chunks, embeddings)

# Search
query = "What backend technologies do I know?"
query_embedding = embedding_service.embed_query(query)
results = store.search(query_embedding, top_k=3)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['chunk'].content[:200]}...")
    print()
```

---

## Phase 3: RAG Pipeline (Week 3)

### Goal
Connect all components into a working RAG system with CLI.

### Tasks

#### 3.1 Implement Retriever
**File:** `src/retrieval/retriever.py` (create this)

**What to implement:**
```python
class Retriever:
    def __init__(self, vector_store, embedding_service):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve(self, query: str, top_k: int = 5):
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k)
        
        # Filter by threshold
        filtered = [
            r for r in results 
            if r['score'] >= settings.similarity_threshold
        ]
        
        return filtered
```

---

#### 3.2 Build CLI Interface
**File:** `src/cli/main.py` (create this)

**What to implement:**
```python
import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer()
console = Console()

@app.command()
def ask(question: str):
    """Ask the career advisor a question."""
    console.print(f"[bold blue]Question:[/bold blue] {question}")
    
    # Retrieve context
    retriever = Retriever(vector_store, embedding_service)
    contexts = retriever.retrieve(question)
    
    # Generate response
    llm_client = GraniteLLMClient()
    response = llm_client.generate_with_context(question, contexts)
    
    # Display
    console.print("\n[bold green]Answer:[/bold green]")
    console.print(Markdown(response))

@app.command()
def load(file_path: str):
    """Load a document into the knowledge base."""
    # Load, chunk, embed, store
    pass

@app.command()
def stats():
    """Show knowledge base statistics."""
    pass

if __name__ == "__main__":
    app()
```

---

## Phase 4: Advanced Features (Week 4+)

### 4.1 Conversation Memory
- Store chat history
- Include recent messages in context
- Implement conversation summarization

### 4.2 Evaluation Suite
- Create test questions with expected answers
- Measure response quality
- Track metrics over time

### 4.3 Web Search Integration
- Add Serper API or similar
- Fetch live job market data
- Combine with knowledge base

### 4.4 FastAPI Backend
- Create REST endpoints
- Add authentication
- Enable web UI integration

### 4.5 Web UI
- React/Next.js frontend
- Chat interface
- Document management

---

## Testing Strategy

### Unit Tests
Test each component independently:
```python
# tests/test_embeddings.py
def test_embed_text():
    service = EmbeddingService()
    embedding = service.embed_text("test")
    assert len(embedding) == settings.vector_dimension

# tests/test_chunker.py
def test_chunk_document():
    chunker = DocumentChunker()
    doc = Document(...)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 0
```

### Integration Tests
Test the full pipeline:
```python
def test_rag_pipeline():
    # Load document
    # Chunk it
    # Embed chunks
    # Store in vector store
    # Query
    # Generate response
    # Assert response quality
```

---

## Tips for Success

1. **Start Simple**: Get basic functionality working before adding complexity
2. **Test Incrementally**: Test each component before moving to the next
3. **Use Logging**: Add structured logs everywhere for debugging
4. **Iterate on Prompts**: Experiment with different system prompts
5. **Measure Quality**: Create evaluation datasets early
6. **Document Learnings**: Keep notes on what works and what doesn't

---

## Common Pitfalls to Avoid

1. **Chunk Size**: Too small = loss of context, too large = irrelevant info
2. **Overlap**: Too little = context loss, too much = redundancy
3. **Embedding Model**: Ensure it matches your use case (retrieval vs. similarity)
4. **Prompt Engineering**: Generic prompts = generic answers
5. **Error Handling**: Always handle API failures gracefully

---

## Next Steps After Completion

1. Deploy to IBM Cloud
2. Add monitoring and observability
3. Collect user feedback
4. Iterate on prompts and chunking
5. Expand knowledge base
6. Add more features (web search, memory, etc.)

Good luck! Remember: build incrementally, test thoroughly, and iterate based on results. 🚀