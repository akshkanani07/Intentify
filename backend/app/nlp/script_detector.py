"""Script Detection Engine – fine-grained Unicode block decomposition."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.nlp.script_detector")


@dataclass
class ScriptProfile:
    """Detailed script distribution of input text."""

    primary_script: str
    script_counts: dict[str, int] = field(default_factory=dict)
    script_percentages: dict[str, float] = field(default_factory=dict)
    is_mixed: bool = False
    total_characters: int = 0


class ScriptDetector:
    """Classifies Unicode codepoints into linguistic scripts and computes distribution profiles."""

    SCRIPT_RANGES: dict[str, list[tuple[int, int]]] = {
        "Gujarati": [(0x0A80, 0x0AFF)],
        "Devanagari": [(0x0900, 0x097F), (0xA8E0, 0xA8FF)],
        "Arabic": [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
        "Han": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x20000, 0x2A6DF)],
        "Hiragana": [(0x3040, 0x309F)],
        "Katakana": [(0x30A0, 0x30FF)],
        "Tamil": [(0x0B80, 0x0BFF)],
        "Telugu": [(0x0C00, 0x0C7F)],
        "Cyrillic": [(0x0400, 0x04FF), (0x0500, 0x052F)],
        "Latin": [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F), (0x1E00, 0x1EFF)],
    }

    def detect(self, text: str) -> ScriptProfile:
        """Alias for analyze_scripts to conform to engine detector interfaces."""
        return self.analyze_scripts(text)

    def detect_script(self, text: str) -> str:
        """Return the single primary script name."""
        profile = self.analyze_scripts(text)
        return profile.primary_script

    def analyze_scripts(self, text: str) -> ScriptProfile:
        """Compute full per-script character count and distribution percentages."""
        if not text or not text.strip():
            return ScriptProfile(
                primary_script="Latin",
                script_counts={"Latin": 0},
                script_percentages={"Latin": 100.0},
                is_mixed=False,
                total_characters=0,
            )

        counts: dict[str, int] = {script: 0 for script in self.SCRIPT_RANGES}
        counts["Japanese"] = 0
        total_counted = 0

        for char in text:
            cp = ord(char)
            matched = False
            for script_name, ranges in self.SCRIPT_RANGES.items():
                if any(start <= cp <= end for start, end in ranges):
                    counts[script_name] += 1
                    total_counted += 1
                    matched = True
                    break

        # Consolidate Hiragana & Katakana into Japanese
        counts["Japanese"] = counts.pop("Hiragana", 0) + counts.pop("Katakana", 0)

        if total_counted == 0:
            return ScriptProfile(
                primary_script="Latin",
                script_counts={"Latin": 0},
                script_percentages={"Latin": 100.0},
                is_mixed=False,
                total_characters=len(text),
            )

        # Filter out 0 counts
        active_counts = {k: v for k, v in counts.items() if v > 0}
        percentages = {k: round((v / total_counted) * 100.0, 2) for k, v in active_counts.items()}

        sorted_scripts = sorted(active_counts.items(), key=lambda kv: kv[1], reverse=True)
        primary_script = sorted_scripts[0][0]

        # Mixed script determination: secondary script has >= 10% or >= 3 chars
        is_mixed = False
        if len(sorted_scripts) > 1:
            sec_count = sorted_scripts[1][1]
            sec_pct = percentages.get(sorted_scripts[1][0], 0.0)
            if sec_pct >= 10.0 or sec_count >= 3:
                is_mixed = True

        return ScriptProfile(
            primary_script=primary_script,
            script_counts=active_counts,
            script_percentages=percentages,
            is_mixed=is_mixed,
            total_characters=total_counted,
        )
