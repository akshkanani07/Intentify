"""Unit tests for the 2-Tier Hierarchical Domain Taxonomy (Step 1 Requirement 4)."""

import json
from pathlib import Path
import pytest


TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "knowledge-base" / "taxonomy" / "domain_tree.json"


@pytest.fixture(scope="module")
def domain_tree_data():
    assert TAXONOMY_PATH.exists(), f"Taxonomy file not found at {TAXONOMY_PATH}"
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_taxonomy_file_structure(domain_tree_data):
    """Verify top-level keys and metadata."""
    assert "version" in domain_tree_data
    assert "parents" in domain_tree_data
    assert len(domain_tree_data["parents"]) >= 21


def test_every_child_has_exactly_one_parent(domain_tree_data):
    """Invariant: Every child specialization must belong to exactly one parent domain."""
    seen_children: dict[str, str] = {}
    duplicate_children: list[tuple[str, str, str]] = []

    for parent_name, parent_data in domain_tree_data["parents"].items():
        children = parent_data.get("children", {})
        for child_name in children:
            if child_name in seen_children:
                duplicate_children.append((child_name, seen_children[child_name], parent_name))
            else:
                seen_children[child_name] = parent_name

    assert not duplicate_children, f"Found children with multiple parents: {duplicate_children}"
    assert len(seen_children) >= 80, f"Expected at least 80 child specializations, got {len(seen_children)}"


def test_no_orphan_triggers_and_valid_formats(domain_tree_data):
    """Invariant: All parent and child triggers must be non-empty valid strings."""
    for parent_name, parent_data in domain_tree_data["parents"].items():
        parent_triggers = parent_data.get("triggers", [])
        assert isinstance(parent_triggers, list), f"Parent {parent_name} triggers must be a list"
        assert len(parent_triggers) > 0, f"Parent {parent_name} has no triggers (orphan)"
        for pt in parent_triggers:
            assert isinstance(pt, str) and len(pt.strip()) >= 2, f"Invalid parent trigger '{pt}' in {parent_name}"

        children = parent_data.get("children", {})
        for child_name, child_data in children.items():
            child_triggers = child_data.get("triggers", [])
            assert isinstance(child_triggers, list), f"Child {child_name} triggers must be a list"
            assert len(child_triggers) > 0, f"Child {child_name} has no triggers (orphan)"
            for ct in child_triggers:
                assert isinstance(ct, str) and len(ct.strip()) >= 2, f"Invalid child trigger '{ct}' in {child_name}"
