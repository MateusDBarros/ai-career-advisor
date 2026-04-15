# Setup Guide - AI Career Advisor

This guide will help you set up and start implementing the AI Career Advisor project.

## Prerequisites

- Python 3.10 or higher
- Poetry (recommended) or pip
- IBM Cloud account with watsonx.ai access
- Git

## Step 1: Install Dependencies

### Using Poetry (Recommended)

```bash
cd ai-career-advisor
poetry install
```

### Using pip

```bash
cd ai-career-advisor
pip install -e .
```

## Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:

```bash
# Get these from IBM Cloud Console
IBM_CLOUD_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here

# Adjust based on your region
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Getting IBM Cloud Credentials

1. **IBM Cloud API Key:**
   - Go to https://cloud.ibm.com/iam/apikeys
   - Click "Create an IBM Cloud API key"
   - Give it a name and description
   - Copy the API key (you won't see it again!)

2. **watsonx.ai Project ID:**
   - Go to https://dataplatform.cloud.ibm.com/wx/home
   - Create or select a project
   - Go to Project Settings → General
   - Copy the Project ID

3. **IBM Cloud Object Storage (Optional):**
   - Go to https://cloud.ibm.com/objectstorage
   - Create a service instance if you don't have one
   - Get credentials from Service Credentials tab

## Step 3: Implementation Order

Follow this order to build the system step by step:

### Phase 1: Core Infrastructure (Week 1)

1. **Implement Configuration & Logging**
   - File: `src/core/config.py` - Already set up, just needs .env
   - File: `src/core/logging.py` - Implement structured logging
   - Test: Create a simple script to verify config loads

2. **Implement LLM Client**
   - File: `src/llm/client.py`
   - Install: `pip install ibm-watsonx-ai`
   - Follow TODO comments in the file
   - Test: Send a simple prompt and get response

3. **Implement Embedding Service**
   - File: `src/llm/embeddings.py`
   - Use IBM Slate embeddings
   - Test: Generate embeddings for sample text

### Phase 2: Knowledge Base (Week 2)

4. **Implement Document Loader**
   - File: `src/knowledge/document_loader.py`
   - Start with PDF and text files
   - Test: Load your CV

5. **Implement Document Chunker**
   - File: `src/knowledge/chunker.py`
   - Start with simple token-based chunking
   - Test: Chunk your CV into pieces

6. **Set Up Vector Store**
   - Choose: FAISS (easiest) or Milvus (your experience)
   - File: `src/retrieval/vector_store.py` (create this)
   - Test: Store and retrieve chunks

### Phase 3: RAG Pipeline (Week 3)

7. **Implement Retriever**
   - File: `src/retrieval/retriever.py` (create this)
   - Combine embedding + vector store
   - Test: Search for relevant chunks

8. **Build CLI Interface**
   - File: `src/cli/main.py` (create this)
   - Use Typer for commands
   - Test: Ask questions via CLI

### Phase 4: Advanced Features (Week 4+)

9. **Add Conversation Memory**
10. **Build Evaluation Suite**
11. **Add Web Search**
12. **Create FastAPI Endpoints**
13. **Build Web UI**

## Step 4: Quick Start Implementation

### Test LLM Connection

Create `test_llm.py`:

```python
from src.core.config import settings
from ibm_watsonx_ai.foundation_models import Model

credentials = {
    "url": settings.ibm_watsonx_url,
    "apikey": settings.ibm_cloud_api_key
}

model = Model(
    model_id=settings.llm_model,
    credentials=credentials,
    project_id=settings.ibm_watsonx_project_id
)

response = model.generate(
    prompt="What are the key skills for a backend engineer?",
    params={
        "max_new_tokens": 200,
        "temperature": 0.7
    }
)

print(response["results"][0]["generated_text"])
```

Run:
```bash
poetry run python test_llm.py
```

### Test Embeddings

Create `test_embeddings.py`:

```python
from src.core.config import settings
from ibm_watsonx_ai.foundation_models import Embeddings

credentials = {
    "url": settings.ibm_watsonx_url,
    "apikey": settings.ibm_cloud_api_key
}

embeddings = Embeddings(
    model_id=settings.embedding_model,
    credentials=credentials,
    project_id=settings.ibm_watsonx_project_id
)

text = "Python backend development with microservices"
result = embeddings.embed_query(text)
embedding = result["results"][0]["embedding"]

print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

Run:
```bash
poetry run python test_embeddings.py
```

## Step 5: Load Your CV

1. Copy your CV to `data/raw/`:
```bash
cp ~/path/to/your/cv.pdf data/raw/
```

2. Create a script to load and chunk it:

```python
from src.knowledge.document_loader import DocumentLoader
from src.knowledge.chunker import DocumentChunker
from src.knowledge.schema import DocumentType

# Load CV
loader = DocumentLoader()
cv_doc = loader.load_document(
    "data/raw/cv.pdf",
    doc_type=DocumentType.CV,
    title="My CV"
)

# Chunk it
chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
chunks = chunker.chunk_document(cv_doc)

print(f"Created {len(chunks)} chunks from CV")
for i, chunk in enumerate(chunks[:3]):  # Show first 3
    print(f"\nChunk {i}:")
    print(chunk.content[:200] + "...")
```

## Common Issues

### Import Errors

If you see import errors like `Import "src.core.logging" could not be resolved`:
- Make sure you're in the project directory
- Run `poetry install` or `pip install -e .`
- The errors are from the type checker and won't affect runtime

### API Authentication Errors

- Double-check your API key and project ID
- Ensure your IBM Cloud account has watsonx.ai access
- Check the region URL matches your instance

### Vector Store Issues

- Start with FAISS (simplest, no server needed)
- For Milvus, you'll need to run a Milvus server locally or use cloud

## Next Steps

1. Complete Phase 1 (Core Infrastructure)
2. Test each component individually
3. Move to Phase 2 (Knowledge Base)
4. Build the RAG pipeline
5. Iterate and improve

## Resources

- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [Granite Models](https://www.ibm.com/granite)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## Getting Help

- Check TODO comments in each file for implementation guidance
- Review the architecture diagram in README.md
- Test each component independently before integration
- Use structured logging to debug issues

Good luck building your AI Career Advisor! 🚀