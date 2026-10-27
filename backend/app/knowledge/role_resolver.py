"""Role Resolver Engine – resolves roles via pattern extraction, exact matching, semantic embeddings, and dynamic persona synthesis."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.entity_extractor import Entity
from app.nlp.role_extractor import RoleExtractor

logger = logging.getLogger("intentify.knowledge.role_resolver")


@dataclass
class RoleResult:
    """Resolved role details and expert persona attributes."""

    role_title: str
    expertise_areas: list[str]
    confidence: float
    is_dynamic: bool = False
    category: str = "General"
    prompt_style: str = "authoritative, technical, structured"
    typical_intents: list[str] = field(default_factory=lambda: ["create", "plan", "analyze"])
    seniority: str | None = None

    @property
    def role(self) -> str:
        return self.role_title


class RoleResolver:
    """Resolves user role input or extracts role from freeform text; falls back to dynamic expert persona synthesis."""

    def __init__(self, knowledge_manager: KnowledgeManager | None = None) -> None:
        self._km = knowledge_manager or KnowledgeManager()
        self._role_extractor = RoleExtractor()
        self._semantic_store: Any = None

    def _get_semantic_store(self) -> Any:
        if self._semantic_store is None:
            from app.knowledge.semantic_store import SemanticKnowledgeStore
            self._semantic_store = SemanticKnowledgeStore(knowledge_manager=self._km)
        return self._semantic_store

    def resolve(
        self,
        role_input: str | None = None,
        detail_text: str = "",
        entities: list[Entity] | None = None,
    ) -> RoleResult:
        """Resolve role using input string, detail text extraction, knowledge base matching, or dynamic persona generation."""
        target_role = (role_input or "").strip()
        seniority = None

        # 1. If role input is empty, extract role candidate from detail text
        if not target_role and detail_text:
            extracted = self._role_extractor.extract_primary_role(detail_text)
            if extracted:
                target_role = extracted
                seniority = self._role_extractor._detect_seniority(detail_text)

        # Detect seniority if role_input was provided
        if target_role and not seniority:
            seniority = self._role_extractor._detect_seniority(target_role)

        # 2. If still empty, infer from recognized entities or use fallback
        if not target_role:
            if entities:
                techs = [e.text for e in entities if e.label == "TECHNOLOGY"]
                if techs:
                    target_role = "Senior Software Architect"
                else:
                    target_role = "Principal Subject Matter Expert"
            else:
                target_role = "Principal Subject Matter Expert"

        # 3. Tier 1: Exact Title or Alias Match in Knowledge Base
        roles = self._km.get_roles()
        target_clean = re.sub(r"\b(?:senior|lead|principal|junior|chief|staff|expert|specialist)\b", "", target_role, flags=re.IGNORECASE).strip().lower()
        target_lower = target_role.lower()

        for r in roles:
            title = r.get("title", "")
            aliases = [a.lower() for a in r.get("aliases", [])]
            # Exact title or exact alias hit
            if target_lower == title.lower() or target_lower in aliases or target_clean == title.lower() or target_clean in aliases:
                final_title = f"{seniority} {title}" if seniority and seniority.lower() not in title.lower() else title
                return RoleResult(
                    role_title=final_title,
                    expertise_areas=r.get("expertise_areas", []),
                    confidence=0.98,
                    is_dynamic=False,
                    category=r.get("category", "General"),
                    prompt_style=r.get("prompt_style", "expert"),
                    typical_intents=r.get("typical_intents", ["create"]),
                    seniority=seniority,
                )

        # 4. Tier 2: Substring Partial Match in Knowledge Base
        for r in roles:
            title = r.get("title", "")
            if target_clean and (target_clean in title.lower() or any(target_clean in a for a in r.get("aliases", []))):
                final_title = f"{seniority} {title}" if seniority and seniority.lower() not in title.lower() else title
                return RoleResult(
                    role_title=final_title,
                    expertise_areas=r.get("expertise_areas", []),
                    confidence=0.88,
                    is_dynamic=False,
                    category=r.get("category", "General"),
                    prompt_style=r.get("prompt_style", "expert"),
                    typical_intents=r.get("typical_intents", ["create"]),
                    seniority=seniority,
                )

        # 5. Tier 3: Dense Vector Semantic Search
        try:
            store = self._get_semantic_store()
            semantic_matches = store.search_roles(target_role, top_k=1, min_score=0.55)
            if semantic_matches:
                top = semantic_matches[0]
                r = top.metadata
                matched_title = r.get("title", top.text)
                
                # If user provided a specific multi-word specialization and matched_title is a generic base role (e.g. "Space Lawyer" vs "Lawyer"),
                # preserve user's distinct specialized persona while inheriting the domain category and expertise!
                if target_role and len(target_role.split()) > len(matched_title.split()) and matched_title.lower() in target_role.lower():
                    final_title = target_role.title()
                else:
                    final_title = f"{seniority} {matched_title}" if seniority and seniority.lower() not in matched_title.lower() else matched_title

                expertise = list(r.get("expertise_areas", []))
                first_word = target_role.split()[0] if target_role else ""
                if first_word and first_word.lower() not in matched_title.lower():
                    expertise.insert(0, f"{first_word.capitalize()} specialization & domain governance")

                return RoleResult(
                    role_title=final_title,
                    expertise_areas=expertise,
                    confidence=round(top.score, 2),
                    is_dynamic=False,
                    category=r.get("category", "General"),
                    prompt_style=r.get("prompt_style", "expert"),
                    typical_intents=r.get("typical_intents", ["create"]),
                    seniority=seniority,
                )
        except Exception as exc:
            logger.debug("Semantic role lookup skipped: %s", exc)

        # 6. Tier 4: Dynamic Expert Persona Synthesis for Unknown / Novel Roles
        return self._generate_dynamic_role(target_role, seniority=seniority)

    def _generate_dynamic_role(self, raw_role: str, seniority: str | None = None) -> RoleResult:
        """Synthesize an authoritative, domain-specialized persona for novel or emerging roles."""
        clean_title = raw_role.strip().title()

        # Add expert suffix if role is solely a topic name
        if not any(clean_title.endswith(sfx) for sfx in ["Expert", "Specialist", "Architect", "Lead", "Strategist", "Scientist", "Engineer", "Analyst", "Director", "Officer", "Consultant"]):
            clean_title = f"{clean_title} Specialist"

        if seniority and seniority.lower() not in clean_title.lower():
            clean_title = f"{seniority} {clean_title}"

        # Extract primary field nouns
        field_name = re.sub(r"\b(?:Specialist|Expert|Architect|Lead|Senior|Principal|Chief|Junior|Officer)\b", "", clean_title).strip()
        if not field_name:
            field_name = clean_title

        expertise = [
            f"End-to-end {field_name} methodologies, standards, and execution",
            f"Advanced domain decomposition and best practices in {field_name}",
            "Rigorous risk mitigation, edge case handling, and quality assurance",
            "Strategic advisory, architectural blueprint formulation, and operational guidance",
        ]

        return RoleResult(
            role_title=clean_title,
            expertise_areas=expertise,
            confidence=0.80,
            is_dynamic=True,
            category="Custom / Emerging Industry",
            prompt_style="authoritative, deeply analytical, rigorous, actionable",
            typical_intents=["create", "design", "plan", "analyze"],
            seniority=seniority,
        )
