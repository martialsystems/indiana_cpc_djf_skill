# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from cpcskill.claims import scan_text
from cpcskill.config import INDEX_GIST, PRECIP_GIST, QUESTION, TEMP_GIST

REPO = Path(__file__).resolve().parents[1]


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    assert "1991-2020" in text or "equal-chance" in text or "equal chance" in text
    assert "ac36f0f" in text
    assert "1416da1" in text
    assert "6b47f21" in text
    assert "9aa7935" in text
    assert "28941fb" in text
    assert "USW00014848" in text
    assert "USW00014827" in text
    assert "USW00093819" in text
    assert "USW00093817" in text
    assert "Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3" in text
    assert "Open_the_research_console" not in text
    assert "labelColor" not in text
    assert INDEX_GIST in text
    assert TEMP_GIST.split("/")[-1] in text
    assert PRECIP_GIST.split("/")[-1] in text
    assert ".github/blob/main/RESEARCH.md" not in text
    assert "lead04/off04" not in text
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert ".venv/bin/python -m pytest" in text
    assert "`a95a16b`" in text
    assert "0.643" in text
    assert "0.809" in text
    assert "0.667" in text
    assert "skill_bars.png" in text
    assert "north_south.png" in text
    assert "not a statewide precip win" in text
    assert "Do not average it" in text
