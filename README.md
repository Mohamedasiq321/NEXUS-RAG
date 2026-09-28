# NEXUS-RAG

### Adaptive Enterprise RAG System

NEXUS-RAG is a local-first Retrieval-Augmented Generation system that combines **hybrid search, agentic multi-hop retrieval, structured-data retrieval, reranking, and grounded answer verification** to produce reliable, source-cited answers from enterprise documents.

## What it does

* Ingests **TXT, PDF, DOCX, and CSV** files
* Creates structure-aware chunks and local embeddings
* Combines **Dense + BM25 hybrid retrieval**
* Uses **cross-encoder reranking** for relevance
* Supports **query routing and transformation**
* Performs controlled **agentic multi-hop retrieval**
* Supports **row-level CSV retrieval and metadata filtering**
* Verifies evidence, citations, and generated claims
* Performs **grounded refusal** when sufficient evidence is unavailable
* Provides retrieval and generation **telemetry** for debugging

## Architecture

```text
User Query
    ↓
Query Router / Transformer
    ↓
Agentic Retrieval
    ├── Dense Search
    ├── BM25 Search
    ├── Structured Search
    └── Multi-Hop Retrieval
    ↓
Hybrid Ranking + Cross-Encoder
    ↓
Evidence Evaluation
    ↓
Ollama LLM
    ↓
Citation + Claim Verification
    ↓
Grounded Answer / Refusal
```

## Tech Stack

**Backend:** Python, FastAPI
**Frontend:** React, Vite, CSS
**Database:** PostgreSQL + pgvector
**Embeddings:** `BAAI/bge-small-en-v1.5`
**Reranker:** `BAAI/bge-reranker-base`
**LLM:** Ollama + `qwen2.5:1.5b`
**Data Processing:** Pandas
**Infrastructure:** Docker

## Example

**Query**

> Which employees have 3 remote days per week and are approved?

**Result**

> EMP005, EMP001 `[S1][S2]`

The system retrieves the matching CSV rows, preserves the structured constraints across retrieval hops, and verifies the resulting evidence before returning the answer.

## Evaluation

On the included **6-query benchmark (K=5)**:

| Strategy | Recall@5 |    MRR | NDCG@5 |
| -------- | -------: | -----: | -----: |
| Dense    |     1.00 | 0.9167 | 0.9555 |
| BM25     |     1.00 | 0.5889 | 0.6852 |
| Hybrid   |     1.00 | 0.8056 | 0.8687 |
| Adaptive |     1.00 | 0.9167 | 0.9385 |

> Benchmark results are specific to the included dataset and corpus.

## Run Locally

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Start PostgreSQL/pgvector and Ollama separately, then load the required Ollama model:

```bash
ollama pull qwen2.5:1.5b
```

## Project Goal

NEXUS-RAG was built to explore how modern RAG systems can move beyond simple **“retrieve → generate”** pipelines toward **adaptive retrieval, structured evidence, verification, and reliable grounded answers**.
