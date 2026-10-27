"""TemplateEngine – Jinja2-compatible template rendering for prompt compilation."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("intentify.compiler.template_engine")


@dataclass
class Template:
    """Represents a named prompt template."""

    name: str
    content: str
    variables: list[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.variables:
            # Extract variables from {var_name} patterns
            self.variables = re.findall(r"\{([a-zA-Z0-9_]+)\}", self.content)


class TemplateEngine:
    """Renders prompt templates with variable interpolation and fallbacks."""

    def __init__(self) -> None:
        self._templates: dict[str, Template] = {}

    def register_template(self, name: str, content: str, description: str = "") -> Template:
        """Register a template by name."""
        template = Template(name=name, content=content, description=description)
        self._templates[name] = template
        return template

    def get_template(self, name: str) -> Template | None:
        """Retrieve a registered template by name."""
        return self._templates.get(name)

    def render(self, template_str_or_name: str, variables: dict[str, Any]) -> str:
        """Render a template string or registered template name with provided variables."""
        if template_str_or_name in self._templates:
            template_content = self._templates[template_str_or_name].content
        else:
            template_content = template_str_or_name

        def replace_var(match: re.Match[str]) -> str:
            key = match.group(1)
            val = variables.get(key)
            if val is None:
                return ""
            if isinstance(val, list):
                return "\n".join(f"- {item}" for item in val if str(item).strip())
            return str(val)

        rendered = re.sub(r"\{([a-zA-Z0-9_]+)\}", replace_var, template_content)
        # Clean up any excessive blank lines created by empty variable replacements
        cleaned = re.sub(r"\n{3,}", "\n\n", rendered)
        return cleaned.strip()

    def render_section(self, header: str, items: list[str] | str, bullet: bool = True) -> str:
        """Helper to render a cleanly formatted section."""
        if not items:
            return ""
        if isinstance(items, str):
            content = items.strip()
        elif bullet:
            content = "\n".join(f"- {item}" for item in items if item and item.strip())
        else:
            content = "\n".join(item for item in items if item and item.strip())

        if not content:
            return ""
        return f"### {header}\n{content}"
