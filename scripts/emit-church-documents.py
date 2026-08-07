#!/usr/bin/env python3.11
"""
Emit the regionalization corpus into ~/church-documents so other projects can
consume the amended constitutional text instead of the stale bod-2024.json.

Reads the same generated YAML the site renders from, so the two cannot drift.
Run `extract-amendments.py` first.

Deliberately does NOT rewrite bod-2024.json. That file is a faithful parse of the
printed 2020/2024 Cokesbury edition, which genuinely still reads the pre-amendment
way; silently patching it would destroy the ability to cite what the printed book
says. This ships the amendment as a separate instrument and flags the Discipline
entry as superseded in part, so consumers overlay rather than guess.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "content" / "paragraphs"
CD = Path.home() / "church-documents"
OUT = CD / "documents" / "constitution" / "umc-constitutional-amendments-2024.json"
MANIFEST = CD / "manifest.json"

DOC_ID = "umc-constitutional-amendments-2024"
# Bumped by hand: scripts here cannot call Date.now()-equivalents reproducibly,
# and a manifest date that silently drifts on every re-run is worse than a stale one.
UPDATED = "2026-08-07"
RAW = (
    "https://raw.githubusercontent.com/wilsonpruitt/church-documents/main/"
    "documents/constitution/umc-constitutional-amendments-2024.json"
)


def read_yaml(path: Path) -> dict:
    """Minimal reader for the fixed shape extract-amendments.py writes."""
    text = path.read_text(encoding="utf-8")
    out: dict = {}

    for key in ("ballotNumber", "disciplineNumber"):
        out[key] = int(re.search(rf"^{key}: (\d+)$", text, re.M).group(1))
    out["status"] = re.search(r"^status: (\w+)$", text, re.M).group(1)
    for key in ("articleOld", "articleNew", "sectionOld", "sectionNew", "divisionOld"):
        out[key] = json.loads(re.search(rf'^{key}: (".*")$', text, re.M).group(1))
    out["retainedWording"] = float(
        re.search(r"^retainedWording: ([\d.]+)$", text, re.M).group(1)
    )
    for key in ("rewritten", "elided"):
        out[key] = re.search(rf"^{key}: (true|false)$", text, re.M).group(1) == "true"

    for key in ("textOld", "textNew"):
        m = re.search(rf"^{key}: (?:\|-\n((?:    .*\n?)*)|(\"\"))$", text, re.M)
        out[key] = (
            "\n".join(line[4:] for line in m.group(1).rstrip("\n").split("\n")).strip()
            if m.group(1)
            else ""
        )

    notes = re.search(r"^notes:\n((?:  - .*\n)*)", text, re.M)
    out["notes"] = (
        [json.loads(ln.strip()[2:]) for ln in notes.group(1).strip().split("\n")]
        if notes and notes.group(1).strip()
        else []
    )
    return out


def main() -> None:
    files = sorted(SRC.glob("*.yaml"), key=lambda p: int(p.stem))
    if not files:
        sys.exit("FATAL: no paragraphs found — run extract-amendments.py first.")
    paras = [read_yaml(f) for f in files]
    paras.sort(key=lambda p: p["disciplineNumber"])

    counts = {s: sum(1 for p in paras if p["status"] == s) for s in ("amended", "new", "deleted")}
    if (counts["amended"], counts["deleted"], counts["new"]) != (26, 2, 1):
        sys.exit(f"FATAL: unexpected scope {counts}; refusing to publish.")

    doc = {
        "meta": {
            "id": DOC_ID,
            "title": (
                "UMC Constitution — Amendment I (Worldwide Regionalization), "
                "Petition 21039, as ratified"
            ),
            "petition": "21039",
            "calendarItem": "22",
            "committeeItem": "ST29",
            "adopted": "2024-04-25",
            "adoptedVote": "586-164",
            "certified": "2025-11-05",
            "ratificationShare": 0.916,
            "certifiedBy": "Council of Bishops, autumn 2025 meeting",
            "source": (
                "Proposed Constitutional Amendments, approved by the 2020/2024 General "
                "Conference (Gary W. Graves, Secretary of the General Conference), as "
                "printed in the Western North Carolina Conference 2025 Program and "
                "Reports, pp. 29-39."
            ),
            "coverage": (
                f"complete for Amendment I — {counts['amended']} paragraphs amended, "
                f"{counts['deleted']} struck, {counts['new']} added"
            ),
            "numbering": (
                "IMPORTANT. Two numbering systems are in play. The ballot text was "
                "drafted against the PRE-2019 constitution numbering; Article VI "
                "(Gender Justice) was inserted at para 6 by an amendment ratified in "
                "2019, shifting everything after it up by one. So ballot para N = "
                "Discipline para N+1 from para 6 onward. This file is keyed by "
                "DISCIPLINE number; ballotNumber is carried on every record. Verified "
                "structurally: at this offset the Roman article numbers align on 23 of "
                "26 amended paragraphs, and the three exceptions are documented in "
                "each record's notes."
            ),
            "supersedes": (
                "bod-2024 paragraphs 10-62. bod-2024.json is a faithful parse of the "
                "printed 2020/2024 edition and predates ratification; it is NOT patched. "
                "Overlay this document on top of it for the Constitution as now in force. "
                "Paragraphs 1-9 are unaffected."
            ),
            "notInScope": (
                "Amendments II (para 4, inclusiveness), III (para 5, racial justice) and "
                "IV (para 36, clergy delegates), ratified the same day; and the enabling "
                "legislation outside the Constitution (paras 101, 507, 543-544, 2201), "
                "which is ordinary legislation and was not part of the ratification vote."
            ),
            "caveat": (
                "The post-ratification wording here is the ballot text — what the annual "
                "conferences actually voted on. No official reprinting of the amended "
                "Constitution has been located. The ballot's own editorial note says "
                "'Numbering of paragraphs will be subject to the final editing of The "
                "Book of Discipline 2020/2024.' Treat fine typography and final "
                "numbering as provisional; the substance is what was ratified."
            ),
            "paragraph_count": len(paras),
            "generatedBy": "umc-regionalization/scripts/emit-church-documents.py",
            "lookup": (
                "`index` maps Discipline paragraph number (string) -> position in "
                "paragraphs[]. `ballotIndex` does the same for ballot numbers."
            ),
        },
        "index": {str(p["disciplineNumber"]): i for i, p in enumerate(paras)},
        "ballotIndex": {str(p["ballotNumber"]): i for i, p in enumerate(paras)},
        "paragraphs": paras,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    entry = {
        "id": DOC_ID,
        "title": "UMC Constitution — Amendment I (Regionalization), Petition 21039, as ratified",
        "category": "constitution",
        "format": "json",
        "path": "documents/constitution/umc-constitutional-amendments-2024.json",
        "rawUrl": RAW,
        "records": (
            f"{len(paras)} paragraphs ({counts['amended']} amended, "
            f"{counts['deleted']} struck, {counts['new']} added)"
        ),
        "completeness": "full",
        "note": (
            "The regionalization amendment adopted by the 2020/2024 General Conference "
            "and certified as ratified 2025-11-05 (91.6%). Carries old and new text for "
            "every paragraph. SUPERSEDES bod-2024 paragraphs 10-62 — overlay it. "
            "NB: ballot paragraph numbers run one behind Discipline numbers; see "
            "meta.numbering."
        ),
        "canonicalSource": "generated by umc-regionalization/scripts/emit-church-documents.py",
    }

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    man["updated"] = UPDATED
    docs = man["documents"]
    at = next((i for i, d in enumerate(docs) if d["id"] == DOC_ID), None)
    if at is None:
        after = next((i for i, d in enumerate(docs) if d["id"] == "bod-2024-supplement"), None)
        docs.insert(after + 1 if after is not None else len(docs), entry)
    else:
        docs[at] = entry

    for d in docs:
        if d["id"] == "bod-2024" and "SUPERSEDED IN PART" not in d["note"]:
            d["note"] += (
                " ⚠️ SUPERSEDED IN PART: paragraphs 10-62 predate the regionalization "
                f"amendment ratified 2025-11-05. Overlay `{DOC_ID}` for the Constitution "
                "as now in force. Paragraphs 1-9 are unaffected."
            )

    MANIFEST.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(CD)} ({OUT.stat().st_size:,} bytes)")
    print(f"  {counts['amended']} amended · {counts['deleted']} struck · {counts['new']} added")
    print(f"manifest: {len(docs)} documents; bod-2024 flagged superseded in part")


if __name__ == "__main__":
    main()
