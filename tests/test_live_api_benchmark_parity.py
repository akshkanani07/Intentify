"""Gate test for Step 3: Verifies exact mathematical score parity between live API pipeline and benchmark runner."""

import pytest
from app.api.v1.schemas.prompt import PromptGenerationRequest
from app.engine.planner import KnowledgePlanner
from app.engine.quality_engine import QualityEngine
from app.engine.reranker import CandidateReranker
from app.engine.spec_extractor import SpecExtractor
from app.services.orchestrator import PromptOrchestrator


@pytest.fixture(scope="module")
def orchestrator():
    return PromptOrchestrator()


@pytest.fixture(scope="module")
def benchmark_suite():
    planner = KnowledgePlanner()
    quality = QualityEngine()
    reranker = CandidateReranker(planner=planner, quality_engine=quality)
    extractor = SpecExtractor()
    return {
        "planner": planner,
        "quality": quality,
        "reranker": reranker,
        "extractor": extractor,
    }


@pytest.mark.parametrize(
    "case_input, role, language",
    [
        ("Build a scalable Kafka microservice with idempotent webhook consumers", "", "English"),
        ("હું શિખાઉ છું, મને પાયથોન શીખવો", "", "Gujarati"),
        ("Create an enterprise B2B SaaS lead generation strategy with account-based marketing (ABM)", "Senior Marketing Director", "English"),
        ("kuch banao mere liye", "", "Hindi"),
    ],
)
def test_live_api_and_benchmark_exact_score_parity(orchestrator, benchmark_suite, case_input, role, language):
    """Assert that calling the live API pipeline and running the benchmark on the same input

    return the EXACT same score, before and after caps.
    """
    # 1. Live API Pipeline Execution
    req = PromptGenerationRequest(detail=case_input, role=role, language=language)
    api_res = orchestrator.generate_prompt_sync(req)

    # 2. Benchmark Pipeline Execution
    extractor = benchmark_suite["extractor"]
    reranker = benchmark_suite["reranker"]
    quality = benchmark_suite["quality"]

    spec = extractor.extract(text=case_input, role_hint=role, language_hint=language)
    winner, _ = reranker.generate_and_rerank(spec)
    standards_registry = benchmark_suite["planner"].km.list_standards()
    audit = quality.audit(
        prompt_text=winner.full_text,
        spec=spec,
        raw_input=case_input,
        standards_registry=standards_registry,
    )

    # 3. Assert Exact Parity Before and After Caps
    assert api_res.metadata is not None, "API response missing metadata"
    assert api_res.quality_score == round(audit.total_score, 2), (
        f"Score mismatch for '{case_input}': API={api_res.quality_score}, Benchmark={audit.total_score}"
    )
    assert api_res.metadata.score_before_cap == audit.score_before_cap, (
        f"score_before_cap mismatch: API={api_res.metadata.score_before_cap}, Benchmark={audit.score_before_cap}"
    )
    assert api_res.metadata.score_after_cap == audit.score_after_cap, (
        f"score_after_cap mismatch: API={api_res.metadata.score_after_cap}, Benchmark={audit.score_after_cap}"
    )

    # 4. Assert Penalties List Count Parity
    expected_penalties_count = len(audit.audit_result.penalties) if audit.audit_result else 0
    assert len(api_res.metadata.penalties) == expected_penalties_count, (
        f"Penalties count mismatch: API={len(api_res.metadata.penalties)}, Benchmark={expected_penalties_count}"
    )
