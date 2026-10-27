"""KnowledgeManager – manages static and dynamic domain/role/blueprint data."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any
from app.core.config import get_settings
from app.core.exceptions import KnowledgeBaseError

logger = logging.getLogger("intentify.knowledge.manager")


class KnowledgeManager:
    """Loads and caches knowledge base artifacts (roles, domains, blueprints, formats, quality rules)."""

    _instance: KnowledgeManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> KnowledgeManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_path: str | Path | None = None) -> None:
        if getattr(self, "_initialized", False):
            return
        settings = get_settings()
        kb_path = Path(base_path or settings.KNOWLEDGE_BASE_DIR)
        if not kb_path.exists():
            cand = Path(__file__).resolve()
            for _ in range(5):
                cand = cand.parent
                if (cand / "knowledge-base").exists():
                    kb_path = cand / "knowledge-base"
                    break
        self.base_path = kb_path
        self._roles: list[dict[str, Any]] = []
        self._domains: list[dict[str, Any]] = []
        self._blueprints: list[dict[str, Any]] = []
        self._templates: list[dict[str, Any]] = []
        self._quality_rules: dict[str, Any] = {}
        self._assumptions: dict[str, Any] = {}
        self._concept_graphs: dict[str, dict[str, Any]] = {}
        self._concept_aliases: dict[str, str] = {}
        self._standards: dict[str, dict[str, Any]] = {}
        self._standards_aliases: dict[str, str] = {}
        self._load_all()
        self._initialized = True

    def _load_json_file(self, path: Path) -> Any:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            logger.warning("Knowledge base file does not exist: %s", path)
            return None
        except Exception as exc:
            logger.error("Failed to parse knowledge file %s: %s", path, exc)
            return None

    def _load_all(self) -> None:
        """Load all knowledge base components."""
        roles_path = self.base_path / "roles" / "roles.json"
        roles_data = self._load_json_file(roles_path)
        if roles_data and isinstance(roles_data, list):
            self._roles = roles_data
        elif roles_data and isinstance(roles_data, dict) and "roles" in roles_data:
            self._roles = roles_data["roles"]

        domains_path = self.base_path / "domains" / "domains.json"
        domains_data = self._load_json_file(domains_path)
        if domains_data and isinstance(domains_data, list):
            self._domains = domains_data
        elif domains_data and isinstance(domains_data, dict) and "domains" in domains_data:
            self._domains = domains_data["domains"]

        blueprints_path = self.base_path / "blueprints" / "intent_blueprints.json"
        bp_data = self._load_json_file(blueprints_path)
        if bp_data:
            self._blueprints = bp_data if isinstance(bp_data, list) else bp_data.get("blueprints", [])

        templates_path = self.base_path / "templates" / "output_formats.json"
        tpl_data = self._load_json_file(templates_path)
        if tpl_data:
            self._templates = tpl_data if isinstance(tpl_data, list) else tpl_data.get("formats", [])

        rules_path = self.base_path / "quality_rules" / "quality_rules.json"
        self._quality_rules = self._load_json_file(rules_path) or {}

        assumptions_path = self.base_path / "assumptions" / "default_assumptions.json"
        self._assumptions = self._load_json_file(assumptions_path) or {}

        # Load Concept Graphs (Stage C1)
        cg_dir = self.base_path / "concept_graphs"
        if cg_dir.exists():
            for p in cg_dir.glob("*.json"):
                data = self._load_json_file(p)
                if isinstance(data, dict):
                    stem = p.stem.lower()
                    if "topics" in data:
                        canonical = data.get("subject", stem)
                        self._concept_graphs[stem] = data
                        self._concept_aliases[stem] = canonical
                        self._concept_aliases[canonical.lower()] = canonical
                        for alias in data.get("aliases", []):
                            self._concept_aliases[alias.lower()] = canonical

        # Load Standards Registry (Stage D)
        std_dir = self.base_path / "standards"
        if std_dir.exists():
            for p in std_dir.glob("*.json"):
                data = self._load_json_file(p)
                if isinstance(data, dict):
                    stem = p.stem.lower()
                    canonical = data.get("subject", stem)
                    self._standards[stem] = data
                    self._standards_aliases[stem] = canonical
                    self._standards_aliases[canonical.lower()] = canonical
                    for alias in data.get("aliases", []):
                        self._standards_aliases[alias.lower()] = canonical

        logger.info(
            "Knowledge base loaded: %d roles, %d domains, %d blueprints, %d concept graphs, %d standards",
            len(self._roles),
            len(self._domains),
            len(self._blueprints),
            len(self._concept_graphs),
            len(self._standards),
        )

    def get_roles(self) -> list[dict[str, Any]]:
        return self._roles

    def get_domains(self) -> list[dict[str, Any]]:
        return self._domains

    def get_blueprints(self) -> list[dict[str, Any]]:
        return self._blueprints

    def get_templates(self) -> list[dict[str, Any]]:
        return self._templates

    def get_quality_rules(self) -> dict[str, Any]:
        return self._quality_rules

    def get_assumptions(self) -> dict[str, Any]:
        return self._assumptions

    def get_concept_graph(self, subject_or_alias: str) -> dict[str, Any] | None:
        """Resolve concept graph by canonical subject name or alias without hardcoding."""
        key = (subject_or_alias or "").strip().lower()
        if not key:
            return None
        # Direct key match
        if key in self._concept_graphs:
            return self._concept_graphs[key]
        # Alias lookup
        if key in self._concept_aliases:
            canonical = self._concept_aliases[key]
            for data in self._concept_graphs.values():
                if data.get("subject", "").lower() == canonical.lower():
                    return data
        # Search aliases by length descending with word-boundary matching
        sorted_aliases = sorted(self._concept_aliases.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            pattern = rf"(?:^|[^\w]){re.escape(alias)}(?:[^\w]|$)"
            if re.search(pattern, key, re.IGNORECASE):
                canonical = self._concept_aliases[alias]
                for data in self._concept_graphs.values():
                    if data.get("subject", "").lower() == canonical.lower():
                        return data
        return None

    def get_standards(self, subject_or_alias: str) -> dict[str, Any] | None:
        """Resolve standards entry from knowledge-base/standards/<subject>.json only."""
        key = (subject_or_alias or "").strip().lower()
        if not key:
            return None
        if key in self._standards:
            return self._standards[key]
        if key in self._standards_aliases:
            canonical = self._standards_aliases[key]
            for data in self._standards.values():
                if data.get("subject", "").lower() == canonical.lower():
                    return data
        sorted_aliases = sorted(self._standards_aliases.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            pattern = rf"(?:^|[^\w]){re.escape(alias)}(?:[^\w]|$)"
            if re.search(pattern, key, re.IGNORECASE):
                canonical = self._standards_aliases[alias]
                for data in self._standards.values():
                    if data.get("subject", "").lower() == canonical.lower():
                        return data
        return None

    def get_canonical_subject(self, subject_or_alias: str) -> str | None:
        """Retrieve canonical subject name for an alias if registered in knowledge base."""
        key = (subject_or_alias or "").strip().lower()
        if not key:
            return None
        if key in self._concept_aliases:
            return self._concept_aliases[key]
        sorted_aliases = sorted(self._concept_aliases.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            pattern = rf"(?:^|[^\w]){re.escape(alias)}(?:[^\w]|$)"
            if re.search(pattern, key, re.IGNORECASE):
                return self._concept_aliases[alias]
        return None

    def list_concept_graphs(self) -> dict[str, dict[str, Any]]:
        return self._concept_graphs

    def list_standards(self) -> dict[str, dict[str, Any]]:
        return self._standards
