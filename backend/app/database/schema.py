SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    source TEXT,
    version TEXT,
    content_hash TEXT UNIQUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    section TEXT,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id
    ON chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON chunks
    USING hnsw (embedding vector_cosine_ops);
"""