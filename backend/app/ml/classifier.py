"""Autonomous Local ML Classification Heads with Dual-Mode (ML & Rules Fallback) Execution."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from app.ml.embeddings import EmbeddingEngine

logger = logging.getLogger("intentify.ml.classifier")


@dataclass
class ClassificationResult:
    """Standard container for ML classification predictions."""

    label: str
    confidence: float
    probabilities: dict[str, float] = field(default_factory=dict)
    engine_mode: str = "rules_fallback"
    top_k: list[tuple[str, float]] = field(default_factory=list)


class BaseClassifier:
    """Base class for local ML classifiers with safe non-throwing default implementation."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path) if model_path else None
        self._is_loaded = False
        self._embedding_engine = EmbeddingEngine()
        self.engine_mode = "rules_fallback"

    def predict(self, text: str) -> ClassificationResult:
        """Safe default prediction that does not raise NotImplementedError."""
        clean = (text or "").strip()
        if not clean:
            return ClassificationResult(
                label="general",
                confidence=0.5,
                probabilities={"general": 1.0},
                engine_mode=self.engine_mode,
            )
        return ClassificationResult(
            label="general",
            confidence=0.7,
            probabilities={"general": 0.7, "other": 0.3},
            engine_mode=self.engine_mode,
        )

    def predict_batch(self, texts: list[str]) -> list[ClassificationResult]:
        return [self.predict(t) for t in texts]


class IntentClassifierML(BaseClassifier):
    """ML-backed intent classifier supporting local neural weights and intelligent rules fallback."""

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "create": ["create", "build", "make", "develop", "implement", "construct", "બનાવો", "બનાવવું", "તૈયાર કરો", "બનાવ"],
        "plan": ["plan", "roadmap", "strategy", "timeline", "આયોજન", "પ્લાન", "યોજના", "તૈયારી"],
        "debug": ["debug", "fix", "error", "bug", "traceback", "exception", "crash", "સુધારો", "ભૂલ", "સોલ્વ"],
        "explain": ["explain", "understand", "what is", "how does", "સમજાવો", "શું છે", "કેવી રીતે"],
        "design": ["design", "ui", "ux", "wireframe", "mockup", "ડિઝાઇન", "આર્કિટેક્ચર"],
        "analyze": ["analyze", "evaluate", "audit", "benchmark", "વિશ્લેષણ", "ચકાસણી"],
        "improve": ["improve", "optimize", "refactor", "scale", "સુધારણા", "ઝડપી"],
        "research": ["research", "survey", "investigate", "અભ્યાસ", "સંશોધન"],
        "learn": ["learn", "study", "curriculum", "tutorial", "શીખવું", "શીખ", "સીખના"],
        "write": ["write", "draft", "compose", "લખો", "લખવું"],
    }

    def __init__(self, model_path: str | Path | None = None) -> None:
        super().__init__(model_path)
        self.classes: list[str] = [
            "create", "plan", "debug", "explain", "design",
            "analyze", "improve", "research", "learn", "write",
        ]
        self._weights: dict[str, np.ndarray] | None = None
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        """Attempt to load trained weights; if valid, activate 'ml' engine mode."""
        base_dir = Path(__file__).resolve().parents[3] / "ml-engine" / "models" / "intent_model"
        weights_file = base_dir / "weights.npz"
        meta_file = base_dir / "metadata.json"

        if weights_file.exists() and meta_file.exists():
            try:
                with open(meta_file, encoding="utf-8") as f:
                    meta = json.load(f)
                loaded_classes = meta.get("classes", [])
                if loaded_classes and meta.get("train_accuracy", 0.0) >= 0.50:
                    self.classes = loaded_classes
                    self._weights = dict(np.load(weights_file))
                    self._is_loaded = True
                    self.engine_mode = "ml"
                    logger.info("IntentClassifierML loaded neural weights (accuracy: %s)", meta.get("train_accuracy"))
                    return
            except Exception as e:
                logger.warning("Could not load neural intent weights: %s. Using rules fallback.", e)

        self.engine_mode = "rules_fallback"

    def predict(self, text: str) -> ClassificationResult:
        clean = (text or "").lower().strip()
        if not clean:
            return ClassificationResult(label="create", confidence=0.5, engine_mode=self.engine_mode)

        # 1. Neural forward pass if high-quality model weights are available
        if self._is_loaded and self._weights:
            try:
                emb = self._embedding_engine.encode_single(clean)
                w0, b0 = self._weights["w_0"], self._weights["b_0"]
                w1, b1 = self._weights["w_1"], self._weights["b_1"]
                w2, b2 = self._weights["w_2"], self._weights["b_2"]

                h1 = np.maximum(0, np.dot(emb, w0) + b0)
                h2 = np.maximum(0, np.dot(h1, w1) + b1)
                logits = np.dot(h2, w2) + b2
                exp_logits = np.exp(logits - np.max(logits))
                probs = (exp_logits / np.sum(exp_logits)).flatten()

                top_idx = int(np.argmax(probs))
                pred_label = self.classes[top_idx] if top_idx < len(self.classes) else "create"
                prob_dict = {self.classes[i]: float(probs[i]) for i in range(min(len(self.classes), len(probs)))}

                return ClassificationResult(
                    label=pred_label,
                    confidence=float(probs[top_idx]),
                    probabilities=prob_dict,
                    engine_mode="ml",
                )
            except Exception as e:
                logger.warning("Neural forward pass failed, switching to rules_fallback: %s", e)

        # 2. Semantic Rules Fallback
        scores: dict[str, float] = {c: 0.05 for c in self.classes}

        # Check keyword matches
        for intent, kw_list in self.INTENT_KEYWORDS.items():
            for kw in kw_list:
                if kw in clean:
                    scores[intent] = scores.get(intent, 0.0) + 1.0

        # Normalization
        total = sum(scores.values()) or 1.0
        prob_dict = {k: round(v / total, 4) for k, v in scores.items()}
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        best_label, best_conf = sorted_probs[0]

        return ClassificationResult(
            label=best_label,
            confidence=max(0.65, best_conf),
            probabilities=prob_dict,
            engine_mode="rules_fallback",
            top_k=sorted_probs[:3],
        )


class DomainClassifierML(BaseClassifier):
    """ML-backed domain classifier with neural weights and semantic fallback."""

    DOMAIN_SIGNALS: dict[str, list[str]] = {
        "Education & Learning": ["learn", "study", "curriculum", "syllabus", "student", "teacher", "tutorial", "શીખવું", "કોર્સ", "પરીક્ષા"],
        "SaaS Web Applications": ["scheduling", "saas", "dashboard", "subscription", "calendar sync", "booking website", "web app", "portal"],
        "Healthcare & Clinical": ["patient", "doctor", "clinical", "hospital", "diagnosis", "dosage", "medical", "તબીબી", "દવા", "સારવાર"],
        "Event Planning & Weddings": ["wedding", "marriage", "ceremony", "reception", "udaipur", "destination wedding", "લગ્ન", "મંડપ", "ઇવેન્ટ"],
        "Debugging & Diagnostics": ["nullpointerexception", "stacktrace", "traceback", "segfault", "error", "bug", "crash", "fix this error"],
        "Financial Architecture": ["portfolio", "banking", "investment", "fintech", "trading", "equity", "hedge fund", "sec", "finra"],
        "Specialized Engineering": ["hardware", "circuit", "robotics", "drone", "embedded", "mechanical", "electrical"],
    }

    def __init__(self, model_path: str | Path | None = None) -> None:
        super().__init__(model_path)
        self.classes: list[str] = list(self.DOMAIN_SIGNALS.keys())
        self._weights: dict[str, np.ndarray] | None = None
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        base_dir = Path(__file__).resolve().parents[3] / "ml-engine" / "models" / "domain_model"
        weights_file = base_dir / "weights.npz"
        meta_file = base_dir / "metadata.json"
        if weights_file.exists() and meta_file.exists():
            try:
                with open(meta_file, encoding="utf-8") as f:
                    meta = json.load(f)
                loaded_classes = meta.get("classes", [])
                if loaded_classes and meta.get("train_accuracy", 0.0) >= 0.50:
                    self.classes = loaded_classes
                    self._weights = dict(np.load(weights_file))
                    self._is_loaded = True
                    self.engine_mode = "ml"
                    return
            except Exception as e:
                logger.warning("Could not load neural domain weights: %s", e)
        self.engine_mode = "rules_fallback"

    def predict(self, text: str) -> ClassificationResult:
        clean = (text or "").lower().strip()
        if not clean:
            return ClassificationResult(label="General Software", confidence=0.5, engine_mode=self.engine_mode)

        if self._is_loaded and self._weights:
            try:
                emb = self._embedding_engine.encode_single(clean)
                w0, b0 = self._weights["w_0"], self._weights["b_0"]
                w1, b1 = self._weights["w_1"], self._weights["b_1"]
                h1 = np.maximum(0, np.dot(emb, w0) + b0)
                logits = np.dot(h1, w1) + b1
                exp_logits = np.exp(logits - np.max(logits))
                probs = (exp_logits / np.sum(exp_logits)).flatten()
                top_idx = int(np.argmax(probs))
                pred_label = self.classes[top_idx] if top_idx < len(self.classes) else "Software Development"
                prob_dict = {self.classes[i]: float(probs[i]) for i in range(min(len(self.classes), len(probs)))}
                sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
                return ClassificationResult(
                    label=pred_label,
                    confidence=float(probs[top_idx]),
                    probabilities=prob_dict,
                    engine_mode="ml",
                    top_k=sorted_probs[:3],
                )
            except Exception as e:
                logger.warning("Neural domain pass failed: %s", e)

        scores: dict[str, float] = {d: 0.05 for d in self.DOMAIN_SIGNALS}
        for domain, keywords in self.DOMAIN_SIGNALS.items():
            for kw in keywords:
                if kw in clean:
                    scores[domain] = scores.get(domain, 0.0) + 1.2

        total = sum(scores.values()) or 1.0
        prob_dict = {k: round(v / total, 4) for k, v in scores.items()}
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        best_label, best_conf = sorted_probs[0]

        return ClassificationResult(
            label=best_label,
            confidence=max(0.70, best_conf),
            probabilities=prob_dict,
            engine_mode="rules_fallback",
            top_k=sorted_probs[:3],
        )


class RoleClassifierML(BaseClassifier):
    """ML-backed role classifier with neural weights and intelligent persona resolution."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        super().__init__(model_path)
        self.classes: list[str] = []
        self._weights: dict[str, np.ndarray] | None = None
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        base_dir = Path(__file__).resolve().parents[3] / "ml-engine" / "models" / "role_model"
        weights_file = base_dir / "weights.npz"
        meta_file = base_dir / "metadata.json"
        if weights_file.exists() and meta_file.exists():
            try:
                with open(meta_file, encoding="utf-8") as f:
                    meta = json.load(f)
                loaded_classes = meta.get("classes", [])
                if loaded_classes and meta.get("train_accuracy", 0.0) >= 0.50:
                    self.classes = loaded_classes
                    self._weights = dict(np.load(weights_file))
                    self._is_loaded = True
                    self.engine_mode = "ml"
                    return
            except Exception as e:
                logger.warning("Could not load neural role weights: %s", e)
        self.engine_mode = "rules_fallback"

    def predict(self, text: str) -> ClassificationResult:
        clean = (text or "").lower().strip()
        if not clean:
            return ClassificationResult(label="Principal Software Architect", confidence=0.5, engine_mode=self.engine_mode)

        if self._is_loaded and self._weights:
            try:
                emb = self._embedding_engine.encode_single(clean)
                w0, b0 = self._weights["w_0"], self._weights["b_0"]
                w1, b1 = self._weights["w_1"], self._weights["b_1"]
                h1 = np.maximum(0, np.dot(emb, w0) + b0)
                logits = np.dot(h1, w1) + b1
                exp_logits = np.exp(logits - np.max(logits))
                probs = (exp_logits / np.sum(exp_logits)).flatten()
                top_idx = int(np.argmax(probs))
                pred_label = self.classes[top_idx] if top_idx < len(self.classes) else "Software Engineer"
                prob_dict = {self.classes[i]: float(probs[i]) for i in range(min(len(self.classes), len(probs)))}
                sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
                return ClassificationResult(
                    label=pred_label,
                    confidence=float(probs[top_idx]),
                    probabilities=prob_dict,
                    engine_mode="ml",
                    top_k=sorted_probs[:3],
                )
            except Exception as e:
                logger.warning("Neural role pass failed: %s", e)

        role = "Principal Software Architect"
        if any(w in clean for w in ["learn", "teach", "student", "study", "શીખવું"]):
            role = "Pedagogical Curriculum Designer & Technical Instructor"
        elif any(w in clean for w in ["wedding", "marriage", "ceremony", "udaipur", "લગ્ન"]):
            role = "Senior Luxury Destination Wedding Planner & Event Architect"
        elif any(w in clean for w in ["error", "exception", "bug", "traceback", "fix", "crash"]):
            role = "Principal Systems Reliability & Diagnostic Debugging Specialist"
        elif any(w in clean for w in ["patient", "clinical", "medical", "hospital", "doctor"]):
            role = "Chief Clinical Specialist & Medical Systems Director"
        elif any(w in clean for w in ["scheduling", "saas", "calendar", "booking"]):
            role = "Senior Full Stack SaaS Architect"

        return ClassificationResult(
            label=role,
            confidence=0.88,
            probabilities={role: 0.88, "Technical Advisor": 0.12},
            engine_mode=self.engine_mode,
        )
