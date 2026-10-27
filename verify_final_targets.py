"""Verify all 6 core user test inputs across the Cognitive Prompt Compiler Engine."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "backend"))
sys.path.insert(0, str(BASE / "ml-engine"))

from app.engine.composer import PromptComposer
from app.engine.planner import KnowledgePlanner
from app.engine.quality_engine import QualityEngine
from app.engine.reranker import CandidateReranker
from app.engine.spec_extractor import SpecExtractor

extractor = SpecExtractor()
planner = KnowledgePlanner()
composer = PromptComposer()
quality = QualityEngine()
reranker = CandidateReranker(planner=planner, composer=composer, quality_engine=quality)

test_targets = [
    {
        "id": "1",
        "input": "want to learn c++",
        "language_override": "",
        "expected_lang": "English",
        "description": "Pedagogical request in English",
    },
    {
        "id": "2",
        "input": "મારે Java શીખવું છે",
        "language_override": "",
        "expected_lang": "Gujarati",
        "description": "Pedagogical request in Gujarati",
    },
    {
        "id": "3",
        "input": "Build a scheduling website with calendar sync",
        "language_override": "",
        "expected_lang": "English",
        "description": "Full-Stack SaaS architecture in English",
    },
    {
        "id": "4",
        "input": "fix this NullPointerException",
        "language_override": "",
        "expected_lang": "English",
        "description": "Diagnostic RCA and patching in English",
    },
    {
        "id": "5",
        "input": "kuch banao",
        "language_override": "",
        "expected_lang": "Hindi",
        "description": "Vague conversational request in Hindi",
    },
    {
        "id": "6",
        "input": "organic farming app",
        "language_override": "",
        "expected_lang": "English",
        "description": "Novel open-domain application",
    },
]

print("================================================================================")
print(" Intentify AI — 6 Core Target Test Inputs Final Verification")
print("================================================================================\n")

for target in test_targets:
    t_id = target["id"]
    inp = target["input"]
    desc = target["description"]
    lang_over = target["language_override"]
    exp_lang = target["expected_lang"]

    spec = extractor.extract(text=inp, language_hint=lang_over)
    winner, _ = reranker.generate_and_rerank(spec)

    print(f"[{t_id}/6] INPUT: \"{inp}\" ({desc})")
    print(f"       Detected Input Lang : {spec.input_language}")
    print(f"       Target Output Lang  : {spec.output_language} (Matches Expected: {spec.output_language == exp_lang})")
    print(f"       Action / Goal       : {spec.action} -> {spec.object_subject}")
    print(f"       Domain              : {spec.domain}")
    print(f"       Audience / Level    : {spec.audience} ({spec.proficiency})")
    print(f"       Persona Role        : {spec.persona_role}")
    print(f"       Quality Score       : {winner.audit.total_score}/100.0 (Candidate Style: {winner.style})")
    print(f"       Penalties           : {winner.audit.penalties or 'Zero penalties (Flawless)'}")
    print("--------------------------------------------------------------------------------")
    print("       MASTER PROMPT SAMPLE (First 400 chars):")
    prompt_sample = winner.full_text[:400].replace("\n", "\n       ")
    print(f"       {prompt_sample}")
    print("       ...\n")

    assert spec.output_language == exp_lang, f"Language mismatch for {inp}: got {spec.output_language}, expected {exp_lang}"
    assert winner.audit.total_score >= 85.0, f"Score below 85.0 for {inp}: got {winner.audit.total_score}"

print("================================================================================")
print(" All 6 target test inputs passed verification with 100% compliance!")
print("================================================================================")
