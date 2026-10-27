"""Automated test suite verifying Step 2: Knowledge Base Architecture and Artifacts."""

from __future__ import annotations

import pytest
from app.knowledge.domain_resolver import DomainResolver
from app.knowledge.knowledge_manager import KnowledgeManager
from app.knowledge.role_resolver import RoleResolver


@pytest.fixture(scope="module")
def km() -> KnowledgeManager:
    """Fixture providing initialized KnowledgeManager."""
    return KnowledgeManager(base_path="c:/intentify/knowledge-base")


def test_roles_completeness(km: KnowledgeManager):
    """Verify at least 100 professional roles with required schema fields and unique IDs."""
    roles = km.get_roles()
    assert len(roles) >= 100, f"Expected >= 100 roles, found {len(roles)}"

    ids = set()
    categories = set()

    for r in roles:
        assert "id" in r and r["id"], "Role must have a non-empty 'id'"
        assert r["id"] not in ids, f"Duplicate role id found: {r['id']}"
        ids.add(r["id"])

        assert "title" in r and r["title"], "Role must have a non-empty 'title'"
        assert "category" in r and r["category"], "Role must have a 'category'"
        categories.add(r["category"])

        assert isinstance(r.get("aliases"), list) and len(r["aliases"]) >= 1, f"Role {r['title']} missing aliases"
        assert isinstance(r.get("expertise_areas"), list) and len(r["expertise_areas"]) >= 2, f"Role {r['title']} missing expertise areas"
        assert isinstance(r.get("typical_intents"), list) and len(r["typical_intents"]) >= 1, f"Role {r['title']} missing typical intents"
        assert isinstance(r.get("common_domains"), list), f"Role {r['title']} missing common domains"
        assert "prompt_style" in r, f"Role {r['title']} missing prompt_style"
        assert isinstance(r.get("keywords"), list), f"Role {r['title']} missing keywords"

    # Diverse category representation
    assert len(categories) >= 8, f"Expected >= 8 role categories, found {len(categories)}"

    # Check for Wedding Planning role
    wedding_roles = [r for r in roles if "wedding" in r["title"].lower() or any("wedding" in a.lower() for a in r["aliases"])]
    assert len(wedding_roles) >= 1, "Expected at least one wedding planning role in roles.json"


def test_domains_completeness(km: KnowledgeManager):
    """Verify at least 80 specialized industry domains with valid relations."""
    domains = km.get_domains()
    assert len(domains) >= 80, f"Expected >= 80 domains, found {len(domains)}"

    ids = set()
    categories = set()

    for d in domains:
        assert "id" in d and d["id"], "Domain must have a non-empty 'id'"
        assert d["id"] not in ids, f"Duplicate domain id: {d['id']}"
        ids.add(d["id"])

        assert "name" in d and d["name"], "Domain must have a 'name'"
        assert "category" in d and d["category"], "Domain must have a 'category'"
        categories.add(d["category"])

        assert isinstance(d.get("sub_domains"), list) and len(d["sub_domains"]) >= 2, f"Domain {d['name']} missing sub_domains"
        assert isinstance(d.get("keywords"), list) and len(d["keywords"]) >= 3, f"Domain {d['name']} missing keywords"
        assert isinstance(d.get("prompt_context_hints"), list) and len(d["prompt_context_hints"]) >= 1, f"Domain {d['name']} missing prompt_context_hints"

    assert len(categories) >= 10, f"Expected >= 10 domain categories, found {len(categories)}"


def test_blueprints_completeness(km: KnowledgeManager):
    """Verify blueprints cover all 13 core prompt intents with complete 9 sections."""
    blueprints = km.get_blueprints()
    assert len(blueprints) == 13, f"Expected exactly 13 intent blueprints, found {len(blueprints)}"

    expected_intents = {
        "create", "write", "generate", "plan", "analyze", "explain",
        "compare", "translate", "research", "design", "debug", "improve", "decide"
    }

    found_intents = set()
    required_sections = {
        "role", "objective", "context", "requirements",
        "constraints", "instructions", "output_format", "assumptions", "quality_checklist"
    }

    for bp in blueprints:
        intent = bp.get("intent")
        assert intent in expected_intents, f"Unknown blueprint intent: {intent}"
        found_intents.add(intent)

        sections = bp.get("sections", [])
        section_names = {s.get("name") for s in sections}
        missing_sections = required_sections - section_names
        assert not missing_sections, f"Blueprint '{intent}' is missing required sections: {missing_sections}"

        # Verify quality weights sum to 100
        weights = bp.get("quality_weights", {})
        total_weight = sum(weights.values())
        assert total_weight == 100, f"Blueprint '{intent}' quality weights must sum to 100, got {total_weight}"

    assert found_intents == expected_intents, f"Missing blueprints for intents: {expected_intents - found_intents}"


def test_templates_completeness(km: KnowledgeManager):
    """Verify at least 20 output format templates with structure placeholders."""
    templates = km.get_templates()
    assert len(templates) >= 20, f"Expected >= 20 output formats, found {len(templates)}"

    ids = set()
    for t in templates:
        assert "id" in t and t["id"], "Template must have an id"
        assert t["id"] not in ids, f"Duplicate template id: {t['id']}"
        ids.add(t["id"])

        assert "name" in t and t["name"], "Template must have a name"
        assert "structure" in t and t["structure"], f"Template {t['name']} must define output structure"
        assert isinstance(t.get("suitable_intents"), list) and len(t["suitable_intents"]) >= 1

    # Verify key enterprise templates exist
    template_ids = {t["id"] for t in templates}
    assert "format_detailed_technical" in template_ids
    assert "format_step_by_step_guide" in template_ids
    assert "format_comparison_matrix" in template_ids
    assert "format_json_schema" in template_ids
    assert "format_executive_brief" in template_ids
    assert "format_rca_report" in template_ids
    assert "format_adr" in template_ids


def test_quality_rules_structure(km: KnowledgeManager):
    """Verify 100-point rubric breakdown and threshold."""
    rules = km.get_quality_rules()
    assert rules.get("threshold") == 85.0
    assert rules.get("max_score") == 100.0

    criteria = rules.get("criteria", [])
    assert len(criteria) == 6, f"Expected 6 criteria, found {len(criteria)}"

    total_score = sum(c.get("max_score", 0.0) for c in criteria)
    assert total_score == 100.0, f"Total criteria score must equal 100.0, got {total_score}"

    criteria_ids = {c["id"] for c in criteria}
    expected_ids = {"clarity", "specificity", "context", "constraints", "output_format", "ambiguity_handling"}
    assert criteria_ids == expected_ids


def test_default_assumptions_coverage(km: KnowledgeManager):
    """Verify baseline proactive assumptions across general, domains, and intents."""
    assumptions = km.get_assumptions()

    general = assumptions.get("general_defaults", [])
    assert len(general) >= 3, "Expected at least 3 general baseline assumptions"

    domains = assumptions.get("domain_assumptions", {})
    assert len(domains) >= 8, f"Expected >= 8 domain assumption sets, found {len(domains)}"
    assert "Software Development" in domains
    assert "Healthcare" in domains
    assert "Legal" in domains
    assert "Finance" in domains

    intents = assumptions.get("intent_assumptions", {})
    assert len(intents) >= 4, f"Expected >= 4 intent assumption sets, found {len(intents)}"


def test_wedding_planner_scenario(km: KnowledgeManager):
    """Test the specific user requirement: 'mare wedding planner mate prompt joiye'."""
    role_resolver = RoleResolver(km)
    domain_resolver = DomainResolver(km)

    # 1. Role resolution with empty role and Gujarati input
    role_result = role_resolver.resolve(
        role_input="",
        detail_text="mare wedding planner mate prompt joiye",
    )
    assert "Wedding Planning" in role_result.role_title
    assert "Hospitality" in role_result.category or "Events" in role_result.category

    # 2. Domain resolution with wedding keywords
    domain_result = domain_resolver.resolve("wedding venue catering guest list banquet decor lagan")
    assert "Event Planning" in domain_result.domain or "Wedding" in domain_result.domain
    assert len(domain_result.sub_domains) >= 2
