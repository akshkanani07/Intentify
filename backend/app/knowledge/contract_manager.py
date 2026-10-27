"""ContractManager – Loads and validates declarative Master Prompt contracts."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("intentify.knowledge.contract_manager")


@dataclass
class ContractSection:
    heading: str
    min_items: int = 1
    description: str = ""


@dataclass
class OptionalSection:
    heading: str
    trigger_keywords: list[str] = field(default_factory=list)
    out_of_scope_message: str = ""


@dataclass
class ContractDefinition:
    contract: str
    name: str
    description: str
    required_sections: list[ContractSection] = field(default_factory=list)
    optional_sections: list[OptionalSection] = field(default_factory=list)

    @property
    def required_headings(self) -> list[str]:
        return [s.heading for s in self.required_sections]


class ContractManager:
    """Manages declarative prompt contracts loaded from knowledge-base/contracts/."""

    def __init__(self, contracts_dir: Path | str | None = None) -> None:
        if contracts_dir is None:
            # Find knowledge-base/contracts
            base = Path(__file__).resolve()
            for _ in range(5):
                base = base.parent
                cand = base / "knowledge-base" / "contracts"
                if cand.exists():
                    contracts_dir = cand
                    break
            if contracts_dir is None:
                contracts_dir = Path("knowledge-base/contracts")

        self.contracts_dir = Path(contracts_dir)
        self._contracts: dict[str, ContractDefinition] = {}
        self._load_all_contracts()

    def _load_all_contracts(self) -> None:
        if not self.contracts_dir.exists():
            logger.warning("Contracts directory not found: %s", self.contracts_dir)
            return

        for p in self.contracts_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                req_sections = [
                    ContractSection(
                        heading=s.get("heading", ""),
                        min_items=s.get("min_items", 1),
                        description=s.get("description", ""),
                    )
                    for s in data.get("required_sections", [])
                ]
                opt_sections = [
                    OptionalSection(
                        heading=s.get("heading", ""),
                        trigger_keywords=s.get("trigger_keywords", []),
                        out_of_scope_message=s.get("out_of_scope_message", ""),
                    )
                    for s in data.get("optional_sections", [])
                ]
                defn = ContractDefinition(
                    contract=data.get("contract", p.stem),
                    name=data.get("name", p.stem),
                    description=data.get("description", ""),
                    required_sections=req_sections,
                    optional_sections=opt_sections,
                )
                self._contracts[defn.contract] = defn
            except Exception as e:
                logger.error("Failed to load contract %s: %s", p, e)

        logger.info("Loaded %d contracts: %s", len(self._contracts), list(self._contracts.keys()))

    def get_contract(self, name: str) -> ContractDefinition | None:
        return self._contracts.get(name.lower())

    def list_contracts(self) -> list[str]:
        return list(self._contracts.keys())
