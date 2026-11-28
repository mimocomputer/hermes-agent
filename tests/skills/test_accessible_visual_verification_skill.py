"""Tests for the optional accessible-visual-verification skill.

The skill ships no script of its own: it orchestrates the `pdf` skill's helpers
plus `vision_analyze`. So the mechanical obligations it can actually be held to
are (a) the frontmatter contract, (b) every helper it tells the agent to run
still exists in the `pdf` skill, and (c) the two rules that make the procedure
safe are present in the body — verify *both* ends of a range, and never ask a
user who cannot see the page to confirm it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agent.skill_utils import SKILL_PROMPT_DESC_LIMIT, parse_frontmatter

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "optional-skills" / "productivity" / "accessible-visual-verification"
PDF_SCRIPTS = REPO / "skills" / "productivity" / "pdf" / "scripts"


@pytest.fixture(scope="module")
def document():
    return parse_frontmatter((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))


def test_frontmatter_contract(document):
    metadata, body = document
    assert metadata["name"] == SKILL_DIR.name
    assert metadata["description"].endswith(".")
    assert len(metadata["description"]) <= SKILL_PROMPT_DESC_LIMIT
    assert metadata["platforms"] == ["linux", "macos", "windows"]
    assert body.strip()


def test_related_skills_resolve_in_repo(document):
    metadata, _ = document
    for related in metadata["metadata"]["hermes"]["related_skills"]:
        assert any((REPO / "skills").rglob(f"{related}/SKILL.md")), related


def test_referenced_pdf_helpers_exist(document):
    _, body = document
    referenced = sorted(set(re.findall(r"scripts/(pdf_\w+\.py)", body)))
    assert referenced, "the skill must name the pdf helpers it runs"
    for helper in referenced:
        assert (PDF_SCRIPTS / helper).is_file(), f"{helper} is gone from the pdf skill"


def test_body_keeps_the_two_safety_rules(document):
    _, body = document
    assert "Verify both ends" in body
    assert "Never ask the user whether page X looks right" in body
