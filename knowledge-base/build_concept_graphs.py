"""Build concept graphs for all 12 key domains with prerequisite-ordered concept trees."""

from __future__ import annotations

import json
from pathlib import Path

cg_dir = Path("knowledge-base/concept_graphs")
cg_dir.mkdir(parents=True, exist_ok=True)

graphs = {
    "c.json": {
        "domain": "C Programming",
        "nodes": [
            {"id": "c_basics", "name": "Syntax, Types & Control Flow", "prerequisites": []},
            {"id": "c_functions", "name": "Functions & Scope", "prerequisites": ["c_basics"]},
            {"id": "c_pointers", "name": "Pointers & Memory Addresses", "prerequisites": ["c_functions"]},
            {"id": "c_mem_mgmt", "name": "Dynamic Memory Allocation (malloc/free)", "prerequisites": ["c_pointers"]},
            {"id": "c_structs", "name": "Structs, Unions & TypeDefs", "prerequisites": ["c_mem_mgmt"]},
            {"id": "c_data_structures", "name": "Linked Lists & Trees in C", "prerequisites": ["c_structs"]},
            {"id": "c_bitwise", "name": "Bitwise Operations & Low-level I/O", "prerequisites": ["c_data_structures"]},
            {"id": "c_file_io", "name": "File I/O & Error Handling (errno)", "prerequisites": ["c_bitwise"]},
        ],
    },
    "cpp.json": {
        "domain": "C++ Programming",
        "nodes": [
            {"id": "cpp_basics", "name": "C++ Core Syntax & References", "prerequisites": []},
            {"id": "cpp_oop", "name": "Classes, Constructors & RAII", "prerequisites": ["cpp_basics"]},
            {"id": "cpp_inheritance", "name": "Inheritance & Virtual Polymorphism", "prerequisites": ["cpp_oop"]},
            {"id": "cpp_stl", "name": "STL Containers, Iterators & Algorithms", "prerequisites": ["cpp_inheritance"]},
            {"id": "cpp_templates", "name": "Templates & Generic Programming", "prerequisites": ["cpp_stl"]},
            {"id": "cpp_smart_ptrs", "name": "Smart Pointers (unique_ptr, shared_ptr)", "prerequisites": ["cpp_templates"]},
            {"id": "cpp_move", "name": "Move Semantics & Rvalue References", "prerequisites": ["cpp_smart_ptrs"]},
            {"id": "cpp_concurrency", "name": "Modern Concurrency & Thread Pools", "prerequisites": ["cpp_move"]},
        ],
    },
    "java.json": {
        "domain": "Java Programming",
        "nodes": [
            {"id": "java_basics", "name": "JVM Basics, Types & Control Structures", "prerequisites": []},
            {"id": "java_oop", "name": "OOP Principles, Interfaces & Abstract Classes", "prerequisites": ["java_basics"]},
            {"id": "java_collections", "name": "Collections Framework & Generics", "prerequisites": ["java_oop"]},
            {"id": "java_exceptions", "name": "Exception Handling & Resource Management", "prerequisites": ["java_collections"]},
            {"id": "java_lambdas", "name": "Streams API & Functional Programming", "prerequisites": ["java_exceptions"]},
            {"id": "java_concurrency", "name": "Multithreading, Locks & Executors", "prerequisites": ["java_lambdas"]},
            {"id": "java_spring", "name": "Spring Boot Architecture & Dependency Injection", "prerequisites": ["java_concurrency"]},
            {"id": "java_testing", "name": "JUnit 5, Mockito & Integration Testing", "prerequisites": ["java_spring"]},
        ],
    },
    "python.json": {
        "domain": "Python Programming",
        "nodes": [
            {"id": "py_basics", "name": "Python Syntax, Control Flow & Data Types", "prerequisites": []},
            {"id": "py_collections", "name": "Lists, Dicts, Sets & Comprehensions", "prerequisites": ["py_basics"]},
            {"id": "py_functions", "name": "Functions, Args/Kwargs & Lambda", "prerequisites": ["py_collections"]},
            {"id": "py_oop", "name": "Object-Oriented Design & Dunder Methods", "prerequisites": ["py_functions"]},
            {"id": "py_iter_gen", "name": "Iterators, Generators & Context Managers", "prerequisites": ["py_oop"]},
            {"id": "py_decorators", "name": "Decorators & Metaprogramming", "prerequisites": ["py_iter_gen"]},
            {"id": "py_async", "name": "Asyncio, Coroutines & Concurrency", "prerequisites": ["py_decorators"]},
            {"id": "py_typing", "name": "Type Annotations & Modern Packaging", "prerequisites": ["py_async"]},
        ],
    },
    "javascript.json": {
        "domain": "JavaScript Programming",
        "nodes": [
            {"id": "js_basics", "name": "Variables, Types, Scope & Functions", "prerequisites": []},
            {"id": "js_async", "name": "Promises, Event Loop & Async/Await", "prerequisites": ["js_basics"]},
            {"id": "js_prototypes", "name": "Prototypes, Classes & ES6+ Features", "prerequisites": ["js_async"]},
            {"id": "js_dom", "name": "DOM Manipulation & Browser Events", "prerequisites": ["js_prototypes"]},
            {"id": "js_modules", "name": "ES Modules & Modern Bundlers", "prerequisites": ["js_dom"]},
            {"id": "js_node", "name": "Node.js Runtime & Streams", "prerequisites": ["js_modules"]},
            {"id": "js_typescript", "name": "TypeScript Typing & Interfaces", "prerequisites": ["js_node"]},
            {"id": "js_frameworks", "name": "React/Next.js Component Lifecycle", "prerequisites": ["js_typescript"]},
        ],
    },
    "sql.json": {
        "domain": "Database & SQL",
        "nodes": [
            {"id": "sql_basics", "name": "Relational Data Modeling & DDL/DML", "prerequisites": []},
            {"id": "sql_joins", "name": "Inner, Outer & Self Joins", "prerequisites": ["sql_basics"]},
            {"id": "sql_aggregation", "name": "GROUP BY, HAVING & Aggregations", "prerequisites": ["sql_joins"]},
            {"id": "sql_subqueries", "name": "Subqueries & CTEs (WITH queries)", "prerequisites": ["sql_aggregation"]},
            {"id": "sql_indexes", "name": "Indexing Strategies & B-Trees", "prerequisites": ["sql_subqueries"]},
            {"id": "sql_acid", "name": "ACID Transactions & Isolation Levels", "prerequisites": ["sql_indexes"]},
            {"id": "sql_query_plan", "name": "EXPLAIN ANALYZE & Query Optimization", "prerequisites": ["sql_acid"]},
            {"id": "sql_partitioning", "name": "Table Partitioning & Sharding", "prerequisites": ["sql_query_plan"]},
        ],
    },
    "saas.json": {
        "domain": "SaaS Cloud Architecture",
        "nodes": [
            {"id": "saas_tenancy", "name": "Multi-Tenant Data Isolation Strategy", "prerequisites": []},
            {"id": "saas_auth", "name": "Unified Identity & RBAC / ABAC Security", "prerequisites": ["saas_tenancy"]},
            {"id": "saas_api", "name": "REST/GraphQL API Gateway & Rate Limiting", "prerequisites": ["saas_auth"]},
            {"id": "saas_billing", "name": "Subscription Billing, Webhooks & Metering", "prerequisites": ["saas_api"]},
            {"id": "saas_async", "name": "Message Queues & Background Job Processing", "prerequisites": ["saas_billing"]},
            {"id": "saas_caching", "name": "Distributed Caching (Redis) & Session Stores", "prerequisites": ["saas_async"]},
            {"id": "saas_observability", "name": "Distributed Tracing, Metrics & APM Alerts", "prerequisites": ["saas_caching"]},
            {"id": "saas_cicd", "name": "Zero-Downtime CI/CD & Blue-Green Deployments", "prerequisites": ["saas_observability"]},
        ],
    },
    "healthcare.json": {
        "domain": "Healthcare Software",
        "nodes": [
            {"id": "health_compliance", "name": "HIPAA / HITECH Compliance & Consent Rules", "prerequisites": []},
            {"id": "health_data_model", "name": "EHR / EMR Data Modeling & FHIR/HL7 Standards", "prerequisites": ["health_compliance"]},
            {"id": "health_security", "name": "End-to-End Encryption & Field-Level PHI Masking", "prerequisites": ["health_data_model"]},
            {"id": "health_clinical_rbac", "name": "Clinical Role-Based Access Control", "prerequisites": ["health_security"]},
            {"id": "health_triage", "name": "Patient Triage & Appointment Scheduling Engine", "prerequisites": ["health_clinical_rbac"]},
            {"id": "health_telemed", "name": "Secure WebRTC Telemedicine Streaming", "prerequisites": ["health_triage"]},
            {"id": "health_audit", "name": "Immutable Tamper-Evident Audit Logging", "prerequisites": ["health_telemed"]},
            {"id": "health_prescription", "name": "e-Prescription & Pharmacy Inventory Sync", "prerequisites": ["health_audit"]},
        ],
    },
    "weddings.json": {
        "domain": "Luxury Event & Wedding Planning",
        "nodes": [
            {"id": "wed_vision", "name": "Client Vision, Aesthetic & Theme Definition", "prerequisites": []},
            {"id": "wed_budget", "name": "Itemized Budget Allocation & Contingency Pool", "prerequisites": ["wed_vision"]},
            {"id": "wed_venue", "name": "Venue Scouting, Capacity & Contract Negotiation", "prerequisites": ["wed_budget"]},
            {"id": "wed_itinerary", "name": "Multi-Day Ceremony Timeline & Logistics Run-Sheet", "prerequisites": ["wed_venue"]},
            {"id": "wed_vendors", "name": "Catering (F&B), Decor & AV Vendor Coordination", "prerequisites": ["wed_itinerary"]},
            {"id": "wed_hospitality", "name": "Guest Logistics, Welcome Desk & Room Allocations", "prerequisites": ["wed_vendors"]},
            {"id": "wed_risk", "name": "Emergency Backup Protocols & Weather Contingencies", "prerequisites": ["wed_hospitality"]},
            {"id": "wed_recap", "name": "Post-Event Vendor Settlement & Final Reconciliation", "prerequisites": ["wed_risk"]},
        ],
    },
    "business_strategy.json": {
        "domain": "Business Strategy & Expansion",
        "nodes": [
            {"id": "biz_market", "name": "Market Sizing, TAM/SAM/SOM & Competitive Landscape", "prerequisites": []},
            {"id": "biz_value_prop", "name": "Unique Value Proposition & ICP Personas", "prerequisites": ["biz_market"]},
            {"id": "biz_unit_econ", "name": "Unit Economics, Margin Analysis & CAC/LTV Matrix", "prerequisites": ["biz_value_prop"]},
            {"id": "biz_gtm", "name": "Go-To-Market Channels & Customer Acquisition Strategy", "prerequisites": ["biz_unit_econ"]},
            {"id": "biz_supply_chain", "name": "Operations, Supply Chain & Vendor Quality Control", "prerequisites": ["biz_gtm"]},
            {"id": "biz_financials", "name": "3-Year Financial Model & Cash-Flow Projections", "prerequisites": ["biz_supply_chain"]},
            {"id": "biz_franchise", "name": "Franchise/Scaling Blueprint & Legal SOPs", "prerequisites": ["biz_financials"]},
            {"id": "biz_kpis", "name": "Executive OKRs & Operational Performance Dashboards", "prerequisites": ["biz_franchise"]},
        ],
    },
    "debugging.json": {
        "domain": "Diagnostic Engineering & RCA",
        "nodes": [
            {"id": "dbg_symptom", "name": "Symptom Triage, Stack Trace & Error Signature Isolation", "prerequisites": []},
            {"id": "dbg_repro", "name": "Minimal Deterministic Reproduction Environment", "prerequisites": ["dbg_symptom"]},
            {"id": "dbg_telemetry", "name": "Log Correlation, Metric Spikes & Trace Inspection", "prerequisites": ["dbg_repro"]},
            {"id": "dbg_rca", "name": "Hypothesis Testing & 5-Whys Root Cause Analysis", "prerequisites": ["dbg_telemetry"]},
            {"id": "dbg_patch", "name": "Defensive Patch Implementation & Code Fix", "prerequisites": ["dbg_rca"]},
            {"id": "dbg_regression", "name": "Regression Unit & Integration Tests", "prerequisites": ["dbg_patch"]},
            {"id": "dbg_canary", "name": "Canary Deployment & Production Monitoring", "prerequisites": ["dbg_regression"]},
            {"id": "dbg_postmortem", "name": "Blameless Post-Mortem & Preventative Architectural Guardrails", "prerequisites": ["dbg_canary"]},
        ],
    },
    "generic.json": {
        "domain": "General Purpose Execution Framework",
        "nodes": [
            {"id": "gen_decompose", "name": "Problem Decomposition & Requirement Elicitation", "prerequisites": []},
            {"id": "gen_architecture", "name": "Architecture Topology & System Boundaries", "prerequisites": ["gen_decompose"]},
            {"id": "gen_milestones", "name": "Phased Execution Milestones & Deliverables", "prerequisites": ["gen_architecture"]},
            {"id": "gen_implementation", "name": "High-Fidelity Implementation & Standards Compliance", "prerequisites": ["gen_milestones"]},
            {"id": "gen_qa", "name": "Verification, Testing & Quality Assurance", "prerequisites": ["gen_implementation"]},
            {"id": "gen_deployment", "name": "Operational Deployment, Monitoring & Runbooks", "prerequisites": ["gen_qa"]},
        ],
    },
    "education.json": {
        "domain": "Pedagogy & Curriculum Design",
        "nodes": [
            {"id": "edu_needs", "name": "Learner Profile & Prerequisite Diagnostic", "prerequisites": []},
            {"id": "edu_outcomes", "name": "Bloom's Taxonomy Learning Outcomes", "prerequisites": ["edu_needs"]},
            {"id": "edu_modules", "name": "Scaffolded Modular Syllabus Breakdown", "prerequisites": ["edu_outcomes"]},
            {"id": "edu_labs", "name": "Hands-on Exercises & Active Learning Tasks", "prerequisites": ["edu_modules"]},
            {"id": "edu_assess", "name": "Formative Quizzes & Milestone Checkpoints", "prerequisites": ["edu_labs"]},
            {"id": "edu_capstone", "name": "Independent Capstone Synthesis Project", "prerequisites": ["edu_assess"]},
        ],
    },
    "marketing.json": {
        "domain": "Marketing & Growth Strategy",
        "nodes": [
            {"id": "mkt_persona", "name": "Ideal Customer Profile (ICP) & Buyer Personas", "prerequisites": []},
            {"id": "mkt_positioning", "name": "Value Proposition & Brand Positioning Narrative", "prerequisites": ["mkt_persona"]},
            {"id": "mkt_funnel", "name": "Full-Funnel Acquisition & Retention Architecture", "prerequisites": ["mkt_positioning"]},
            {"id": "mkt_content", "name": "Content Strategy, SEO & Organic Flywheel", "prerequisites": ["mkt_funnel"]},
            {"id": "mkt_paid", "name": "Paid Channels, Ad Creative & Campaign Budgeting", "prerequisites": ["mkt_content"]},
            {"id": "mkt_cro", "name": "Conversion Rate Optimization (CRO) & A/B Testing", "prerequisites": ["mkt_paid"]},
            {"id": "mkt_attribution", "name": "Multi-Touch Attribution & CAC/LTV Metrics", "prerequisites": ["mkt_cro"]},
        ],
    },
    "design.json": {
        "domain": "UI/UX & Product Design",
        "nodes": [
            {"id": "des_research", "name": "User Research, Empathy Maps & Journey Flows", "prerequisites": []},
            {"id": "des_ia", "name": "Information Architecture & Site Taxonomy", "prerequisites": ["des_research"]},
            {"id": "des_wireframes", "name": "Low-Fidelity Wireframes & Interaction Models", "prerequisites": ["des_ia"]},
            {"id": "des_tokens", "name": "Design Systems, Tokens & Component Libraries", "prerequisites": ["des_wireframes"]},
            {"id": "des_prototype", "name": "High-Fidelity Interactive Prototypes", "prerequisites": ["des_tokens"]},
            {"id": "des_usability", "name": "Usability Testing & Accessibility (WCAG 2.1 AA)", "prerequisites": ["des_prototype"]},
        ],
    },
    "writing.json": {
        "domain": "Content Strategy & Technical Writing",
        "nodes": [
            {"id": "wri_audience", "name": "Audience Framing, Tone of Voice & Thesis", "prerequisites": []},
            {"id": "wri_outline", "name": "Structural Outline & Argumentation Flow", "prerequisites": ["wri_audience"]},
            {"id": "wri_drafting", "name": "First-Principles Draft Composition", "prerequisites": ["wri_outline"]},
            {"id": "wri_citations", "name": "Fact-Checking, Data Synthesis & Primary Citations", "prerequisites": ["wri_drafting"]},
            {"id": "wri_editing", "name": "Substantive Editing, Readability & Flow Polish", "prerequisites": ["wri_citations"]},
            {"id": "wri_cta", "name": "Headlines, Executive Summary & Call to Action", "prerequisites": ["wri_editing"]},
        ],
    },
    "research.json": {
        "domain": "Scientific & Academic Research",
        "nodes": [
            {"id": "res_hypo", "name": "Research Question & Literature Review", "prerequisites": []},
            {"id": "res_method", "name": "Methodological Design & Experimental Protocols", "prerequisites": ["res_hypo"]},
            {"id": "res_data", "name": "Data Collection, Sampling & Integrity Checks", "prerequisites": ["res_method"]},
            {"id": "res_analysis", "name": "Quantitative & Qualitative Statistical Analysis", "prerequisites": ["res_data"]},
            {"id": "res_findings", "name": "Synthesis of Findings, Novel Insights & Validation", "prerequisites": ["res_analysis"]},
            {"id": "res_ethics", "name": "Peer-Review Preparation, Ethics & Limitations", "prerequisites": ["res_findings"]},
        ],
    },
    "finance.json": {
        "domain": "Financial Modeling & Investment Analysis",
        "nodes": [
            {"id": "fin_accounting", "name": "Three-Statement Financial Modeling (P&L, Balance, Cash)", "prerequisites": []},
            {"id": "fin_dcf", "name": "Discounted Cash Flow (DCF) & Valuation Multiples", "prerequisites": ["fin_accounting"]},
            {"id": "fin_unit_econ", "name": "Unit Economics, Contribution Margin & Break-Even", "prerequisites": ["fin_dcf"]},
            {"id": "fin_sensitivity", "name": "Monte Carlo Simulation & Scenario Stress Testing", "prerequisites": ["fin_unit_econ"]},
            {"id": "fin_compliance", "name": "Regulatory Compliance (GAAP/IFRS) & Audit Readiness", "prerequisites": ["fin_sensitivity"]},
            {"id": "fin_risk", "name": "Capital Allocation & Treasury Risk Hedging", "prerequisites": ["fin_compliance"]},
        ],
    },
    "travel.json": {
        "domain": "Travel Planning & Tourism Logistics",
        "nodes": [
            {"id": "trv_destination", "name": "Destination Profiling, Visa Rules & Entry Protocols", "prerequisites": []},
            {"id": "trv_itinerary", "name": "Optimized Day-by-Day Geolocation Route Mapping", "prerequisites": ["trv_destination"]},
            {"id": "trv_transit", "name": "Intercity Transit, Flights & Local Commute Logistics", "prerequisites": ["trv_itinerary"]},
            {"id": "trv_lodging", "name": "Accommodation Curation & Neighborhood Vetting", "prerequisites": ["trv_transit"]},
            {"id": "trv_budget", "name": "Currency Management, Daily Per Diem & Reserve Pool", "prerequisites": ["trv_lodging"]},
            {"id": "trv_emergency", "name": "Health Insurance, Embassy Contacts & Safety Protocols", "prerequisites": ["trv_budget"]},
        ],
    },
    "legal.json": {
        "domain": "Legal Strategy & Contract Analysis",
        "nodes": [
            {"id": "leg_jurisdiction", "name": "Jurisdiction, Governing Law & Regulatory Landscape", "prerequisites": []},
            {"id": "leg_clauses", "name": "Core Contractual Clauses & Obligations Analysis", "prerequisites": ["leg_jurisdiction"]},
            {"id": "leg_ip", "name": "Intellectual Property Ownership & Assignment Terms", "prerequisites": ["leg_clauses"]},
            {"id": "leg_indemnity", "name": "Indemnification, Liability Caps & Risk Allocation", "prerequisites": ["leg_ip"]},
            {"id": "leg_compliance", "name": "Statutory Compliance Audit & Data Privacy (GDPR/CCPA)", "prerequisites": ["leg_indemnity"]},
            {"id": "leg_dispute", "name": "Dispute Resolution, Arbitration & Termination Protocols", "prerequisites": ["leg_compliance"]},
        ],
    },
    "creative.json": {
        "domain": "Creative Media & Multimedia Production",
        "nodes": [
            {"id": "cre_concept", "name": "Creative Concept Brief & Core Visual Theme", "prerequisites": []},
            {"id": "cre_moodboard", "name": "Art Direction, Palette & Aesthetic References", "prerequisites": ["cre_concept"]},
            {"id": "cre_storyboard", "name": "Scene-by-Scene Storyboarding & Narrative Pacing", "prerequisites": ["cre_moodboard"]},
            {"id": "cre_production", "name": "Asset Production Pipeline & Tooling Setup", "prerequisites": ["cre_storyboard"]},
            {"id": "cre_review", "name": "Editorial Review, Sound Design & Color Grading", "prerequisites": ["cre_production"]},
            {"id": "cre_export", "name": "Multi-Platform Export, Encoding & Quality Sign-Off", "prerequisites": ["cre_review"]},
        ],
    },
}

if __name__ == "__main__":
    for fname, data in graphs.items():
        p = cg_dir / fname
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {p.name} with {len(data['nodes'])} nodes")
