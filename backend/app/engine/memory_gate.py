"""MemoryGate – Quality-gated admission, validation, and deduplication for the self-learning memory store."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("intentify.engine.memory_gate")


class MemoryGate:
    """Enforces strict admission criteria for persistent learning memory, purging corrupted and contaminated records."""

    def __init__(self, store_path: str | Path | None = None) -> None:
        if store_path:
            self.store_path = Path(store_path)
        else:
            self.store_path = Path(__file__).resolve().parents[3] / "ml-engine" / "memory" / "learning_store.json"

    def purge_corrupted_memories(self) -> dict[str, int]:
        """Scan learning_store.json, remove corrupt/cross-contaminated entries, and deduplicate on (goal, domain, intent)."""
        if not self.store_path.exists():
            logger.warning("Memory store not found at %s", self.store_path)
            return {"scanned": 0, "purged": 0, "retained": 0}

        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("Failed to load memory store: %s", e)
            return {"scanned": 0, "purged": 0, "retained": 0}

        memories = data.get("memories", [])
        scanned = len(memories)
        retained_memories: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str, str]] = set()
        purged = 0

        for m in memories:
            goal = str(m.get("goal", "")).strip()
            domain = str(m.get("domain", "")).strip()
            intent = str(m.get("intent", "")).strip()
            score = float(m.get("quality_score", 0.0))
            assumptions = " ".join(m.get("smart_assumptions", [])).lower()

            # Rule 1: Minimum Quality Score Gate
            if score < 85.0:
                logger.info("Purging low-score memory %s (score: %.1f)", m.get("id"), score)
                purged += 1
                continue

            # Rule 2: Goal Echo Artifacts
            if re.search(r"\b(?:a\s+want\s+to|build\s+a\s+mare|mare\s+wedding|mujhe\s+chahiye)\b", goal, re.IGNORECASE):
                logger.info("Purging goal-echo memory %s ('%s')", m.get("id"), goal)
                purged += 1
                continue

            # Rule 3: Severe Domain Contamination (e.g. Wedding with Finance / SEC / FINRA)
            if "wedding" in goal.lower() and domain.lower() == "finance":
                logger.info("Purging contaminated wedding-finance memory %s", m.get("id"))
                purged += 1
                continue

            if ("wedding" in goal.lower() or "restaurant" in goal.lower()) and any(w in assumptions for w in ["sec", "finra", "double-entry bookkeeping"]):
                logger.info("Purging contaminated SEC/FINRA memory %s", m.get("id"))
                purged += 1
                continue

            # Rule 4: Deduplicate on (normalized_goal, domain, intent)
            norm_goal = re.sub(r"[^\w\s]", "", goal.lower()).strip()
            dedup_key = (norm_goal, domain.lower(), intent.lower())
            if dedup_key in seen_keys:
                logger.info("Purging duplicate memory %s for goal '%s'", m.get("id"), goal)
                purged += 1
                continue

            seen_keys.add(dedup_key)
            retained_memories.append(m)

        # Re-index IDs sequentially
        for idx, m in enumerate(retained_memories, 1):
            m["id"] = f"mem_{idx:05d}"

        data["memories"] = retained_memories

        # Save cleaned file back
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("MemoryGate purge complete: %d scanned, %d purged, %d retained.", scanned, purged, len(retained_memories))
        return {
            "scanned": scanned,
            "purged": purged,
            "retained": len(retained_memories),
        }

    def validate_admission(
        self,
        goal: str,
        domain: str,
        quality_score: float,
        assumptions: list[str] | None = None,
    ) -> bool:
        """Validate whether a newly generated prompt meets quality standards to be admitted into learning memory."""
        if quality_score < 85.0:
            return False

        # Check goal echo
        if re.search(r"\b(?:a\s+want\s+to|build\s+a\s+mare|mare\s+wedding|mujhe\s+chahiye)\b", goal, re.IGNORECASE):
            return False

        # Check domain contamination
        if "wedding" in goal.lower() and domain.lower() == "finance":
            return False

        assump_text = " ".join(assumptions or []).lower()
        if "wedding" in goal.lower() and any(w in assump_text for w in ["sec", "finra"]):
            return False

        return True


# Alias for backward and forward compatibility
MemoryAdmissionGate = MemoryGate
