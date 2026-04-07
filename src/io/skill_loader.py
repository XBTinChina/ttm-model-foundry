"""Minimal skill-folder loader.

Skill markdown files use a simple convention: each field from the templates in
\u00a711 is rendered as a level-2 heading whose body is either prose or a bullet
list. This loader parses the bullet-list sections we need at parity-test time:

  ``## Compatible primitives``  \u2192 list of dotted module paths
  ``## Key dependent measures``  \u2192 list of analyzer function names

Other sections are ignored. The richer agent-facing loader (Step 11, future)
will return entire markdown bodies on demand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
MODELS_SKILLS_DIR = SKILLS_DIR / "models"
EXPERIMENTS_SKILLS_DIR = SKILLS_DIR / "experiments"

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
# Match a bullet line and extract its first identifier-like token. Prefers a
# backticked token; falls back to the first whitespace-separated token. The
# rest of the line (after an em/en dash, " - ", or " \u2014 ") is descriptive
# prose and is discarded.
_BULLET_LINE_RE = re.compile(r"^[-*+]\s+(.*)$")
_FIRST_TOKEN_RE = re.compile(r"`([^`]+)`|([A-Za-z_][\w\.]*)")


@dataclass
class SkillEntry:
    path: Path
    title: str
    sections: dict[str, list[str]] = field(default_factory=dict)

    def bullets(self, section: str) -> list[str]:
        """Return the bullet items under ``section``, case-insensitive."""
        for key, items in self.sections.items():
            if key.lower() == section.lower():
                return items
        return []


def parse_skill_markdown(path: Path) -> SkillEntry:
    """Parse a single skill entry. Title is the first H1; sections are H2 bullet lists."""
    text = path.read_text()
    title = path.stem
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and title == path.stem:
            title = line[2:].strip()
            continue
        m = _SECTION_RE.match(line)
        if m:
            current = m.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is None:
            continue
        m = _BULLET_LINE_RE.match(line)
        if m:
            tok = _FIRST_TOKEN_RE.search(m.group(1))
            if tok:
                sections[current].append(tok.group(1) or tok.group(2))
    return SkillEntry(path=path, title=title, sections=sections)


def list_skill_entries(root: Path) -> list[SkillEntry]:
    """Return every ``*.md`` under ``root`` except the index ``SKILL.md``."""
    if not root.exists():
        return []
    entries: list[SkillEntry] = []
    for md in sorted(root.rglob("*.md")):
        if md.name == "SKILL.md":
            continue
        entries.append(parse_skill_markdown(md))
    return entries


def list_model_entries() -> list[SkillEntry]:
    return list_skill_entries(MODELS_SKILLS_DIR)


def list_experiment_entries() -> list[SkillEntry]:
    return list_skill_entries(EXPERIMENTS_SKILLS_DIR)
