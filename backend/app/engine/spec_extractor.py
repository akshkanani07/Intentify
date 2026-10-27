"""Prompt Specification Extractor – Translates normalized input into a structured Pydantic v2 PromptSpec."""

from __future__ import annotations

import logging
import re
from typing import Any

from pydantic import BaseModel, Field

from app.engine.normalizer import InputNormalizer
from app.knowledge.domain_resolver import DomainResolver
from app.knowledge.knowledge_manager import KnowledgeManager
from app.nlp.audience_detector import AudienceDetector
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.goal_extractor import GoalExtractor
from app.nlp.language_detector import LanguageDetector
from app.nlp.requirement_extractor import RequirementExtractor
from app.nlp.role_alignment_engine import RoleAlignmentEngine

logger = logging.getLogger("intentify.engine.spec_extractor")


class PromptSpec(BaseModel):
    """Structured Pydantic v2 specification representing the user's intent and operational boundaries."""

    action: str = Field(..., description="Primary action verb (e.g. Learn, Build, Plan, Debug, Architect, Analyze)")
    product_name: str | None = Field(default=None, description="Explicit product or project name")
    subject: str = Field(..., description="Canonical target object or topic (resolved via KnowledgeBase)")
    object_subject: str = Field(default="", description="Alias/backward compatibility for subject")
    requester: str = Field(default="Software Developer", description="Role/identity of the person making the request")
    audience: str = Field(..., description="Target audience persona")
    audience_source: str = Field(default="assumed", description="stated | assumed")
    proficiency: str = Field(..., description="Audience technical proficiency level")
    proficiency_signals: list[str] = Field(default_factory=list, description="Explicit signals used to determine proficiency")
    contract: str = Field(default="build_app", description="build_tool | build_app | learn | debug | plan | business | event | write | analyze")
    domain: str = Field(..., description="Primary domain category (domain_parent)")
    domain_parent: str = Field(default="", description="Parent domain category")
    domain_child: str = Field(default="", description="Specialized child domain")
    child_domain: str = Field(default="", description="Specialized child domain alias")
    sub_domains: list[str] = Field(default_factory=list, description="Specialized sub-domains")
    persona_role: str = Field(..., description="AI expert persona aligned with domain and goal")
    deliverable: str = Field(..., description="Primary concrete deliverable")
    format: str = Field(..., description="Required output format")
    input_language: str = Field(default="English", description="Detected language of user input")
    output_language: str = Field(default="English", description="Target response language")
    tone: str = Field(default="supportive, step-by-step", description="Tone of the response")
    constraints: list[str] = Field(default_factory=list, description="Negative or operational constraints explicitly stated")
    decisions_needed: list[str] = Field(default_factory=list, description="Alternatives left undecided in request")
    entities: list[dict[str, Any]] = Field(default_factory=list, description="Named entities extracted from input")
    missing_fields: list[str] = Field(default_factory=list, description="Ambiguities or parameters needing assumptions")
    confidence: float = Field(default=0.90, description="Overall extraction confidence")
    field_confidence: dict[str, float] = Field(default_factory=dict, description="Confidence per field")
    engine_mode: str = Field(default="rules_fallback", description="Inference engine execution mode")
    content_source: str = Field(default="concept_graph", description="concept_graph | generated | derived")
    reviewed: bool = Field(default=False, description="Whether the knowledge content has been human-reviewed")
    raw_input: str = Field(default="", description="Original raw user input text")

    def model_post_init(self, __context: Any) -> None:
        if not self.object_subject:
            self.object_subject = self.subject
        if not self.domain_parent:
            self.domain_parent = self.domain
        if not self.domain_child and self.child_domain:
            self.domain_child = self.child_domain
        elif not self.child_domain and self.domain_child:
            self.child_domain = self.domain_child


class SpecExtractor:
    """Extracts a rigorous PromptSpec from raw or normalized human thought adhering to S2 requirements."""

    def __init__(self, km: KnowledgeManager | None = None) -> None:
        self.km = km or KnowledgeManager()
        self.normalizer = InputNormalizer()
        self.lang_detector = LanguageDetector()
        self.goal_extractor = GoalExtractor()
        self.domain_resolver = DomainResolver(knowledge_manager=self.km)
        self.role_aligner = RoleAlignmentEngine()
        self.audience_detector = AudienceDetector()
        self.entity_extractor = EntityExtractor()
        self.req_extractor = RequirementExtractor()

    def _extract_product_name(self, raw_text: str) -> str | None:
        """Extract explicit product_name strictly from naming patterns. Never return raw sentence."""
        # 1. Explicit naming phrase: 'name is X', 'called X', 'named X', 'nu naam X', 'ka naam X'
        p1 = re.search(
            r'(?:(?:which\s+)?name\s+is\s+|(?:\bis\s+)?called\s+|(?:\bis\s+)?named\s+|(?:nu\s+|ka\s+)?(?:naam|નામ|नाम)\s*(?:che|hai|is)?\s*[:\s]*)(?:"([^"]+)"|\'([^\']+)\'|([A-Za-z0-9_-]+))',
            raw_text,
            re.IGNORECASE,
        )
        if p1:
            val = p1.group(1) or p1.group(2) or p1.group(3)
            if val:
                val = val.strip(".,;:?!'\" ")
                if val and len(val.split()) <= 4 and val.lower() not in ("a", "an", "the", "website", "app", "tool", "project"):
                    return val

        # 2. Quoted word following a product descriptor keyword
        p2 = re.search(
            r'\b(?:app|tool|project|product|service|system|website|platform)\b\s*(?:called|named)?\s*["\']([A-Za-z0-9_-]{2,30})["\']',
            raw_text,
            re.IGNORECASE,
        )
        if p2:
            val = p2.group(1).strip(".,;:?!'\" ")
            if val and val.lower() not in ("a", "an", "the", "website", "app", "tool", "project"):
                return val

        return None

    def _clean_subject_from_product_name(self, subject: str, product_name: str | None) -> str:
        """Remove product_name and its naming clause from subject so they are never merged."""
        if not product_name:
            return subject

        cleaned = subject
        # Remove clauses like ', which name is "taskflow"' or 'named taskflow'
        cleaned = re.sub(
            rf'(?:,\s*)?(?:which\s+)?name\s+is\s+["\']?{re.escape(product_name)}["\']?',
            '',
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            rf'(?:,\s*)?(?:named|called)\s+["\']?{re.escape(product_name)}["\']?',
            '',
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            rf'(?:nu\s+|ka\s+)?(?:naam|નામ|नाम)\s*(?:che|hai|is)?\s*["\']?{re.escape(product_name)}["\']?',
            '',
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(rf'["\']{re.escape(product_name)}["\']', '', cleaned)
        cleaned = re.sub(rf'\b{re.escape(product_name)}\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip(" ,.-")
        return cleaned or "Application"

    def _determine_contract(self, action: str, domain: str, raw_text: str) -> str:
        """Determine contract from knowledge-base/contracts/: build_tool | build_app | learn | debug | plan | business | event | write | analyze."""
        act = action.lower()
        dom = domain.lower()
        txt = raw_text.lower()

        # 1. Learning & Education
        if act in ("learn", "study", "teach") or any(k in txt for k in ["learn", "study", "tutorial", "curriculum", "shikhvu", "sikho", "sikhna", "seekhna", "શીખવું"]):
            return "learn"

        # 2. Debugging & RCA
        if act in ("debug", "fix", "troubleshoot") or any(k in txt for k in ["debug", "fix", "error", "nullpointer", "exception", "segfault", "deadlock"]):
            return "debug"

        # Event Planning (Strictly non-software events)
        is_software_event = bool(re.search(r"\b(?:event-driven|events/sec|event stream|event sourcing|event broker|event queue|event listener|event loop|events per second)\b", txt))
        if not is_software_event:
            if any(k in dom for k in ["event planning", "wedding", "hospitality"]) or any(k in txt for k in ["wedding", "summit", "gala", "sangeet", "reception", "party", "conference", "banquet", "celebrity artist", "stage lighting", "choreography"]):
                return "event"
            if re.search(r"\b(?:plan|organize|host)\s+(?:an?\s+)?event\b", txt):
                return "event"

        # If management application or web platform described as tool
        if any(k in txt for k in ["project management", "task management", "management tool", "productivity tool"]):
            return "build_app"

        # 3. Building CLI Tools, Utilities, Scripts, Libraries
        if re.search(r"\b(?:cli|script|scripts|utility|utilities|library|libraries|microservice|microservices|sdk|sdks|linter|parser)\b", txt):
            return "build_tool"
        if re.search(r"\b(?:dev\s+tool|developer\s+tool|cli\s+tool)\b", txt):
            return "build_tool"
        if re.search(r"\btool\b", txt) and not any(k in txt for k in ["project", "management", "sound", "lighting", "event"]):
            return "build_tool"

        # 4. Building Applications (Websites, Apps, Marketplaces, Platforms, Portals)
        if any(k in txt for k in ["website", "marketplace", "platform", "portal", "dashboard", "web app", "app", "application", "saas", "વેબસાઇટ", "વેબસાટ", "वेबसाइट"]):
            return "build_app"

        # 5. Creative Writing & Literature
        if act in ("write", "compose", "draft", "author") or any(k in dom for k in ["writing", "creative", "fiction", "novel", "poetry", "literature", "arts"]) or any(k in txt for k in ["novel", "chapter", "fiction", "poetry", "story", "copywriting", "screenplay"]):
            return "write"

        # 7. Business & Financial Strategy
        if any(k in dom for k in ["business", "marketing", "finance", "strategy", "retail", "real estate"]) or any(k in txt for k in ["franchise", "business", "gtm", "marketing", "valuation", "investment", "dcf"]):
            return "business"

        # 8. Analysis & Audit
        if act in ("analyze", "audit", "evaluate", "assess") or any(k in dom for k in ["compliance", "audit", "research"]):
            return "analyze"

        # 9. Planning & Roadmaps
        if act in ("plan", "roadmap") or "roadmap" in txt:
            return "plan"

        return "build_app"

    def _extract_decisions_needed(self, text: str) -> list[str]:
        """Extract undecided alternatives like 'REST or GraphQL', 'Postgres or Mongo'."""
        decisions: list[str] = []
        matches = re.findall(r'\b([A-Za-z0-9#+.-]+)\s+or\s+([A-Za-z0-9#+.-]+)\b', text, re.IGNORECASE)
        tech_words = {"rest", "graphql", "postgres", "mongodb", "mysql", "sql", "nosql", "vue", "react", "angular", "aws", "gcp", "azure", "docker", "kubernetes", "fastapi", "django", "flask"}
        for a, b in matches:
            if a.lower() in tech_words or b.lower() in tech_words:
                decisions.append(f"Architecture decision required: select {a} vs {b}")
        return decisions

    def extract(
        self,
        text: str,
        role_hint: str = "",
        domain_hint: str = "",
        constraints_hint: list[str] | None = None,
        language_hint: str = "",
    ) -> PromptSpec:
        """Process input text into a complete PromptSpec fulfilling S2 requirements."""
        raw_text = (text or "").strip()
        lower_raw = raw_text.lower()
        norm_result = self.normalizer.normalize(raw_text)
        normalized_text = norm_result.core_content
        script = norm_result.primary_script
        norm_lang = norm_result.detected_language

        # 1. Language Detection & Mirroring
        detected_lang_res = self.lang_detector.detect(raw_text)
        primary_lang = detected_lang_res.language
        if norm_lang == "gu" or script == "gujarati":
            primary_lang = "Gujarati"
        elif norm_lang == "hi" or script == "devanagari":
            primary_lang = "Hindi"

        if language_hint and language_hint.strip() and language_hint.strip().lower() not in ("auto", "none", "default"):
            output_lang = language_hint.strip()
        elif norm_lang == "gu" or script == "gujarati" or primary_lang.lower() == "gujarati":
            output_lang = "Gujarati"
        elif norm_lang == "hi" or script == "devanagari" or primary_lang.lower() == "hindi":
            output_lang = "Hindi"
        else:
            output_lang = "English"

        # 2. Product Name Extraction (S2: Taken only from explicit patterns, never raw sentence)
        product_name = self._extract_product_name(raw_text)

        # 3. Goal & Subject Extraction
        goal_res = self.goal_extractor.extract_goal(
            detail=normalized_text,
            role_input=role_hint,
        )
        action = goal_res.action or "Build"
        if re.search(r"\b(?:write|author|draft|compose)\b", lower_raw) and not any(k in lower_raw for k in ["code", "script", "test", "platform", "app"]):
            action = "Write" 
        raw_subject = goal_res.target_subject or ""

        # Clean subject from product_name
        raw_subject = self._clean_subject_from_product_name(raw_subject, product_name)

        if not raw_subject or raw_subject.lower() in ["item", "target", "system", "application"]:
            cleaned_tokens = [
                t for t in norm_result.tokens
                if t.lower() not in {"want", "learn", "build", "create", "make", "fix", "mare", "mujhe", "joiye", "karvu"}
            ]
            raw_subject = " ".join(cleaned_tokens[:4]).title() if cleaned_tokens else "Target Project"

        clean_subject = re.sub(r"^(?:learn|study|teach|build|create|fix|debug)\s+", "", raw_subject, flags=re.IGNORECASE).strip()
        if not clean_subject:
            clean_subject = raw_subject

        clean_subject = self._clean_subject_from_product_name(clean_subject, product_name)

        # 4. Canonical Subject Resolution
        lower_raw = raw_text.lower()
        is_learning = (
            action.lower() in ["learn", "study", "teach", "explain"]
            or (
                action.lower() not in ["analyze", "debug"]
                and (
                    bool(re.search(r"\b(?:learn|study|curriculum|teach|tutorial|lrn|shikhvu|shikhavu|sikho|sikhvu|sikhna|seekhna|sikh|seekh)\b", lower_raw))
                    or any(w in lower_raw for w in ["શીખવું", "શીખવ", "સીખના", "સીખવું", "सीखना", "सीखनी", "सीखें", "पढ़ना", "पढ़ाई", "पढ़ना", "पढ़ाई"])
                )
            )
        )
        is_debug = not is_learning and (
            action.lower() in ("debug", "fix") or bool(re.search(r"\b(?:debug|fix|troubleshoot|diagnose|segfault|deadlock|memory\s+leak|nullpointer\w*)\b", lower_raw))
        )

        if is_debug:
            canonical_subject = clean_subject
        elif len(clean_subject.split()) > 3 and any(w in clean_subject.lower() for w in ["using", "with", "and", "in"]):
            canonical_subject = clean_subject
        else:
            canonical_subject = self.km.get_canonical_subject(clean_subject) or self.km.get_canonical_subject(raw_text) or clean_subject

        # Ensure product_name did not leak into canonical_subject
        canonical_subject = self._clean_subject_from_product_name(canonical_subject, product_name)

        cg = self.km.get_concept_graph(canonical_subject)
        content_source = "concept_graph" if cg else "derived"
        reviewed = cg.get("reviewed", False) if cg else False

        # 5. Domain Resolution
        resolved_domain = self.domain_resolver.resolve(text=normalized_text)
        if is_debug:
            domain = "Debugging"
            sub_domains = ["Root-Cause Diagnostic Analysis", "System Trace Inspection", "Automated Regression Testing", "Defect Isolation & Patch Verification"]
        elif is_learning and ("Education" in resolved_domain.domain or resolved_domain.domain == "Programming Education"):
            domain = resolved_domain.domain
            sub_domains = resolved_domain.sub_domains or []
        else:
            domain = cg.get("domain", resolved_domain.domain) if cg else resolved_domain.domain
            sub_domains = resolved_domain.sub_domains or []

        child_domain = getattr(resolved_domain, "child_domain", "")

        # 6. Requester vs Audience Separation (S2 Rule)
        # Requester is who makes the request; Audience is who will consume/use the result
        if role_hint and role_hint.strip():
            requester = role_hint.strip()
        else:
            # Check for self-description in raw text ("I am a teacher", "As a doctor")
            self_role_m = re.search(r"\b(?:i\s+am\s+a|as\s+a)\s+([A-Za-z0-9\s]+?)(?:,|\s+and|\s+who|\s+want|\s+i|\.|$)", raw_text, re.IGNORECASE)
            if self_role_m:
                requester = self_role_m.group(1).strip().title()
            elif is_learning:
                requester = "Student / Learner"
            elif is_debug:
                requester = "Software Engineer / System Maintainer"
            elif any(k in domain.lower() for k in ["event", "wedding"]):
                requester = "Event Host / Client"
            elif any(k in domain.lower() for k in ["business", "strategy", "finance"]):
                requester = "Business Stakeholder / Founder"
            else:
                requester = "Software Developer"

        # Audience determination: Stated vs Assumed
        stated_aud_m = re.search(r"\bfor\s+([A-Za-z0-9\s,&-]+?)(?:\.|$|,|\s+with|\s+and|\s+which)", raw_text, re.IGNORECASE)
        if stated_aud_m and len(stated_aud_m.group(1).split()) <= 5:
            candidate_aud = stated_aud_m.group(1).strip().title()
            if candidate_aud.lower() not in ("retail", "production", "high availability", "speed", "performance", "sale", "rent"):
                audience = candidate_aud
                audience_source = "stated"
            else:
                audience_source = "assumed"
                audience = None
        else:
            audience_source = "assumed"
            audience = None

        if not audience:
            audience_source = "assumed"
            if is_learning:
                audience = "Students & Learners"
            elif is_debug:
                audience = "Software Engineers & Maintainers"
            elif "wedding" in domain.lower() or "wedding" in raw_text.lower():
                audience = "Wedding Guests & Families"
            elif any(k in domain.lower() for k in ["event", "hospitality"]):
                audience = "Event Attendees & Participants"
            elif any(k in domain.lower() for k in ["business", "strategy"]):
                audience = "Executive Stakeholders & Investors"
            elif any(k in (role_hint or "").lower() for k in ["architect", "engineer", "developer"]):
                audience = "Software Engineers & Architects"
            else:
                audience = "End Users & Platform Clients"

        # 7. Proficiency & Explicit Signals (S2 Rule)
        combined_eval_text = f"{raw_text} {normalized_text}".strip()
        audience_res = self.audience_detector.detect(
            text=combined_eval_text,
            domain_hint=domain,
            role_hint=role_hint,
            action_hint=action,
        )

        if is_learning:
            if action.lower() != "explain":
                action = "Learn"

        is_beginner_role = bool(role_hint and any(b in role_hint.lower() for b in ["student", "beginner", "intern", "novice", "learner"]))
        is_beginner_text = bool(any(b in lower_raw for b in ["like i am 10", "from scratch", "from basics", "for beginners", "beginner", "starter", "novice"]))

        proficiency_signals: list[str] = []
        if is_learning:
            if audience_res.explicit_self_seniority:
                proficiency = audience_res.experience_level
                proficiency_signals.append("explicit_self_seniority")
                tone = "concise, technical"
            elif is_beginner_role or is_beginner_text:
                proficiency = "Novice / Beginner"
                proficiency_signals.append("action_learn_default")
                tone = "supportive, step-by-step"
            elif any(w in lower_raw for w in ["distributed", "zero-trust", "concurrency", "low-latency", "microservices", "lock-free"]):
                proficiency = "Intermediate / Practitioner"
                proficiency_signals.append("architecture_vocabulary_learning")
                tone = "supportive, step-by-step"
            else:
                proficiency = "Novice / Beginner"
                proficiency_signals.append("action_learn_default")
                tone = "supportive, step-by-step"
        else:
            if is_beginner_role or is_beginner_text:
                proficiency = "Novice / Beginner"
                proficiency_signals.append("explicit_beginner_signal")
                tone = "supportive, step-by-step"
            elif audience_res.explicit_self_seniority:
                proficiency = audience_res.experience_level
                proficiency_signals.append("explicit_self_seniority")
            elif is_debug and any(k in lower_raw for k in ["segfault", "deadlock", "leak", "oom", "timeout", "kill", "exhaustion", "504"]):
                proficiency = "Advanced / Senior"
                proficiency_signals.append("critical_fault_complexity")
            elif any(k in lower_raw for k in ["distributed", "raft", "paxos", "sharding", "multi-region", "zero-trust", "ebpf"]):
                proficiency = "Advanced / Senior"
                proficiency_signals.append("distributed_systems_lexicon")
            else:
                proficiency = audience_res.experience_level
                proficiency_signals.append("domain_baseline")

            if proficiency.lower() in ("novice / beginner", "beginner", "novice"):
                tone = "supportive, step-by-step"
            elif any(k in proficiency.lower() for k in ("expert", "senior", "principal", "architect", "lead")):
                tone = "concise, technical"
            else:
                tone = "practical, structured"

        # 8. Persona Role Synthesis
        if is_learning:
            persona_role = f"{canonical_subject} Instructor & Curriculum Mentor"
        else:
            role_alignment = self.role_aligner.align_role(
                requested_role=role_hint or requester,
                detail_text=normalized_text,
                detected_domain=domain,
                intent=action.lower(),
            )
            persona_role = role_alignment.final_role or f"Principal {canonical_subject} Specialist"

        # 9. Contract Determination
        contract = self._determine_contract(action, domain, raw_text)

        # 10. Deliverable & Format Determination
        if is_learning:
            deliverable = f"Curriculum & Hands-On Practice Roadmap for {canonical_subject}"
            output_format = "Pedagogical Markdown with Concept Explanations and Step-by-Step Exercises"
        elif action.lower() in ("debug", "fix"):
            deliverable = f"Root Cause Analysis (RCA) & Resolution Patch for {canonical_subject}"
            output_format = "Diagnostic Technical Report with Decompilation and Regression Tests"
        elif contract == "event":
            if "wedding" in canonical_subject.lower() or "wedding" in raw_text.lower():
                deliverable = f"Comprehensive Wedding Execution Plan for {canonical_subject}"
            else:
                deliverable = f"Comprehensive Event Execution Plan for {canonical_subject}"
            output_format = "Structured Markdown Document with Event Timeline and Vendor Specifications"
        elif contract == "business":
            deliverable = f"Strategic Business Expansion Blueprint for {canonical_subject}"
            output_format = "Structured Markdown Document with Operational Framework and Financials"
        elif contract == "build_tool":
            deliverable = f"Production CLI / Tool Specification for {canonical_subject}"
            output_format = "Structured Technical Specification with Command Syntax and Interfaces"
        else:
            deliverable = f"Production Architecture Specification for {canonical_subject}"
            output_format = "Structured Markdown Document with System Topology and Specifications"

        # 11. Entities & Decisions Needed
        extracted_entities = self.entity_extractor.extract(raw_text)
        entities_data = [
            {"text": e.text, "label": e.label, "confidence": getattr(e, "confidence", 0.9)}
            for e in extracted_entities
        ]

        extracted_reqs = self.req_extractor.extract(raw_text)
        constraints = list(extracted_reqs.constraints or [])
        if constraints_hint:
            for c in constraints_hint:
                if c not in constraints:
                    constraints.append(c)

        decisions_needed = self._extract_decisions_needed(raw_text)

        # 12. Missing Fields
        missing_fields: list[str] = []
        if is_learning:
            missing_fields.append("Weekly study commitment timeframe")
        elif "saas" in canonical_subject.lower() or "website" in canonical_subject.lower():
            missing_fields.append("Authentication and security authorization model")

        field_confidence = {
            "action": 0.95,
            "subject": 0.92,
            "product_name": 0.98 if product_name else 1.0,
            "domain": 0.94,
            "requester": 0.90,
            "audience": 0.90,
            "proficiency": 0.95,
            "contract": 0.94,
            "language": 0.98,
        }

        return PromptSpec(
            action=action,
            product_name=product_name,
            subject=canonical_subject,
            object_subject=canonical_subject,
            requester=requester,
            audience=audience,
            audience_source=audience_source,
            proficiency=proficiency,
            proficiency_signals=proficiency_signals,
            contract=contract,
            domain=domain,
            domain_parent=domain,
            domain_child=child_domain,
            child_domain=child_domain,
            sub_domains=sub_domains,
            persona_role=persona_role,
            deliverable=deliverable,
            format=output_format,
            input_language=primary_lang,
            output_language=output_lang,
            tone=tone,
            constraints=constraints,
            decisions_needed=decisions_needed,
            entities=entities_data,
            missing_fields=missing_fields,
            confidence=0.94,
            field_confidence=field_confidence,
            engine_mode="rules_fallback",
            content_source=content_source,
            reviewed=reviewed,
            raw_input=raw_text,
        )
