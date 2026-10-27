"""Comprehensive Knowledge Base Builder for Intentify AI Platform."""

from __future__ import annotations

import json
from pathlib import Path


def build_intent_blueprints() -> dict:
    return {
        "version": "1.0.0",
        "total_blueprints": 13,
        "blueprints": [
            {
                "id": "blueprint_create",
                "intent": "create",
                "name": "Creation and Construction Blueprint",
                "description": "Production blueprint for building, coding, generating from scratch, and architecting new assets.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an industry-leading {role} with deep specialization in {expertise_areas}. Approach this assignment with the rigorous precision and standards of a principal practitioner.", "required": True},
                    {"name": "objective", "template": "### 2. Core Objective\nYour primary objective is to create and deliver: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Context & Background\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Technical & Functional Requirements\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Guardrails & Operational Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Execution Instructions\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Output Format Specification\nDeliver the final response strictly in {format_spec} format.", "required": True},
                    {"name": "assumptions", "template": "### 8. Documented Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Self-Verification Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Build a high-performance REST API with FastAPI and PostgreSQL", "Create an autonomous prompt compilation engine"],
                "fallback_strategies": ["Assume modern LTS production environment", "Adopt modular clean architecture"]
            },
            {
                "id": "blueprint_write",
                "intent": "write",
                "name": "Professional Composition and Authoring Blueprint",
                "description": "Blueprint for editorial composition, technical documentation, executive proposals, and communication.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an acclaimed Master Author and Editorial Director ({role}) with mastery in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Core Objective\nDraft an eloquent, high-impact document to: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Narrative Context & Audience\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Key Messaging & Content Requirements\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Tone & Style Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Drafting Guidelines\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Document Layout & Structure\nFormat output strictly as {format_spec}.", "required": True},
                    {"name": "assumptions", "template": "### 8. Audience & Context Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Editorial Quality Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Write an executive summary of enterprise AI readiness", "Compose a comprehensive technical whitepaper"],
                "fallback_strategies": ["Adopt formal professional tone", "Structure with executive summary and key findings"]
            },
            {
                "id": "blueprint_generate",
                "intent": "generate",
                "name": "Generative Synthesis and Brainstorming Blueprint",
                "description": "Blueprint for producing diverse idea matrices, synthetic test vectors, and multi-variant solutions.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an expert Creative Strategist & Synthesis Lead ({role}) specializing in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Generative Objective\nSynthesize an exhaustive, diverse catalog of ideas and solutions for: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Problem Space Context\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Diversity & Novelty Criteria\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Exclusion Criteria & Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Generation Process\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Delivery Format\nPresent results in structured {format_spec} with categorization and scoring.", "required": True},
                    {"name": "assumptions", "template": "### 8. Context Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Feasibility & Quality Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Generate 20 high-potential SaaS startup concepts in legal tech", "Generate 50 unit test edge cases for token authentication"],
                "fallback_strategies": ["Ensure multi-angle diversity", "Include viability ratings for each generated entry"]
            },
            {
                "id": "blueprint_plan",
                "intent": "plan",
                "name": "Roadmapping and Strategic Planning Blueprint",
                "description": "Blueprint for chronological phase planning, work breakdown structures, risk matrices, and milestone tracking.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Principal Strategic Director & Enterprise Program Architect ({role}) with expertise in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Planning Objective\nFormulate a production-grade, milestone-driven execution plan for: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Operational Environment\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Deliverables & Resource Scope\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Resource & Schedule Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Phased Execution Steps\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Roadmap Specification\nDeliver roadmap in structured {format_spec} including phases, owners, and exit criteria.", "required": True},
                    {"name": "assumptions", "template": "### 8. Baseline Dependencies & Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Risk & Feasibility Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Plan a 6-month migration from AWS to GCP", "mare wedding planner mate prompt joiye"],
                "fallback_strategies": ["Structure into 4 chronological phases", "Identify critical path and dependencies"]
            },
            {
                "id": "blueprint_analyze",
                "intent": "analyze",
                "name": "Analytical Deep-Dive and Audit Blueprint",
                "description": "Blueprint for empirical decomposition, quantitative metrics auditing, and root-cause analytical review.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Senior Quantitative Analyst and Systems Auditor ({role}) with mastery in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Analytical Objective\nConduct a rigorous, data-driven audit and decomposition of: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Baseline Data & System Context\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Key Metrics & Dimensions\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Analysis Boundaries & Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Analytical Methodology\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Report Structure\nStructure findings as {format_spec} with findings, metrics, and risk scores.", "required": True},
                    {"name": "assumptions", "template": "### 8. Baseline Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Analytical Rigor Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Analyze database query bottlenecks under 100k QPS", "Audit financial churn indicators for subscription business"],
                "fallback_strategies": ["Establish quantitative baselines", "Separate correlation from causation"]
            },
            {
                "id": "blueprint_explain",
                "intent": "explain",
                "name": "Pedagogical Explanation and Mental Model Blueprint",
                "description": "Blueprint for elucidating complex technical and conceptual ideas across multiple cognitive levels.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an elite Educator, Distinguished Researcher, and Explainer ({role}) with specialization in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Explanation Objective\nDemystify and explain with supreme clarity: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Learner Background & Context\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Core Concepts & Analogies Required\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Cognitive Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Pedagogical Flow\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Explanation Structure\nFormat as {format_spec} transitioning from first principles to concrete real-world intuition.", "required": True},
                    {"name": "assumptions", "template": "### 8. Prerequisite Knowledge Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Comprehension & Clarity Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Explain multi-head attention mechanisms to a web developer", "Explain zero-knowledge proofs from first principles"],
                "fallback_strategies": ["Use intuitive real-world analogies", "Provide progressive disclosure of complexity"]
            },
            {
                "id": "blueprint_compare",
                "intent": "compare",
                "name": "Comparative Evaluation and Trade-off Matrix Blueprint",
                "description": "Blueprint for objective side-by-side benchmarking, architectural trade-offs, and multi-criteria scoring.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an unbiased Technical Evaluator and Systems Architect ({role}) with mastery in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Comparative Objective\nPerform an objective, multi-criteria comparison between options for: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Evaluation Context & Workload\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Comparison Dimensions & Weights\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Impartiality & Scope Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Comparison Methodology\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Comparison Matrix Format\nDeliver a markdown comparison table followed by trade-off analysis in {format_spec}.", "required": True},
                    {"name": "assumptions", "template": "### 8. Comparison Baseline Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Objectivity Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Compare PostgreSQL vs MongoDB for high-throughput fintech", "Compare Kubernetes vs AWS ECS for startup deployment"],
                "fallback_strategies": ["Evaluate performance, cost, developer experience, and scalability", "Provide definitive decision rule"]
            },
            {
                "id": "blueprint_translate",
                "intent": "translate",
                "name": "Localization and Cross-Lingual Translation Blueprint",
                "description": "Blueprint for idiomatically nuanced, culturally context-aware, and domain-precise multilingual conversion.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Master Multilingual Translator and Cultural Localization Expert ({role}) specializing in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Translation Objective\nTranslate and adapt with 100% semantic fidelity: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Linguistic Context & Dialect\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Terminology & Register Requirements\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Localization Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Translation Process\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Deliverable Layout\nDeliver target language text with side-by-side or annotated {format_spec}.", "required": True},
                    {"name": "assumptions", "template": "### 8. Idiom & Cultural Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Linguistic Fidelity Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Translate technical documentation from English to Gujarati", "Localize terms of service into legal French"],
                "fallback_strategies": ["Preserve specialized terminology in parentheses", "Avoid literal calques in favor of natural phrasing"]
            },
            {
                "id": "blueprint_research",
                "intent": "research",
                "name": "State-of-the-Art Research and Literature Synthesis Blueprint",
                "description": "Blueprint for academic survey, frontier research synthesis, and empirical literature review.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Principal Research Scientist ({role}) with international renown in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Research Objective\nInvestigate, survey, and synthesize state-of-the-art developments regarding: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Scientific & Academic Context\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Research Scope & Dimensions\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Methodological Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Investigation Protocol\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Research Digest Format\nStructure synthesized findings into {format_spec} with methodologies, findings, and citations.", "required": True},
                    {"name": "assumptions", "template": "### 8. Methodological Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Empirical Rigor Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Survey current methods in sparse attention models", "Research clinical trial outcomes for mRNA oncology vaccines"],
                "fallback_strategies": ["Group by taxonomy of approaches", "Highlight open challenges and frontier questions"]
            },
            {
                "id": "blueprint_design",
                "intent": "design",
                "name": "Architecture and UX/System Design Blueprint",
                "description": "Blueprint for architectural schemas, component hierarchy, UI/UX interaction flows, and physical/digital systems.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Chief Architect & Principal Designer ({role}) specializing in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Design Objective\nCreate a holistic, elegant, scalable design specification for: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Design Environment & Constraints\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Design Components & Schemas\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Architectural Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. System Synthesis Steps\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Specification Blueprint Format\nProvide detailed architectural diagrams, interfaces, and schemas in {format_spec}.", "required": True},
                    {"name": "assumptions", "template": "### 8. Architectural Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Modularity & UX Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Design microservices event-driven architecture for e-commerce", "Design a mobile-first dashboard for healthcare analytics"],
                "fallback_strategies": ["Include component interaction models", "Define interface contracts and schemas"]
            },
            {
                "id": "blueprint_debug",
                "intent": "debug",
                "name": "Root Cause Analysis and Troubleshooting Blueprint",
                "description": "Blueprint for incident reproduction, diagnostic telemetry tracing, and definitive defect resolution.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are an elite Systems Diagnostic Engineer & Reliability Architect ({role}) specializing in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Diagnostic Objective\nIsolate root cause, reproduce the defect, and deliver an airtight fix for: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Incident Context & Stack Trace\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Diagnostic Criteria & Reproduction Steps\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Operational Constraints\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Systematic Troubleshooting Flow\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. RCA Report Format\nFormat response as {format_spec} with Root Cause, Patch Code, and Regression Suite.", "required": True},
                    {"name": "assumptions", "template": "### 8. Incident Environment Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Zero-Regression Verification Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Debug memory leak in Node.js server under high event loop load", "Resolve race condition in Redis distributed lock"],
                "fallback_strategies": ["Formulate hypothesis tree", "Provide minimal reproducible test case"]
            },
            {
                "id": "blueprint_improve",
                "intent": "improve",
                "name": "Optimization and Modernization Blueprint",
                "description": "Blueprint for refactoring legacy assets, algorithmic latency reduction, throughput enhancement, and modernization.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Principal Performance Engineer & Refactoring Specialist ({role}) with mastery in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Optimization Objective\nRefactor, optimize, and dramatically elevate performance of: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Existing Baseline & Profile Data\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Target Performance KPIs\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Backward Compatibility Guardrails\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Refactoring Steps\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Deliverable Layout\nDeliver before/after comparisons and benchmarked improvements in {format_spec}.", "required": True},
                    {"name": "assumptions", "template": "### 8. Performance Baseline Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Optimization Verification Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Optimize slow SQL joins handling 50M rows", "Refactor monolithic backend service into clean modular architecture"],
                "fallback_strategies": ["Profile hottest execution paths", "Quantify expected speedup and complexity change"]
            },
            {
                "id": "blueprint_decide",
                "intent": "decide",
                "name": "Decision Framework and Strategic Recommendation Blueprint",
                "description": "Blueprint for high-stakes executive decisions, cost-benefit trade-offs, risk assessments, and final verdicts.",
                "sections": [
                    {"name": "role", "template": "### 1. Role & Persona\nYou are a Chief Strategy Officer and Executive Decision Advisory Partner ({role}) with expertise in {expertise_areas}.", "required": True},
                    {"name": "objective", "template": "### 2. Decision Objective\nFormulate a rigorous, risk-weighted recommendation and definitive decision on: {goal}.", "required": True},
                    {"name": "context", "template": "### 3. Business Context & Stakes\n{context_details}", "required": True},
                    {"name": "requirements", "template": "### 4. Decision Criteria & Hurdle Rates\n{requirements_list}", "required": True},
                    {"name": "constraints", "template": "### 5. Risk Tolerance & Boundary Conditions\n{constraints_list}", "required": True},
                    {"name": "instructions", "template": "### 6. Decision Analysis Framework\n{instructions}", "required": True},
                    {"name": "output_format", "template": "### 7. Executive Decision Memo Format\nDeliver a formal Executive Decision Memo in {format_spec} with clear verdict, rationale, and mitigation strategy.", "required": True},
                    {"name": "assumptions", "template": "### 8. Economic & Context Assumptions\n{assumptions_list}", "required": True},
                    {"name": "quality_checklist", "template": "### 9. Decision Robustness Checklist\n{checklist}", "required": True}
                ],
                "quality_weights": {"clarity": 20, "specificity": 20, "context": 15, "constraints": 15, "output_format": 15, "ambiguity_handling": 15},
                "example_prompts": ["Decide whether to build in-house or buy third-party fraud detection software", "Recommend optimal cloud architecture for multi-region fintech"],
                "fallback_strategies": ["Define decision matrix with weighted scores", "Provide unambiguous executive verdict"]
            }
        ]
    }


def build_output_formats() -> dict:
    return {
        "version": "1.0.0",
        "total_formats": 25,
        "formats": [
            {
                "id": "format_detailed_technical",
                "name": "Detailed Technical Response",
                "description": "Exhaustive enterprise technical documentation with executive overview, implementation, and verification.",
                "structure": "## Executive Summary\n{summary}\n\n## Architecture & Implementation\n{implementation}\n\n## Verification & Edge Cases\n{verification}\n\n## Next Steps\n{next_steps}",
                "suitable_intents": ["create", "plan", "analyze", "debug", "improve"],
                "suitable_domains": ["Technology", "Engineering", "Cybersecurity", "Data Science"]
            },
            {
                "id": "format_step_by_step_guide",
                "name": "Step-by-Step Implementation Guide",
                "description": "Chronological numbered instructions with clear prerequisites, code blocks, and validation gates.",
                "structure": "### Prerequisites\n{prerequisites}\n\n### Step 1: Initialization\n{step_1}\n\n### Step 2: Implementation\n{step_2}\n\n### Step 3: Verification\n{step_3}",
                "suitable_intents": ["create", "plan", "improve", "debug", "explain"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_comparison_matrix",
                "name": "Comparison Matrix Table",
                "description": "Multi-dimensional side-by-side comparison table evaluating options across criteria with scoring.",
                "structure": "| Dimension | Option A | Option B | Option C | Recommendation |\n|---|---|---|---|---|\n| Architecture | ... | ... | ... | ... |\n| Scalability | ... | ... | ... | ... |\n| Cost | ... | ... | ... | ... |",
                "suitable_intents": ["compare", "analyze", "decide"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_json_schema",
                "name": "Strict JSON Schema & Payload",
                "description": "Machine-readable JSON object adhering to defined types and schema specifications.",
                "structure": "```json\n{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"properties\": {}\n}\n```",
                "suitable_intents": ["generate", "create"],
                "suitable_domains": ["Technology", "Finance", "Healthcare"]
            },
            {
                "id": "format_executive_brief",
                "name": "Executive Brief",
                "description": "High-level strategic briefing designed for C-level leadership and board decisions.",
                "structure": "# Executive Brief: {title}\n\n## The Strategic Problem\n{problem}\n\n## Recommended Solution\n{solution}\n\n## Financial & Risk Impact\n{impact}\n\n## Immediate Decision Required\n{verdict}",
                "suitable_intents": ["decide", "plan", "analyze"],
                "suitable_domains": ["Business", "Finance", "Legal", "Executive"]
            },
            {
                "id": "format_adr",
                "name": "Architectural Decision Record (ADR)",
                "description": "Standardized architecture record capturing context, decision, consequences, and alternatives.",
                "structure": "# ADR: {title}\n\n## Status\nProposed / Accepted\n\n## Context\n{context}\n\n## Decision\n{decision}\n\n## Consequences\n### Positive\n{positive}\n### Negative / Trade-offs\n{negative}",
                "suitable_intents": ["decide", "design", "create"],
                "suitable_domains": ["Technology", "Engineering"]
            },
            {
                "id": "format_rca_report",
                "name": "Root Cause Analysis (RCA) Report",
                "description": "Comprehensive post-mortem report isolating failure modes, timeline, root causes, and preventive actions.",
                "structure": "# Incident RCA: {incident_title}\n\n## Incident Summary\n{summary}\n\n## Timeline of Events\n{timeline}\n\n## Root Cause (5 Whys Analysis)\n{root_cause}\n\n## Action Items & Preventative Measures\n{actions}",
                "suitable_intents": ["debug", "analyze"],
                "suitable_domains": ["Technology", "Cybersecurity", "Engineering", "Operations"]
            },
            {
                "id": "format_checklist_protocol",
                "name": "Quality & Verification Protocol Checklist",
                "description": "Actionable, checkbox-driven audit protocol ensuring operational compliance.",
                "structure": "### Pre-Flight Verification\n- [ ] {item_1}\n- [ ] {item_2}\n\n### Execution Checks\n- [ ] {item_3}\n\n### Post-Flight Acceptance\n- [ ] {item_4}",
                "suitable_intents": ["plan", "create", "improve", "debug"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_annotated_code",
                "name": "Production Code with Inline Architectural Annotations",
                "description": "Clean, typed code with inline comments explaining design patterns, complexity, and safety guards.",
                "structure": "```python\n# Architectural Overview: ...\n# Time Complexity: O(...), Space Complexity: O(...)\n\ndef solution():\n    pass\n```",
                "suitable_intents": ["create", "debug", "improve"],
                "suitable_domains": ["Technology", "Data Science"]
            },
            {
                "id": "format_business_proposal",
                "name": "Commercial Business Proposal",
                "description": "Client-facing commercial and technical proposal with scope, timeline, and pricing.",
                "structure": "## Executive Summary\n{summary}\n\n## Proposed Scope of Work\n{scope}\n\n## Delivery Milestones & Timeline\n{timeline}\n\n## Investment & Commercial Terms\n{commercials}",
                "suitable_intents": ["write", "plan"],
                "suitable_domains": ["Business", "Marketing", "Consulting"]
            },
            {
                "id": "format_tutorial_walkthrough",
                "name": "Tutorial & Educational Walkthrough",
                "description": "Beginner-to-advanced learning module with explanations, interactive checks, and summaries.",
                "structure": "# Lesson: {title}\n\n## What You Will Learn\n{outcomes}\n\n## Core Concept: Intuition\n{intuition}\n\n## Hands-on Exercise\n{exercise}\n\n## Key Takeaways\n{takeaways}",
                "suitable_intents": ["explain", "write"],
                "suitable_domains": ["Education", "Technology"]
            },
            {
                "id": "format_sop",
                "name": "Standard Operating Procedure (SOP)",
                "description": "Institutional operational procedure detailing roles, inputs, workflow, and compliance.",
                "structure": "# SOP-{id}: {title}\n\n## Purpose & Scope\n{scope}\n\n## Responsibilities\n{responsibilities}\n\n## Procedure Steps\n{procedure}\n\n## Documentation & Audit Records\n{records}",
                "suitable_intents": ["plan", "create"],
                "suitable_domains": ["Healthcare", "Manufacturing", "Operations", "Legal"]
            },
            {
                "id": "format_faq_guide",
                "name": "FAQ & Troubleshooting Reference",
                "description": "Direct question-and-answer pairs addressing frequent pain points and edge cases.",
                "structure": "### Q: {question_1}?\n**A:** {answer_1}\n\n### Q: {question_2}?\n**A:** {answer_2}",
                "suitable_intents": ["explain", "debug"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_strategy_roadmap",
                "name": "Phased Strategic Roadmap",
                "description": "Timeline-oriented strategic plan broken into quarters or milestones with deliverable gates.",
                "structure": "## Phase 1: Foundation (Months 1-2)\n- Deliverables: {deliv_1}\n- Success Metrics: {kpi_1}\n\n## Phase 2: Scaling (Months 3-4)\n- Deliverables: {deliv_2}\n\n## Phase 3: Optimization (Months 5-6)\n- Deliverables: {deliv_3}",
                "suitable_intents": ["plan", "decide"],
                "suitable_domains": ["Business", "Technology", "Marketing"]
            },
            {
                "id": "format_executive_email",
                "name": "Executive Email & Stakeholder Communication",
                "description": "Concise, persuasive email tailored for busy stakeholders.",
                "structure": "**Subject:** {subject}\n\nHi {name},\n\n**TL;DR:** {tldr}\n\n**Key Updates:**\n- {update_1}\n- {update_2}\n\n**Action Required:** {action}\n\nBest,\n{sender}",
                "suitable_intents": ["write"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_policy_document",
                "name": "Institutional Policy & Compliance Standard",
                "description": "Formal governance policy specifying acceptable use, enforcement, and exceptions.",
                "structure": "## Policy Title: {title}\n\n## 1. Policy Statement\n{statement}\n\n## 2. Applicability\n{applicability}\n\n## 3. Mandatory Requirements\n{requirements}\n\n## 4. Enforcement & Penalties\n{enforcement}",
                "suitable_intents": ["create", "write"],
                "suitable_domains": ["Legal", "Cybersecurity", "Corporate"]
            },
            {
                "id": "format_pitch_deck",
                "name": "Pitch Deck Slide-by-Slide Narrative",
                "description": "Compelling 10-slide narrative for startup investor pitches.",
                "structure": "### Slide 1: Problem\n{problem}\n\n### Slide 2: Solution\n{solution}\n\n### Slide 3: Market Size (TAM/SAM/SOM)\n{market}\n\n### Slide 4: Business Model\n{model}\n\n### Slide 5: The Ask\n{ask}",
                "suitable_intents": ["write", "plan"],
                "suitable_domains": ["Business", "Venture Capital"]
            },
            {
                "id": "format_test_plan",
                "name": "Test Plan & QA Verification Matrix",
                "description": "Systematic QA matrix detailing test cases, preconditions, steps, and assertions.",
                "structure": "| Test ID | Component | Precondition | Input / Action | Expected Result | Priority |\n|---|---|---|---|---|---|\n| TC-01 | Auth | User exists | Valid login | 200 OK + JWT | P0 |\n| TC-02 | Auth | Invalid pass | Failed login | 401 Unauthorized | P0 |",
                "suitable_intents": ["plan", "create", "debug"],
                "suitable_domains": ["Technology", "Engineering"]
            },
            {
                "id": "format_whitepaper_digest",
                "name": "Scientific Whitepaper Digest",
                "description": "Structured academic review summarizing background, experimental methodology, and implications.",
                "structure": "# Scientific Digest: {title}\n\n## Abstract\n{abstract}\n\n## Theoretical Framework\n{theory}\n\n## Empirical Findings\n{findings}\n\n## Industrial Implications\n{implications}",
                "suitable_intents": ["research", "analyze"],
                "suitable_domains": ["Science", "Healthcare", "Technology"]
            },
            {
                "id": "format_bullet_summary",
                "name": "Concise Bulleted Summary",
                "description": "Rapid actionable takeaways highlighting core decisions and numbers.",
                "structure": "### Key Takeaways\n- {takeaway_1}\n- {takeaway_2}\n- {takeaway_3}\n\n### Operational Next Steps\n- {step_1}",
                "suitable_intents": ["analyze", "explain", "write"],
                "suitable_domains": ["all"]
            },
            {
                "id": "format_event_master_plan",
                "name": "Event Master Coordination Plan",
                "description": "Multi-phase event coordination roadmap covering budgeting, vendor schedules, run-of-show, and logistics.",
                "structure": "# Event Master Plan: {event_name}\n\n## 1. Event Vision & Key Milestones\n{vision}\n\n## 2. Budget Allocation & Vendor Matrix\n{budget_matrix}\n\n## 3. Run of Show (Minute-by-Minute Timeline)\n{timeline}\n\n## 4. Contingency & Crisis Protocols\n{contingency}",
                "suitable_intents": ["plan", "create"],
                "suitable_domains": ["Hospitality", "Event Planning"]
            },
            {
                "id": "format_contract_clause",
                "name": "Legal Contract Clause & Drafting Memo",
                "description": "Formal legal covenant with definition of terms, obligations, and risk allocation notes.",
                "structure": "### SECTION {num}: {clause_title}\n\n**1. Operative Provision:**\n{provision}\n\n**2. Commentary & Legal Rationale:**\n{commentary}\n\n**3. Negotiation Trade-offs:**\n{tradeoffs}",
                "suitable_intents": ["write", "create"],
                "suitable_domains": ["Legal", "Compliance"]
            },
            {
                "id": "format_clinical_case_study",
                "name": "Clinical Case Study & Care Protocol",
                "description": "Evidence-based clinical protocol detailing patient presentation, diagnostics, and treatment.",
                "structure": "## Patient Profile & Presentation\n{presentation}\n\n## Diagnostic Findings\n{diagnostics}\n\n## Treatment & Intervention Protocol\n{treatment}\n\n## Clinical Prognosis & Monitoring\n{monitoring}",
                "suitable_intents": ["analyze", "plan"],
                "suitable_domains": ["Healthcare", "Medicine"]
            },
            {
                "id": "format_marketing_campaign_brief",
                "name": "Integrated Marketing Campaign Brief",
                "description": "Comprehensive marketing launch brief with audience personas, creative angles, and channel KPIs.",
                "structure": "# Campaign Brief: {campaign_name}\n\n## Target Audience Persona\n{persona}\n\n## Core Value Proposition & Hooks\n{hooks}\n\n## Channel Distribution Strategy\n{channels}\n\n## Attribution & Conversion KPIs\n{kpis}",
                "suitable_intents": ["plan", "write", "create"],
                "suitable_domains": ["Marketing", "E-commerce"]
            },
            {
                "id": "format_data_pipeline_spec",
                "name": "Data Pipeline & ETL Specification",
                "description": "Technical specification for data ingestion, schema validation, transformation, and storage.",
                "structure": "## Pipeline Architecture\n{architecture}\n\n## Source Ingestion & Schemas\n{schemas}\n\n## Transformation Logic & Deduplication\n{transformations}\n\n## SLA, Backfill & Dead-Letter Queue\n{sla}",
                "suitable_intents": ["create", "design"],
                "suitable_domains": ["Technology", "Data Engineering"]
            }
        ]
    }


def build_quality_rules() -> dict:
    return {
        "version": "1.0.0",
        "threshold": 85.0,
        "max_score": 100.0,
        "criteria": [
            {
                "id": "clarity",
                "name": "Clarity & Persona Definition",
                "max_score": 20.0,
                "weight_percentage": 20,
                "rules": [
                    {"id": "clr_role", "name": "Explicit Persona Definition", "points": 5.0, "description": "Defines an authoritative, domain-specialized professional role and persona."},
                    {"id": "clr_objective", "name": "Clear Primary Objective", "points": 5.0, "description": "States an unambiguous, action-oriented primary deliverable or goal."},
                    {"id": "clr_depth", "name": "Comprehensive Depth", "points": 5.0, "description": "Sufficient depth and technical rigor; avoids unhelpful brevity."},
                    {"id": "clr_markdown", "name": "Structural Markdown Sectioning", "points": 5.0, "description": "Uses clean headers, logical sectioning, and structured markdown syntax."}
                ]
            },
            {
                "id": "specificity",
                "name": "Technical Specificity & Actionability",
                "max_score": 20.0,
                "weight_percentage": 20,
                "rules": [
                    {"id": "spc_bullets", "name": "Granular Parameterization", "points": 7.0, "description": "Provides granular, numbered or bulleted items rather than vague prose."},
                    {"id": "spc_instructions", "name": "Step-by-Step Execution Sequence", "points": 7.0, "description": "Provides chronological or phased execution steps."},
                    {"id": "spc_precision", "name": "Deterministic Keywords", "points": 6.0, "description": "Uses exact technical standards, criteria, and determinative terms."}
                ]
            },
            {
                "id": "context",
                "name": "Domain Context & Scope",
                "max_score": 15.0,
                "weight_percentage": 15,
                "rules": [
                    {"id": "ctx_section", "name": "Dedicated Context & Background", "points": 8.0, "description": "Contains an explicit contextual block explaining the environment and stakeholders."},
                    {"id": "ctx_depth", "name": "Specialized Domain Scope", "points": 7.0, "description": "Incorporates specialized domain nuances, standards, and vocabulary."}
                ]
            },
            {
                "id": "constraints",
                "name": "Guardrails & Constraints",
                "max_score": 15.0,
                "weight_percentage": 15,
                "rules": [
                    {"id": "cst_section", "name": "Dedicated Constraints Section", "points": 8.0, "description": "Explicitly details operational boundaries and requirements."},
                    {"id": "cst_negative", "name": "Negative Guardrails", "points": 7.0, "description": "Specifies negative conditions (what the model must NOT do or avoid)."}
                ]
            },
            {
                "id": "output_format",
                "name": "Output Formatting Rules",
                "max_score": 15.0,
                "weight_percentage": 15,
                "rules": [
                    {"id": "fmt_section", "name": "Explicit Output Format Section", "points": 8.0, "description": "Explicitly mandates the response layout, structure, and sections."},
                    {"id": "fmt_syntax", "name": "Concrete Syntax Specifications", "points": 7.0, "description": "Defines exact formatting syntax such as Markdown, JSON, Tables, or Code."}
                ]
            },
            {
                "id": "ambiguity_handling",
                "name": "Ambiguity Resolution & Self-Verification",
                "max_score": 15.0,
                "weight_percentage": 15,
                "rules": [
                    {"id": "amb_assumptions", "name": "Documented Proactive Assumptions", "points": 8.0, "description": "Articulates sensible default assumptions when human input is underspecified."},
                    {"id": "amb_checklist", "name": "Quality Verification Checklist", "points": 7.0, "description": "Includes an actionable self-verification checklist for the executing model."}
                ]
            }
        ],
        "auto_improvement": {
            "trigger_threshold": 85.0,
            "max_iterations": 3,
            "priority_order": ["constraints", "output_format", "ambiguity_handling", "specificity", "context", "clarity"]
        }
    }


def build_default_assumptions() -> dict:
    return {
        "version": "1.0.0",
        "general_defaults": [
            "Target environment represents a modern production standard with security best practices.",
            "Target audience possesses foundational familiarity with standard industry terminology.",
            "Primary language is English unless regional script is explicitly detected.",
            "All software components must follow modular clean architecture with zero hardcoded credentials.",
            "Deliverables must prioritize deterministic verification and measurable success metrics."
        ],
        "domain_assumptions": {
            "Software Development": [
                "Target architecture adheres to clean code, SOLID principles, and modular components.",
                "All dependencies and packages are modern Long-Term Support (LTS) releases.",
                "Automated unit and integration test coverage is expected."
            ],
            "Cybersecurity": [
                "Follow Principle of Least Privilege (PoLP) and Zero Trust architecture.",
                "Ensure compliance with OWASP Top 10, NIST, and SOC2 security frameworks."
            ],
            "Healthcare": [
                "All recommendations prioritize patient safety, HIPAA/GDPR compliance, and clinical evidence.",
                "AI output is for clinical decision support, requiring licensed physician review."
            ],
            "Legal": [
                "Output represents analytical drafting templates requiring qualified jurisdictional attorney review.",
                "Ensure strict statutory compliance with relevant federal and state precedents."
            ],
            "Finance": [
                "Strict auditability, idempotent transaction guarantees, and double-entry bookkeeping apply.",
                "Comply with SEC, FINRA, and international fiscal reporting standards."
            ],
            "Hospitality & Events": [
                "Budgets include 15-20% contingency allocation for unforeseen vendor and venue variances.",
                "Timelines must incorporate buffer windows for vendor load-in and guest arrival dynamics."
            ],
            "Education": [
                "Pedagogical approaches align with Bloom's Taxonomy and universal design for learning.",
                "Learning activities prioritize active problem solving over passive absorption."
            ],
            "Marketing": [
                "Campaign metrics are oriented toward quantifiable ROI, CAC, LTV, and conversion rate.",
                "Messaging respects consumer privacy laws including CAN-SPAM and GDPR consent."
            ],
            "Engineering": [
                "Designs include safety factor margins of at least 1.5x to 2.0x operational tolerances.",
                "Adhere to relevant IEEE, ASME, or ISO manufacturing and structural specifications."
            ],
            "Agriculture": [
                "Recommendations emphasize sustainable soil stewardship, water conservation, and integrated pest management.",
                "Calculations account for local climate zone variability and seasonal rainfall trends."
            ]
        },
        "intent_assumptions": {
            "create": [
                "Build for maintainability, documentation completeness, and ease of automated testing."
            ],
            "debug": [
                "Isolate root cause before recommending surgical, minimally invasive fixes.",
                "Include regression test assertions to ensure the bug cannot silently recur."
            ],
            "plan": [
                "Break milestones into 2-week execution sprints with concrete acceptance criteria."
            ],
            "compare": [
                "Maintain complete objectivity with calibrated scoring across all evaluation dimensions."
            ],
            "decide": [
                "Provide an unambiguous final recommendation with explicit risk mitigations."
            ]
        }
    }


def main():
    kb_dir = Path(__file__).resolve().parent

    # 1. Blueprints
    bp_path = kb_dir / "blueprints" / "intent_blueprints.json"
    bp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bp_path, "w", encoding="utf-8") as f:
        json.dump(build_intent_blueprints(), f, indent=2)
    print(f"Saved 13 intent blueprints to {bp_path}")

    # 2. Output Formats
    fmt_path = kb_dir / "templates" / "output_formats.json"
    fmt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(fmt_path, "w", encoding="utf-8") as f:
        json.dump(build_output_formats(), f, indent=2)
    print(f"Saved 25 output format templates to {fmt_path}")

    # 3. Quality Rules
    qr_path = kb_dir / "quality_rules" / "quality_rules.json"
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    with open(qr_path, "w", encoding="utf-8") as f:
        json.dump(build_quality_rules(), f, indent=2)
    print(f"Saved 100-point quality scoring rules to {qr_path}")

    # 4. Default Assumptions
    as_path = kb_dir / "assumptions" / "default_assumptions.json"
    as_path.parent.mkdir(parents=True, exist_ok=True)
    with open(as_path, "w", encoding="utf-8") as f:
        json.dump(build_default_assumptions(), f, indent=2)
    print(f"Saved default assumptions to {as_path}")


if __name__ == "__main__":
    main()
