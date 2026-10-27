"""Unit tests for P2: Contracts Schema and 2-Tier Taxonomy Retrieval (S3 & S4)."""

import json
from pathlib import Path
import pytest
from app.knowledge.contract_manager import ContractManager, ContractDefinition
from app.knowledge.retriever import KnowledgeRetriever, RetrievedChunk


CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "knowledge-base" / "contracts"
TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "knowledge-base" / "taxonomy" / "domain_tree.json"

EXPECTED_CONTRACTS = [
    "build_app", "build_tool", "learn", "debug",
    "plan", "business", "event", "write", "analyze",
]


def test_all_contract_files_exist_and_validate_schema():
    """Verify that all 9 required contract JSON files exist and conform to schema."""
    assert CONTRACTS_DIR.exists(), f"Contracts directory missing: {CONTRACTS_DIR}"
    
    for c_name in EXPECTED_CONTRACTS:
        file_path = CONTRACTS_DIR / f"{c_name}.json"
        assert file_path.exists(), f"Contract file missing: {file_path}"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("contract") == c_name
        assert "name" in data and len(data["name"]) > 0
        assert "description" in data and len(data["description"]) > 0
        assert "required_sections" in data and isinstance(data["required_sections"], list)
        assert len(data["required_sections"]) >= 5, f"Contract {c_name} has fewer than 5 required sections"

        for sec in data["required_sections"]:
            assert "heading" in sec and len(sec["heading"].strip()) > 0
            assert "min_items" in sec and sec["min_items"] >= 1
            assert "description" in sec and len(sec["description"].strip()) > 0

        assert "optional_sections" in data and isinstance(data["optional_sections"], list)
        for opt in data["optional_sections"]:
            assert "heading" in opt and len(opt["heading"].strip()) > 0
            assert "trigger_keywords" in opt and isinstance(opt["trigger_keywords"], list)
            assert "out_of_scope_message" in opt and len(opt["out_of_scope_message"]) > 0


def test_contract_manager_loading_and_lookup():
    """Verify that ContractManager loads all 9 contracts and supports lookup."""
    cm = ContractManager(contracts_dir=CONTRACTS_DIR)
    loaded = cm.list_contracts()
    assert len(loaded) >= 9

    for c_name in EXPECTED_CONTRACTS:
        defn = cm.get_contract(c_name)
        assert isinstance(defn, ContractDefinition)
        assert defn.contract == c_name
        assert len(defn.required_headings) >= 5


def test_knowledge_retriever_indexing_and_scoring():
    """Verify that KnowledgeRetriever indexes chunks and retrieves relevant matches."""
    retriever = KnowledgeRetriever()
    assert len(retriever.chunks) > 0

    # Retrieve for Python learning
    results = retriever.retrieve(query="Python programming fundamentals and syntax", domain="Software Development", top_k=3)
    assert len(results) > 0
    assert any("python" in r.content.lower() or "software" in r.domain.lower() for r in results)

    # Verify content share computation
    share = retriever.compute_content_share(results)
    assert "reviewed" in share
    assert "unreviewed" in share
    assert "generated" in share
    assert round(share["reviewed"] + share["unreviewed"] + share["generated"], 0) == 100.0


def test_two_tier_taxonomy_matching_rule():
    """Fixed matching rule: a case matches domain if parent matches OR child matches."""
    assert TAXONOMY_PATH.exists()
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)

    parents = tree.get("parents", {})
    assert len(parents) >= 21

    # Verify parent matches
    sw_children = parents["Software Development"]["children"]
    assert "Webhook Delivery" in sw_children

    def check_match(expected_domain: str, detected_parent: str, detected_child: str) -> bool:
        """S4 Invariant: parent match OR child match."""
        exp = expected_domain.lower()
        par = detected_parent.lower()
        chi = detected_child.lower() if detected_child else ""
        return exp == par or exp in par or (chi and (exp == chi or exp in chi))

    # Match via child
    assert check_match("Webhook Delivery", "Software Development", "Webhook Delivery")
    # Match via parent
    assert check_match("Software Development", "Software Development", "Webhook Delivery")
    # No match
    assert not check_match("Healthcare", "Software Development", "Webhook Delivery")
