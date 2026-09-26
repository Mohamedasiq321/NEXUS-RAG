import { useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState("");

  const fileInputRef = useRef(null);

  const askNexus = async () => {
    if (!query.trim() || loading) {
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/rag/query`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: query.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to process the query."
        );
      }

      setResult(data);
    } catch (error) {
      setResult({
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);
    setUploadResult(null);
    setUploadError("");
  };

  const uploadDocument = async () => {
    if (!selectedFile || uploading) {
      return;
    }

    setUploading(true);
    setUploadResult(null);
    setUploadError("");

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile
    );

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Document upload failed."
        );
      }

      setUploadResult(data);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleQueryKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askNexus();
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">N</div>

          <div>
            <div className="brand-name">
              NEXUS-RAG
            </div>

            <div className="brand-subtitle">
              Adaptive Enterprise Intelligence
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          System Online
        </div>
      </header>

      <main className="main-content">

        {/* HERO */}

        <section className="hero-section">
          <div className="eyebrow">
            ENTERPRISE RESEARCH AGENT
          </div>

          <h1>
            Ask questions.
            <br />
            <span>Get grounded answers.</span>
          </h1>

          <p>
            NEXUS-RAG retrieves relevant evidence,
            reranks supporting context, and verifies
            answers against your knowledge base.
          </p>
        </section>


        {/* KNOWLEDGE BASE */}

        <section className="knowledge-section">
          <div className="section-heading">
            <div>
              <div className="section-eyebrow">
                KNOWLEDGE BASE
              </div>

              <h2>
                Add enterprise documents
              </h2>

              <p>
                Upload documents to make them
                searchable by NEXUS.
              </p>
            </div>
          </div>

          <div className="upload-card">

            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.docx,.csv"
              onChange={handleFileChange}
              hidden
            />

            <button
              className="drop-zone"
              onClick={() =>
                fileInputRef.current?.click()
              }
            >
              <div className="upload-icon">
                ↑
              </div>

              <strong>
                {selectedFile
                  ? selectedFile.name
                  : "Choose a document"}
              </strong>

              <span>
                {selectedFile
                  ? `${(
                      selectedFile.size / 1024
                    ).toFixed(1)} KB`
                  :  "TXT, PDF, DOCX, and CSV files supported"}
              </span>
            </button>

            <div className="upload-actions">

              <button
                className="secondary-button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
              >
                Browse Files
              </button>

              <button
                className="primary-button"
                disabled={
                  !selectedFile || uploading
                }
                onClick={uploadDocument}
              >
                {uploading
                  ? "Indexing..."
                  : "Upload & Index →"}
              </button>

            </div>

            {uploadResult && (
              <div className="upload-success">
                <div className="success-title">
                  ✓ Document indexed successfully
                </div>

                <div className="upload-details">
                  <span>
                    {uploadResult.document.file_name}
                  </span>

                  <span>
                    {uploadResult.document.chunk_count} chunks
                  </span>

                  <span>
                    {uploadResult.document.embedding_dimension}d embeddings
                  </span>
                </div>
              </div>
            )}

            {uploadError && (
              <div className="upload-error">
                {uploadError}
              </div>
            )}
          </div>
        </section>


        {/* QUERY */}

        <section className="query-section">

          <div className="section-eyebrow">
            RESEARCH QUERY
          </div>

          <div className="query-card">

            <textarea
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              onKeyDown={handleQueryKeyDown}
              placeholder="Ask NEXUS anything about your knowledge base..."
              rows={4}
            />

            <div className="query-footer">

              <span className="keyboard-hint">
                Press Enter to submit
              </span>

              <button
                className="primary-button"
                onClick={askNexus}
                disabled={
                  !query.trim() || loading
                }
              >
                {loading
                  ? "Researching..."
                  : "Ask NEXUS →"}
              </button>

            </div>
          </div>
        </section>


        {/* RESULT */}

        {result && !result.error && (
          <section className="result-section">

            <div className="result-header">
              <div>
                <div className="section-eyebrow">
                  RESEARCH RESULT
                </div>

                <h2>
                  Grounded Answer
                </h2>
              </div>

              <div
  className={`verification-badge ${
    result.verification_passed &&
    result.claims_supported &&
    result.grounded
      ? "verified"
      : "unverified"
  }`}
>
  {result.verification_passed &&
  result.claims_supported &&
  result.grounded
    ? "✓ Verified"
    : "⚠ Verification failed"}
</div>
            </div>

            <div className="answer-card">

              <div className="answer-label">
  {result.grounded
    ? "Evidence grounded"
    : "Evidence verification failed"}
</div>

              <p className="answer-text">
                {result.answer}
              </p>

              <div className="result-metadata">

                <div>
                  <span>Claims supported</span>
                  <strong>
                    {result.claims_supported
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>

                <div>
                  <span>Sources</span>
                  <strong>
                    {result.citations?.length || 0}
                  </strong>
                </div>

                <div>
                  <span>Grounded</span>
                  <strong>
                    {result.grounded
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>

              </div>
            </div>


            {result.citations?.length > 0 && (
              <div className="evidence-section">

                <div className="section-eyebrow">
                  EVIDENCE SOURCES
                </div>

                <h3>
                  Supporting Documents
                </h3>

                <div className="source-grid">

                  {result.citations.map(
                    (citation) => (
                      <div
                        className="source-card"
                        key={
                          citation.citation_id
                        }
                      >
                        <div className="source-top">
                          <span className="source-id">
                            {citation.citation_id}
                          </span>

                          <span className="source-type">
                            Document
                          </span>
                        </div>

                        <strong>
                          {citation.section}
                        </strong>

                        <div className="source-meta">
                          Document ID:{" "}
                          {citation.document_id}
                        </div>

                        <div className="source-meta">
                          Chunk:{" "}
                          {citation.chunk_id}
                        </div>
                      </div>
                    )
                  )}

                </div>
              </div>
            )}

          </section>
        )}


        {result?.error && (
          <div className="error-card">
            {result.error}
          </div>
        )}


        {/* CAPABILITIES */}

        <section className="capabilities-section">

          <div className="section-eyebrow">
            SYSTEM CAPABILITIES
          </div>

          <div className="capability-grid">

            <div className="capability-card">
              <span>01</span>
              <h3>
                Hybrid Retrieval
              </h3>
              <p>
                Dense vector search combined
                with BM25 lexical retrieval.
              </p>
            </div>

            <div className="capability-card">
              <span>02</span>
              <h3>
                Reranking
              </h3>
              <p>
                Cross-encoder reranking improves
                evidence relevance.
              </p>
            </div>

            <div className="capability-card">
              <span>03</span>
              <h3>
                Agentic Retrieval
              </h3>
              <p>
                Queries can be decomposed,
                refined, and retrieved across
                multiple hops.
              </p>
            </div>

            <div className="capability-card">
              <span>04</span>
              <h3>
                Grounded Generation
              </h3>
              <p>
                Answers are checked against
                retrieved evidence and citations.
              </p>
            </div>

          </div>
        </section>

      </main>

      <footer className="footer">
        NEXUS-RAG · Adaptive Enterprise Intelligence
      </footer>
    </div>
  );
}

export default App;