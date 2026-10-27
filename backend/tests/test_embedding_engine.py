"""Automated test suite verifying Step 4: Embedding Engine and Semantic Retrieval."""

from __future__ import annotations

import numpy as np
import pytest
from app.knowledge.knowledge_manager import KnowledgeManager
from app.knowledge.semantic_store import SemanticKnowledgeStore
from app.ml.embeddings import EmbeddingEngine, VectorStore


@pytest.fixture(scope="module")
def engine() -> EmbeddingEngine:
    return EmbeddingEngine(dimension=384)


@pytest.fixture(scope="module")
def semantic_store() -> SemanticKnowledgeStore:
    km = KnowledgeManager("c:/intentify/knowledge-base")
    return SemanticKnowledgeStore(knowledge_manager=km)


def test_vector_dimension_and_normalization(engine: EmbeddingEngine):
    """Verify vectors have exact 384 dimensions and unit L2 length (norm = 1.0)."""
    text = "Build a scalable microservices architecture in Python"
    vec = engine.encode_single(text)

    assert isinstance(vec, np.ndarray)
    assert vec.shape == (384,)
    assert vec.dtype == np.float32

    # L2 Norm must equal 1.0
    norm = float(np.linalg.norm(vec))
    assert abs(norm - 1.0) < 1e-4, f"Vector norm must be 1.0, got {norm}"

    # Batch encoding
    batch = ["First text", "Second text", "Third text"]
    mat = engine.encode(batch)
    assert mat.shape == (3, 384)
    norms = np.linalg.norm(mat, axis=1)
    for n in norms:
        assert abs(float(n) - 1.0) < 1e-4


def test_semantic_similarity_technical_domain(engine: EmbeddingEngine):
    """Verify semantic similarity differentiates technical synonyms from unrelated topics."""
    query = "FastAPI backend REST API development"
    related = "Python web framework microservice server"
    unrelated = "organic tomato fertilizer soil gardening"

    sim_related = engine.similarity(query, related)
    sim_unrelated = engine.similarity(query, unrelated)

    assert sim_related > sim_unrelated, (
        f"Related similarity ({sim_related}) must exceed unrelated ({sim_unrelated})"
    )
    assert sim_related > 0.40, f"Expected strong similarity, got {sim_related}"


def test_semantic_similarity_wedding_domain(engine: EmbeddingEngine):
    """Verify semantic similarity for the core scenario: wedding planning."""
    query = "wedding planner event coordinator"
    related = "marriage ceremony reception catering banquet"
    unrelated = "quantum entanglement semiconductor laser physics"

    sim_related = engine.similarity(query, related)
    sim_unrelated = engine.similarity(query, unrelated)

    assert sim_related > sim_unrelated, (
        f"Related wedding similarity ({sim_related}) must exceed physics ({sim_unrelated})"
    )
    assert sim_related > 0.40


def test_semantic_similarity_medical_domain(engine: EmbeddingEngine):
    """Verify semantic similarity for healthcare concepts."""
    query = "clinical diagnosis physician treatment patient"
    related = "doctor hospital prescription medicine therapy"
    unrelated = "heavy diesel engine mechanical gearbox transmission"

    sim_related = engine.similarity(query, related)
    sim_unrelated = engine.similarity(query, unrelated)

    assert sim_related > sim_unrelated
    assert sim_related > 0.40


def test_vector_store_operations(engine: EmbeddingEngine):
    """Verify in-memory vector store indexing and cosine dot product search."""
    store = engine.create_vector_store()

    texts = [
        "Software Engineer building scalable web applications",
        "Clinical Cardiologist treating heart disease",
        "Corporate Attorney handling M&A contracts",
        "Wedding Planning Specialist organizing ceremonies",
    ]
    vectors = engine.encode(texts)
    metadata = [{"category": "tech"}, {"category": "medical"}, {"category": "legal"}, {"category": "hospitality"}]

    store.add_batch(texts, vectors, metadata)
    assert len(store) == 4

    # Search for tech role
    q_vec = engine.encode_single("Python developer coding API")
    results = store.search(q_vec, top_k=2)

    assert len(results) == 2
    assert "Software Engineer" in results[0].text
    assert results[0].metadata["category"] == "tech"
    assert results[0].score > 0.35


def test_semantic_knowledge_store_indexing(semantic_store: SemanticKnowledgeStore):
    """Verify that all knowledge base artifacts are indexed in the semantic store."""
    assert len(semantic_store.role_store) >= 100
    assert len(semantic_store.domain_store) >= 80
    assert len(semantic_store.blueprint_store) == 13
    assert len(semantic_store.template_store) >= 20


def test_semantic_role_retrieval(semantic_store: SemanticKnowledgeStore):
    """Verify semantic retrieval finds the appropriate role for various queries."""
    # 1. Wedding query
    results_wedding = semantic_store.search_roles("wedding planner coordinator marriage ceremony", top_k=3)
    assert len(results_wedding) > 0
    top_role = results_wedding[0].metadata
    assert "Wedding" in top_role.get("title", "") or "Event" in top_role.get("title", "")

    # 2. Software query
    results_dev = semantic_store.search_roles("build web backend python code", top_k=3)
    assert len(results_dev) > 0
    top_dev_title = results_dev[0].metadata.get("title", "")
    assert any(w in top_dev_title for w in ["Software", "Engineer", "Developer", "Full-Stack"])


def test_semantic_domain_retrieval(semantic_store: SemanticKnowledgeStore):
    """Verify semantic domain search maps tech queries to DevOps/Software and health to Healthcare."""
    res_cloud = semantic_store.search_domains("docker kubernetes aws container deployment", top_k=3)
    assert len(res_cloud) > 0
    top_cloud_domain = res_cloud[0].metadata.get("name", "")
    assert top_cloud_domain in ["DevOps", "Cloud Computing", "Software Development"]

    res_event = semantic_store.search_domains("wedding reception banquet ceremony decor", top_k=3)
    assert len(res_event) > 0
    top_event_domain = res_event[0].metadata.get("name", "")
    assert any(w in top_event_domain for w in ["Event", "Wedding", "Hospitality"])


def test_semantic_template_retrieval(semantic_store: SemanticKnowledgeStore):
    """Verify semantic template search maps requests to appropriate output structures."""
    res_steps = semantic_store.search_templates("numbered walkthrough step by step guide", top_k=3)
    assert len(res_steps) > 0
    top_format = res_steps[0].metadata.get("name", "")
    assert "Step-by-Step" in top_format or "Guide" in top_format or "Tutorial" in top_format


def test_empty_and_edge_case_embeddings(engine: EmbeddingEngine):
    """Verify zero crash on empty string, whitespace, and long inputs."""
    v_empty = engine.encode_single("")
    assert v_empty.shape == (384,)

    v_spaces = engine.encode_single("     ")
    assert v_spaces.shape == (384,)

    long_text = "word " * 3000
    v_long = engine.encode_single(long_text)
    assert v_long.shape == (384,)
    norm = float(np.linalg.norm(v_long))
    assert abs(norm - 1.0) < 1e-4
