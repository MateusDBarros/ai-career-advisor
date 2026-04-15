# AI Career Advisor

A RAG-based AI career advisor that provides personalized career guidance based on your CV, goals, and curated career content.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Knowledge Base                        │
│  CV | Career Content | Job Descriptions | Your Notes    │
│                    (embed + store)                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                     Backend Core                         │
│  Vector Store → Retriever → LLM Layer                   │
│  (Milvus/FAISS)  (Top-k)    (Anthropic)                │
│                                                          │
│  Memory | Eval Suite | Web Search                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   User Interface                         │
│        CLI | FastAPI | Web UI | Observability           │
└─────────────────────────────────────────────────────────┘
```

## Features

- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **Vector Search**: Efficient similarity search using Milvus or FAISS
- **Multi-source Knowledge**: CV, career guides, job descriptions, personal notes
- **Conversation Memory**: Maintains context across interactions
- **Evaluation Suite**: Test and validate response quality
- **Web Search**: Live market data integration (planned)
- **CLI First**: Start with command-line interface, expand to web

## Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **LLM**: Anthropic Claude (via API)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: Milvus / FAISS / ChromaDB
- **CLI**: Typer + Rich
- **Observability**: Structlog, Prometheus

## Project Structure

```
ai-career-advisor/
├── src/
│   ├── core/           # Core utilities, config, logging
│   ├── knowledge/      # Document ingestion, chunking
│   ├── retrieval/      # Vector store, retriever logic
│   ├── llm/            # LLM integration, prompts
│   ├── cli/            # CLI interface
│   └── api/            # FastAPI endpoints (future)
├── tests/              # Unit and integration tests
├── data/
│   ├── raw/            # Original documents (CV, guides)
│   ├── processed/      # Chunked and processed docs
│   └── vectors/        # Vector store data
├── config/             # Configuration files
└── docs/               # Documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- Poetry (recommended) or pip
- Anthropic API key
- OpenAI API key (for embeddings)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   # or
   pip install -e .
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Initialize the knowledge base:
   ```bash
   poetry run career-advisor init
   ```

### Usage

```bash
# Ask a question
poetry run career-advisor ask "What skills should I focus on for senior backend roles?"

# Add content to knowledge base
poetry run career-advisor add-content path/to/document.md

# View knowledge base stats
poetry run career-advisor stats
```

## Development Roadmap

- [x] Project structure and dependencies
- [ ] Document ingestion pipeline
- [ ] Vector store setup (FAISS/Milvus)
- [ ] Embedding generation service
- [ ] Basic retriever with similarity search
- [ ] LLM integration
- [ ] CLI interface
- [ ] Conversation memory
- [ ] Evaluation suite
- [ ] Web search integration
- [ ] FastAPI endpoints
- [ ] Web UI

## Contributing

This is a personal learning project, but suggestions and feedback are welcome!

## License

MIT