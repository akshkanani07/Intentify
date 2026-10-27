"""Entity extraction engine using pattern matching and NER semantics across 6 entity classes."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, asdict

logger = logging.getLogger("intentify.nlp.entity_extractor")


@dataclass
class Entity:
    """Extracted named entity or domain term."""

    text: str
    label: str
    start: int
    end: int
    confidence: float = 0.9

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class EntityExtractor:
    """Extracts entities across: TECHNOLOGY, PLATFORM, LOCATION, METRIC, BUDGET, and TIMEFRAME."""

    TECH_PATTERNS = [
        r"\b(?:Python|JavaScript|TypeScript|React|Next\.?js|Vue|FastAPI|Django|Flask|Node\.?js|Express|Docker|Kubernetes|AWS|GCP|Azure|PostgreSQL|MySQL|SQLite|Redis|MongoDB|Cassandra|GraphQL|REST\s*API|PyTorch|TensorFlow|Tailwind|Bootstrap|SQL|HTML5?|CSS3?|Go|Golang|Rust|Java|Spring\s*Boot|C\+\+|C#|\.NET|Kafka|RabbitMQ|Elasticsearch|Solr|Nginx|Apache)\b",
    ]

    PLATFORM_PATTERNS = [
        r"\b(?:iOS|Android|Web|Linux|Ubuntu|Debian|CentOS|Windows|macOS|Cloud|Serverless|Microservices|SaaS|Mobile|Desktop|Cross-platform|Bare-metal)\b",
    ]

    LOCATION_PATTERNS = [
        # Indian cities & regions
        r"\b(?:Udaipur|Mumbai|Delhi|Bengaluru|Bangalore|Ahmedabad|Jaipur|Surat|Hyderabad|Pune|Chennai|Kolkata|Goa|Kerala|Gujarat|Rajasthan)\b",
        # International tech hubs & capitals
        r"\b(?:San Francisco|Silicon Valley|New York|London|Berlin|Tokyo|Singapore|Dubai|Paris|Toronto|Sydney|Seattle|Austin|Zurich)\b",
        # Cloud regions
        r"\b(?:us-east-1|us-west-2|eu-central-1|ap-south-1|on-premise|remote)\b",
    ]

    METRIC_PATTERNS = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*(?:percent|ms|milliseconds|seconds|mins|hours|qps|rpm|tps|gb|mb|tb|users|concurrent|rps)\b",
        r"\b(?:99\.9+%?|sub-millisecond|zero-downtime)\b",
    ]

    BUDGET_PATTERNS = [
        r"\$\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:k|m|million|billion)?\b",
        r"(?:USD|EUR|GBP|INR|Rs\.?|₹)\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:k|m|lakh|crore|million)?\b",
        r"\b\d+(?:,\d+)*\s*(?:dollars?|usd|eur|inr|rupees?|lakh|crores?|bucks?)\b",
    ]

    TIMEFRAME_PATTERNS = [
        r"\b(?:within|in|by)\s+\d+\s+(?:days?|weeks?|months?|hours?|years?)\b",
        r"\b(?:within\s+\d+|in\s+\d+)\s+(?:divas|hafte|mahina|ghante)\b",
        r"\b(?:Q[1-4]\s*\d{2,4}|end of year|end of quarter|eod|tomorrow|asap|next week|by Dec\w*\s*\d{1,2})\b",
    ]

    def extract(self, text: str) -> list[Entity]:
        """Extract all recognized entities from input text."""
        if not text or not text.strip():
            return []

        entities: list[Entity] = []
        seen_spans: set[tuple[int, int]] = set()

        def _add_matches(patterns: list[str], label: str) -> None:
            for pat in patterns:
                for match in re.finditer(pat, text, re.IGNORECASE):
                    span = (match.start(), match.end())
                    if not any(s <= span[0] and span[1] <= e for s, e in seen_spans):
                        seen_spans.add(span)
                        entities.append(
                            Entity(
                                text=match.group(0).strip(),
                                label=label,
                                start=span[0],
                                end=span[1],
                                confidence=0.92,
                            )
                        )

        # 1. Budget / Currency
        _add_matches(self.BUDGET_PATTERNS, "BUDGET")

        # 2. Locations
        _add_matches(self.LOCATION_PATTERNS, "LOCATION")

        # 3. Technologies
        _add_matches(self.TECH_PATTERNS, "TECHNOLOGY")

        # 4. Platforms
        _add_matches(self.PLATFORM_PATTERNS, "PLATFORM")

        # 5. Metrics
        _add_matches(self.METRIC_PATTERNS, "METRIC")

        # 6. Timeframes
        _add_matches(self.TIMEFRAME_PATTERNS, "TIMEFRAME")

        entities.sort(key=lambda e: e.start)
        return entities
