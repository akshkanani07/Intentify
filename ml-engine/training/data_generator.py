"""Synthetic Data Generation Pipeline for 5000+ multilingual training examples across Intent, Domain, Role, and Requirements."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

from app.knowledge.knowledge_manager import KnowledgeManager

logger = logging.getLogger("intentify.ml.data_generator")


class SyntheticDataGenerator:
    """Generates synthetic datasets for training local classifiers across all 4 modeling tasks:

    1. Intent Classification (13 intents)
    2. Domain Classification (88 domains)
    3. Role Classification (121 roles)
    4. Requirement Extraction (11 dimensions)
    """

    INTENTS = [
        "create", "write", "generate", "plan", "analyze", "explain",
        "compare", "translate", "research", "design", "debug", "improve", "decide"
    ]

    # Multilingual templates per intent
    INTENT_TEMPLATES: dict[str, list[str]] = {
        "create": [
            "Build a scalable {tech} system for {task}",
            "Implement a clean {task} backend using {tech}",
            "Develop a high-performance {task} microservice",
            "Create a production-ready {tech} architecture for {task}",
            "ek {tech} par {task} banavvu che",
            "{tech} aur {task} ke liye naya system banao",
            "Construir un sistema de {task} usando {tech}",
            "Créer un service de {task} avec {tech}",
        ],
        "write": [
            "Draft an executive summary about {task} for leadership",
            "Write comprehensive technical documentation for {tech}",
            "Compose a detailed whitepaper covering {task}",
            "Write an in-depth article analyzing {task}",
            "{task} mate detailed lekh lakho",
            "{task} par vishleshanatmak lekh likho",
            "Redactar un documento técnico sobre {task}",
            "Rédiger un rapport complet sur {task}",
        ],
        "generate": [
            "Generate a synthetic dataset of 500 {task} test cases",
            "Synthesize mock JSON data for {tech} testing",
            "Brainstorm a list of 20 creative ideas for {task}",
            "Produce an exhaustive test matrix for {task}",
            "{task} mate alag alag ideas ni yadi banavo",
            "{task} ke liye sample data generate karo",
            "Generar un conjunto de datos de prueba para {task}",
            "Générer une liste d'idées pour {task}",
        ],
        "plan": [
            "Formulate a 12-month engineering roadmap for {task}",
            "Plan a phase-by-phase migration to {tech}",
            "Draft a detailed rollout timeline for {task}",
            "Coordinate destination wedding in {location} with budget {budget}",
            "{location} ma destination wedding mate complete timeline ayojan banavo",
            "Agli timahi ke liye {task} ki yojana taiyar karo",
            "Planificar una hoja de ruta para {task}",
            "Planifier le déploiement de {tech}",
        ],
        "analyze": [
            "Conduct an in-depth audit of {task} performance metrics",
            "Analyze throughput telemetry and latency bottlenecks in {tech}",
            "Perform a security vulnerability review for {task}",
            "Evaluate operational query performance for {task}",
            "{tech} na performance metrics ni tapas karo",
            "{task} ke data ka gahan vishleshan karo",
            "Analizar los cuellos de botella en {tech}",
            "Analyser les métriques de performance de {task}",
        ],
        "explain": [
            "Explain how {tech} handles concurrent transactions step by step",
            "Break down the fundamental architecture of {tech} for beginners",
            "Clarify the mathematical mechanisms behind {task}",
            "Provide a tutorial on how to configure {tech} for {task}",
            "{tech} na basic concepts saral bhasha ma samjavo",
            "{task} kaise kaam karta hai vistaar se samjhao",
            "Explicar el funcionamiento interno de {tech}",
            "Expliquer comment fonctionne {tech}",
        ],
        "compare": [
            "Compare {tech} versus {tech2} across throughput, latency, and cost",
            "Provide an objective benchmark comparing {tech} and {tech2}",
            "Evaluate pros and cons of {tech} vs {tech2} for {task}",
            "Construct a comparison matrix between {tech} and {tech2}",
            "{tech} ane {tech2} ni sarkhamani kari pro cons janavo",
            "{tech} aur {tech2} ke beech me tulna karke batao",
            "Comparar {tech} frente a {tech2} para {task}",
            "Comparer {tech} et {tech2} pour {task}",
        ],
        "translate": [
            "Translate this technical manual from English to Spanish and German",
            "Localize this onboarding workflow for users in {location}",
            "Transliterate and convert customer support scripts into French",
            "Provide bilingual English and Hindi translations of this policy",
            "Aa dastavej nu Gujarati ma bhashantar karo",
            "Is niyamavali ka Hindi me anuvad karo",
            "Traducir este documento al español con precisión técnica",
            "Traduire cette documentation en français",
        ],
        "research": [
            "Investigate state-of-the-art literature on {task}",
            "Survey cutting-edge academic paradigms in {tech}",
            "Explore recent empirical breakthroughs in {task}",
            "Review peer-reviewed findings on {task} efficiency",
            "{task} par navin sanshodhan no abhyas karo",
            "{task} ke naye shodh patro ka adhyayan karo",
            "Investigar el estado del arte en {task}",
            "Rechercher les avancées récentes sur {task}",
        ],
        "design": [
            "Design the system architecture and schema for {task}",
            "Create a responsive UI wireframe and layout for {task}",
            "Architect the relational database model for {tech}",
            "Formulate the high-level system topology for {task}",
            "{task} mate visual schema ane architecture design karo",
            "{task} ke liye system design aur flow chart banao",
            "Diseñar el esquema de arquitectura para {task}",
            "Concevoir l'architecture système pour {task}",
        ],
        "debug": [
            "Fix the {issue} bug occurring in {tech}",
            "Troubleshoot stack trace exception when {task} fails",
            "Debug memory leak and crash in {tech} service",
            "Resolve race condition in {task} handler",
            "{tech} ma avti {issue} bhul sudharo",
            "{tech} me {issue} error ko theek karo",
            "Depurar el fallo de {issue} en {tech}",
            "Déboguer l'erreur {issue} dans {tech}",
        ],
        "improve": [
            "Optimize latency in {tech} to achieve sub-50ms execution",
            "Refactor legacy {task} implementation for maintainability",
            "Scale the throughput of {tech} by 300%",
            "Enhance memory efficiency during {task}",
            "{tech} ni karyakshamta ane speed sudharo",
            "{task} ke performance ko behtar aur tez banao",
            "Optimizar el rendimiento de {tech} para {task}",
            "Améliorer les performances de {tech}",
        ],
        "decide": [
            "Help me decide whether to use {tech} or {tech2} for {task}",
            "Recommend the best architectural path for {task}",
            "Synthesize an Architectural Decision Record choosing {tech}",
            "Deliver an authoritative verdict between {tech} and {tech2}",
            "{task} mate {tech} ke {tech2} ma thi su pasand karvu",
            "{task} ke liye kaun sa tool chuno {tech} ya {tech2}",
            "Decidir entre {tech} y {tech2} para nuestro proyecto",
            "Décider quelle technologie choisir entre {tech} et {tech2}",
        ],
    }

    TECHS = [
        "PostgreSQL", "FastAPI", "React", "Docker", "Redis", "Kafka", "Kubernetes",
        "Next.js", "MongoDB", "GraphQL", "PyTorch", "Go", "Rust", "TypeScript",
        "AWS Lambda", "Elasticsearch", "Cassandra", "Nginx", "RabbitMQ", "Django"
    ]

    TASKS = [
        "authentication", "payment processing", "data ingestion", "search indexing",
        "rate limiting", "event streaming", "user onboarding", "order fulfillment",
        "machine learning inference", "real-time analytics", "telemetry collection"
    ]

    ISSUES = [
        "deadlock", "null pointer exception", "race condition", "timeout",
        "out of memory error", "connection pool exhaustion", "segmentation fault", "401 unauthorized"
    ]

    LOCATIONS = ["Udaipur", "Mumbai", "San Francisco", "Tokyo", "London", "Berlin", "Singapore", "New York"]
    BUDGETS = ["$10,000", "50 lakh", "₹25 Lakh", "$50k", "€15,000", "$100,000"]
    DEADLINES = ["within 3 days", "within 2 weeks", "by end of quarter", "in 48 hours", "within 1 month"]
    AUDIENCES = ["developers", "executives", "beginners", "wedding_guests", "clients"]
    FORMATS = ["Detailed Technical Response", "Comparison Matrix Table", "Step-by-Step Implementation Guide", "Strict JSON Schema & Payload", "Event Master Coordination Plan"]

    def __init__(self, knowledge_manager: KnowledgeManager | None = None) -> None:
        self._km = knowledge_manager or KnowledgeManager()

    def generate_intent_dataset(self, num_samples: int = 5200) -> list[dict[str, Any]]:
        """Generate 5000+ synthetic samples for 13-class intent classification."""
        samples: list[dict[str, Any]] = []
        samples_per_intent = max(1, num_samples // len(self.INTENTS))

        sample_idx = 0
        for intent in self.INTENTS:
            templates = self.INTENT_TEMPLATES.get(intent, ["Execute {task} using {tech}"])
            for _ in range(samples_per_intent):
                tpl = random.choice(templates)
                tech1 = random.choice(self.TECHS)
                tech2 = random.choice([t for t in self.TECHS if t != tech1])
                text = tpl.format(
                    tech=tech1,
                    tech2=tech2,
                    task=random.choice(self.TASKS),
                    issue=random.choice(self.ISSUES),
                    location=random.choice(self.LOCATIONS),
                    budget=random.choice(self.BUDGETS),
                )
                samples.append({
                    "id": f"intent_{sample_idx:06d}",
                    "text": text,
                    "label": intent,
                })
                sample_idx += 1

        random.shuffle(samples)
        return samples

    def generate_domain_dataset(self, num_samples: int = 5280) -> list[dict[str, Any]]:
        """Generate 5000+ synthetic samples across all catalog domains."""
        domains = self._km.get_domains()
        if not domains:
            domains = [{"name": "Software Development", "category": "Technology", "keywords": ["code", "software"]}]

        samples: list[dict[str, Any]] = []
        samples_per_domain = max(1, num_samples // len(domains))

        sample_idx = 0
        for d in domains:
            d_name = d.get("name", "General")
            category = d.get("category", "General")
            keywords = d.get("keywords", ["general"])
            sub_domains = d.get("sub_domains", [d_name])

            templates = [
                "Formulate an industry standard solution for {keyword} in {sub_domain}",
                "Review operational guidelines and best practices for {sub_domain}",
                "Develop an end-to-end framework focusing on {keyword} in {domain}",
                "Analyze regulatory compliance and risk factors in {sub_domain}",
                "Create a high-impact strategy incorporating {keyword} for {domain}",
            ]

            for _ in range(samples_per_domain):
                kw = random.choice(keywords) if keywords else "principles"
                sub = random.choice(sub_domains) if sub_domains else d_name
                tpl = random.choice(templates)
                text = tpl.format(keyword=kw, sub_domain=sub, domain=d_name)
                samples.append({
                    "id": f"domain_{sample_idx:06d}",
                    "text": text,
                    "domain": d_name,
                    "category": category,
                })
                sample_idx += 1

        random.shuffle(samples)
        return samples

    def generate_role_dataset(self, num_samples: int = 5000) -> list[dict[str, Any]]:
        """Generate 5000+ synthetic samples for role classification."""
        roles = self._km.get_roles()
        if not roles:
            roles = [{"title": "Software Engineer", "expertise_areas": ["coding", "architecture"]}]

        samples: list[dict[str, Any]] = []
        samples_per_role = max(1, num_samples // len(roles))

        sample_idx = 0
        seniorities = ["Principal", "Senior", "Lead", "Staff", "Chief", ""]

        for r in roles:
            title = r.get("title", "Subject Matter Expert")
            expertise = r.get("expertise_areas", [title])

            templates = [
                "Act as a {seniority} {title} to guide our implementation",
                "You are an expert {title} specializing in {skill}",
                "I need a {seniority} {title} to review our technical design",
                "mare {title} mate prompt joiye",
                "mujhe {title} ke liye prompt chahiye",
                "Prompt for a qualified {title} in {skill}",
            ]

            for _ in range(samples_per_role):
                sen = random.choice(seniorities)
                skill = random.choice(expertise) if expertise else title
                tpl = random.choice(templates)
                text = tpl.format(seniority=sen, title=title, skill=skill).strip()
                # Clean double spaces
                text = " ".join(text.split())
                samples.append({
                    "id": f"role_{sample_idx:06d}",
                    "text": text,
                    "role": title,
                })
                sample_idx += 1

        random.shuffle(samples)
        return samples

    def generate_requirements_dataset(self, num_samples: int = 5000) -> list[dict[str, Any]]:
        """Generate 5000+ synthetic examples with multi-dimensional requirement annotations."""
        samples: list[dict[str, Any]] = []

        for i in range(num_samples):
            intent = random.choice(self.INTENTS)
            tech = random.choice(self.TECHS)
            task = random.choice(self.TASKS)
            loc = random.choice(self.LOCATIONS)
            budget = random.choice(self.BUDGETS)
            deadline = random.choice(self.DEADLINES)
            aud = random.choice(self.AUDIENCES)
            fmt = random.choice(self.FORMATS)

            text = (
                f"{intent.title()} a {task} system with {tech} in {loc} for {aud}. "
                f"Budget: {budget}. Deadline: {deadline}. Format: {fmt}. "
                "Must not use external unverified dependencies. Strictly avoid single points of failure."
            )

            samples.append({
                "id": f"req_{i:06d}",
                "text": text,
                "goal": f"{intent.title()} a {task} system with {tech}",
                "audience": aud,
                "format": fmt,
                "budget": budget,
                "deadline": deadline,
                "location": loc,
                "constraints": [
                    "Must not use external unverified dependencies",
                    "Strictly avoid single points of failure",
                ],
            })

        return samples

    def generate_all_datasets(self, output_dir: str | Path = "ml-engine/datasets") -> dict[str, int]:
        """Generate all 4 synthetic datasets (over 20,000 total examples) and save to disk."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        logger.info("Generating 5000+ Intent Dataset...")
        intent_data = self.generate_intent_dataset(5200)
        self._save(intent_data, out_path / "intent_train.json")

        logger.info("Generating 5000+ Domain Dataset...")
        domain_data = self.generate_domain_dataset(5280)
        self._save(domain_data, out_path / "domain_train.json")

        logger.info("Generating 5000+ Role Dataset...")
        role_data = self.generate_role_dataset(5000)
        self._save(role_data, out_path / "role_train.json")

        logger.info("Generating 5000+ Requirements Dataset...")
        req_data = self.generate_requirements_dataset(5000)
        self._save(req_data, out_path / "requirements_train.json")

        counts = {
            "intent_samples": len(intent_data),
            "domain_samples": len(domain_data),
            "role_samples": len(role_data),
            "requirements_samples": len(req_data),
            "total_samples": len(intent_data) + len(domain_data) + len(role_data) + len(req_data),
        }
        logger.info("Successfully generated %d total synthetic training examples across 4 datasets.", counts["total_samples"])
        return counts

    def _save(self, data: list[dict[str, Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
