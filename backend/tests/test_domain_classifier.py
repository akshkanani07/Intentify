"""Tests for Step 7: Domain Intelligence & Classification Engine."""

import pytest
from app.knowledge.domain_graph import DomainKnowledgeGraph, DomainNode
from app.knowledge.domain_resolver import DomainResolver, DomainResult
from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.domain_classifier import DomainClassifier
from app.nlp.entity_extractor import Entity


@pytest.fixture
def km():
    return KnowledgeManager()


@pytest.fixture
def graph(km):
    return DomainKnowledgeGraph(knowledge_manager=km)


@pytest.fixture
def resolver(km, graph):
    return DomainResolver(knowledge_manager=km, domain_graph=graph)


class TestDomainKnowledgeGraph:
    """Verifies graph structure, nodes, categories, and relational traversal."""

    def test_graph_initialization(self, graph):
        assert len(graph.nodes) >= 86
        assert len(graph.category_index) >= 15
        assert "Healthcare" in graph.category_index or "Technology" in graph.category_index

    def test_lookup_node_by_name(self, graph):
        node = graph.get_node("Software Development")
        assert node is not None
        assert node.category == "Technology"
        assert len(node.sub_domains) > 0

    def test_get_related_domains(self, graph):
        node = graph.get_node("Software Development")
        assert node is not None
        related = graph.get_related_domains(node.id)
        # Software Development has related domains in domains.json
        assert isinstance(related, list)

    def test_expand_context_hints(self, graph):
        hints = graph.expand_context_hints("Software Development")
        assert len(hints) > 0
        assert any("stack" in h.lower() or "architecture" in h.lower() or "technology" in h.lower() for h in hints)

    def test_register_dynamic_domain(self, graph):
        dynamic = graph.register_dynamic_domain(
            name="Quantum Bio-Memristor Engineering",
            category="Advanced Nanotechnology",
            sub_domains=["Synaptic Nanocircuits", "Bio-memristive State Control"],
        )
        assert isinstance(dynamic, DomainNode)
        assert dynamic.is_dynamic is True
        assert dynamic.id in graph.nodes
        assert graph.get_node("Quantum Bio-Memristor Engineering") is not None


class TestDomainResolver:
    """Verifies domain classification across required domains, multilingual inputs, and novel industries."""

    def test_medical_domain(self, resolver):
        result = resolver.resolve("Clinical oncology protocol and chemotherapy dosage for hospital patient")
        assert isinstance(result, DomainResult)
        assert result.category == "Healthcare" or "Health" in result.domain or "Medicine" in result.domain
        assert result.confidence >= 0.85
        assert not result.is_dynamic

    def test_legal_domain(self, resolver):
        result = resolver.resolve("Draft an indemnification clause for a commercial SaaS contract compliance audit")
        assert result.category == "Legal" or "Legal" in result.domain
        assert result.confidence >= 0.85
        assert not result.is_dynamic

    def test_marketing_domain(self, resolver):
        result = resolver.resolve("SEO campaign and conversion rate optimization for social media advertising")
        assert result.category == "Marketing" or "Marketing" in result.domain
        assert not result.is_dynamic

    def test_engineering_domain(self, resolver):
        result = resolver.resolve("Perform mechanical stress analysis and thermodynamics on aerospace titanium turbine")
        assert result.category == "Engineering" or "Engineering" in result.domain
        assert not result.is_dynamic

    def test_agriculture_domain(self, resolver):
        result = resolver.resolve("Soil nitrogen management, crop rotation schedule, and precision farming irrigation")
        assert result.category == "Agriculture" or "Agriculture" in result.domain
        assert not result.is_dynamic

    def test_education_domain(self, resolver):
        result = resolver.resolve("Design an e-learning curriculum and pedagogy syllabus for high school students")
        assert result.category == "Education" or "Education" in result.domain
        assert not result.is_dynamic

    def test_finance_domain(self, resolver):
        result = resolver.resolve("Discounted cash flow valuation and investment portfolio risk model for banking")
        assert result.category == "Finance" or "Finance" in result.domain
        assert not result.is_dynamic

    def test_science_domain(self, resolver):
        result = resolver.resolve("Quantum entanglement simulation and molecular biology research")
        assert result.category == "Science" or "Science" in result.domain
        assert not result.is_dynamic

    def test_creative_domain(self, resolver):
        result = resolver.resolve("Worldbuilding, character arcs, and poetry composition for fantasy fiction novel")
        assert result.category in ["Arts & Creative", "Arts"] or "Creative" in result.domain
        assert not result.is_dynamic

    def test_event_planning_wedding_domain(self, resolver):
        result = resolver.resolve("mare wedding planner mate prompt joiye destination wedding in Udaipur")
        assert "Wedding" in result.domain or "Hospitality" in result.category or "Lifestyle" in result.category
        assert not result.is_dynamic

    def test_multilingual_gujarati_agriculture(self, resolver):
        result = resolver.resolve("ખેતી ના પાક અને જમીન ના પોષક તત્વો માટે આયોજન")
        assert result.category == "Agriculture" or "Agriculture" in result.domain

    def test_multilingual_hindi_legal(self, resolver):
        result = resolver.resolve("अदालत में दायर याचिका और कानूनी सलाह के लिए मसौदा")
        assert result.category == "Legal" or "Legal" in result.domain

    def test_entity_based_resolution(self, resolver):
        entities = [Entity(text="Kubernetes", label="TECHNOLOGY", start=0, end=10, confidence=0.95)]
        result = resolver.resolve("Deploy high availability cluster", entities=entities)
        assert "Software" in result.domain or "Technology" in result.category

    def test_unlimited_novel_industry_dynamic_synthesis(self, resolver):
        """Unknown/emerging industry must generate dynamic domain and register in Knowledge Graph."""
        novel_query = "Interstellar Tachyon Drive Calibration and Subspace Relativistic Navigation"
        result = resolver.resolve(novel_query)

        assert isinstance(result, DomainResult)
        assert result.is_dynamic is True
        assert result.category == "Emerging / Specialized Industry"
        assert len(result.sub_domains) >= 3
        assert len(result.context_hints) >= 3
        assert any("Tachyon" in s or "Interstellar" in s or "Relativistic" in s for s in result.sub_domains)

    def test_empty_and_whitespace_fallback(self, resolver):
        result = resolver.resolve("")
        assert result.domain == "General"
        assert result.matched_method == "fallback"

        result_ws = resolver.resolve("   \n\t  ")
        assert result_ws.domain == "General"
        assert result_ws.matched_method == "fallback"
