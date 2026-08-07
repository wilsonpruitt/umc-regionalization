#!/usr/bin/env python3.11
"""
Extract the regionalization amendment (Amendment I / Petition 21039) into the
Astro content collection.

Sources
-------
sources/gc2024/ballot-wnc-2025.txt
    pdftotext -layout of the Western NC Conference 2025 Program and Reports
    printing of the four proposed constitutional amendments. Chosen as primary:
    it is typeset from InDesign, extracts far more cleanly than the Graves draft,
    and it is the only one of the two whose AMEND list includes 48.

church-documents/documents/discipline/bod-2024.json
    The 2020/2024 Book of Discipline. Supplies the OLD text -- i.e. the text
    actually in force before the amendment takes effect.

The numbering problem
---------------------
The ballot text is drafted against the PRE-2019 constitution numbering. Article VI
"Gender Justice" was inserted at 6 by an amendment ratified in 2019, shifting every
subsequent paragraph up by one. So ballot 15 is Discipline 16, ballot 61 is
Discipline 62, and so on.

The offset is treated as a STRUCTURAL fact, not a per-paragraph guess. An earlier
version scored each ballot paragraph against a window of candidates and took the
best match; that produced offsets of -2 and +3 on the paragraphs the amendment
rewrites most heavily, because low text similarity is exactly what a rewrite looks
like. Similarity cannot arbitrate numbering when the whole point of the document
is to change the words.

So: the offset is derived once by consensus across the paragraphs the amendment
barely touches (where similarity IS good evidence), asserted to be unanimous among
them, and then applied uniformly. Per-paragraph similarity is retained only as a
REPORT of how heavily each paragraph was rewritten -- which is genuinely useful
editorial signal, and is surfaced on the page as such.

One documented exception: 9 and 10 swap contents (see SWAP).
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BALLOT = ROOT / "sources" / "gc2024" / "ballot-wnc-2025.txt"
BOD = Path.home() / "church-documents" / "documents" / "discipline" / "bod-2024.json"
OUT = ROOT / "src" / "content" / "paragraphs"
MAPPING = ROOT / "MAPPING.md"

# Paragraphs scoring at or above this are "lightly touched" -- similarity is
# trustworthy evidence there, so these are the rows that vote on the offset.
OFFSET_QUORUM = 0.85

# Below this, the amendment rewrote the paragraph rather than tweaking it. Not a
# mapping problem; a fact about the paragraph, reported as `rewritten: true`.
REWRITE_FLOOR = 0.55

# The ballot header: "AMEND 9, (which shall be renumbered 10), 10 (which shall be
# renumbered 9)". The two paragraphs trade contents. So the provision that BECOMES
# ballot-9 (regional conferences) is the one that WAS ballot-10 (central
# conferences), and vice versa. Keyed ballot-new -> ballot-old.
SWAP = {9: 10, 10: 9}

SOURCE_ID = "wnc-2025-ballot"

# Running heads and bare page numbers that pdftotext interleaves into the prose.
# Recto and verso put the folio on opposite sides of the title, so both orders
# must match -- an earlier version handled only the recto form and leaked the
# verso head into 15.
NOISE = re.compile(
    r"^\s*(?:\d{1,3}\s+)?"
    r"(?:Western NC Conference \| 2025 Program and Reports)"
    r"(?:\s+\d{1,3})?\s*$"
    r"|^\s*\d{1,3}\s*$"
)
PARA_START = re.compile(r"^¶ ?(\d+)\s*\.?\s*Article\s+([IVXL]+)", re.MULTILINE)


@dataclass
class Para:
    ballot: int
    article_new: str
    text_new: str
    discipline: int | None = None
    article_old: str | None = None
    section_old: str | None = None
    division_old: str | None = None
    text_old: str | None = None
    score: float = 0.0
    status: str = "amended"
    section_new: str | None = None
    elided: bool = False
    notes: list[str] = field(default_factory=list)


def norm(s: str) -> str:
    """Comparison form: lowercase letters and spaces only."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", s.lower())).strip()


def clean_lines(block: str) -> str:
    """Drop running heads, then rewrap into single-spaced prose."""
    kept = [ln for ln in block.split("\n") if not NOISE.match(ln)]
    out = re.sub(r"[ \t]+", " ", "\n".join(kept)).strip()
    # InDesign emits a thin space before some periods ("2 .", "¶ 40 ."). Harmless
    # in print, ugly in HTML, and it breaks enumerator detection.
    out = re.sub(r"(?<=[\w\d)]) +\.", ".", out)
    return out


# A line starting one of these begins a new block; anything else is a wrapped
# continuation of the line above. Without this every line break the PDF happened
# to contain survives into the HTML, and enumerated items wrap mid-sentence.
ENUMERATOR = re.compile(r"^\s*(?:\d{1,2}\.(?!\d)|[a-z]\)|\([a-z]\))\s")


def reflow(body: str) -> str:
    """Join wrapped lines back into blocks, keeping breaks before enumerators."""
    blocks: list[str] = []
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        if not blocks or ENUMERATOR.match(line):
            blocks.append(line)
        else:
            blocks[-1] = f"{blocks[-1]} {line}"
    return "\n".join(blocks)


def slice_between(text: str, start: str, end: str, *, label: str) -> str:
    i = text.find(start)
    j = text.find(end, i + 1) if i != -1 else -1
    if i == -1 or j == -1:
        sys.exit(f"FATAL: could not locate {label} (start={i}, end={j}). "
                 "The source PDF layout changed; re-check before trusting output.")
    return text[i + len(start):j]


def main() -> None:
    raw = BALLOT.read_text(encoding="utf-8")

    amendment_i = slice_between(
        raw,
        "Proposed Constitutional Amendment I",
        "Proposed Constitutional Amendment II",
        label="Amendment I",
    )

    # --- the declared scope, straight from the ballot -----------------------
    m = re.search(r"AMEND ¶¶(.*?)and add new (\d+) as follows:", amendment_i, re.S)
    if not m:
        sys.exit("FATAL: AMEND header not found.")
    declared = sorted({int(n) for n in re.findall(r"\b(\d+)\b", m.group(1))})
    new_para = int(m.group(2))

    # --- pass 2: the clean, post-ratification wording -----------------------
    clean = clean_lines(
        slice_between(
            amendment_i,
            "[If ratified, the paragraphs would read as follows:]",
            "Rationale:",
            label="clean pass",
        )
    )

    starts = list(PARA_START.finditer(clean))
    if not starts:
        sys.exit("FATAL: no paragraphs parsed from the clean pass.")

    # Section headings ("Section V. Regional Conferences") sit between paragraphs in
    # the clean pass and are the amendment's own naming of the restructured sections
    # -- worth keeping, since renaming "Central Conferences" to "Regional
    # Conferences" is much of what this amendment does.
    SECTION = re.compile(r"^Section\s+[IVXL]+\.\s+.+$", re.MULTILINE)

    paras: list[Para] = []
    for k, mm in enumerate(starts):
        end = starts[k + 1].start() if k + 1 < len(starts) else len(clean)
        block = clean[mm.start():end]

        # A heading belongs to the paragraph that follows it, not the one before.
        heading = None
        if k + 1 < len(starts):
            tail = clean[mm.end():end]
            found = SECTION.findall(tail)
            if found:
                heading = found[-1].strip()

        body = SECTION.sub("", block).strip()
        body = re.sub(r"^¶ ?\d+\s*\.?\s*Article\s+[IVXL]+\s*\.?\s*[—–-]\s*", "", body)
        elided = bool(re.search(r"(?:^|\n)\s*\.\.\.\s*(?:\n|$)", body))
        body = re.sub(r"(?:^|\n)\s*\.\.\.\s*(?=\n|$)", "", body)
        body = reflow(body)

        paras.append(
            Para(
                ballot=int(mm.group(1)),
                article_new=mm.group(2),
                text_new=re.sub(r"\n{2,}", "\n", body).strip(),
                elided=elided,
            )
        )
        if heading:
            paras[-1].notes.append(f"__SECTION__{heading}")

    # Re-attach: a heading found inside paragraph N's block introduces paragraph N+1.
    for k, p in enumerate(paras):
        marker = next((n for n in p.notes if n.startswith("__SECTION__")), None)
        if marker:
            p.notes.remove(marker)
            if k + 1 < len(paras):
                paras[k + 1].section_new = marker.removeprefix("__SECTION__")

    present = {p.ballot for p in paras}
    deleted = [n for n in declared if n not in present]

    # --- derive the offset by consensus, then apply it uniformly ------------
    bod = json.loads(BOD.read_text(encoding="utf-8"))
    idx, entries = bod["index"], bod["paragraphs"]

    def disc(n: int) -> dict | None:
        pos = idx.get(str(n))
        return entries[pos] if pos is not None else None

    def sim(a: str, b: str, *, head: int | None = None) -> float:
        x, y_ = norm(a), norm(b)
        if head:
            x, y_ = x[:head], y_[:head]
        return difflib.SequenceMatcher(None, x, y_).ratio()

    # Vote: for each candidate offset, how many paragraphs match at quorum?
    votes: dict[int, list[int]] = {}
    for p in paras:
        if p.ballot == new_para:
            continue
        for off in (0, 1, 2):
            e = disc(p.ballot + off)
            if e and sim(p.text_new, e.get("body") or "", head=500) >= OFFSET_QUORUM:
                votes.setdefault(off, []).append(p.ballot)

    if not votes:
        sys.exit("FATAL: no paragraph matched any candidate offset at quorum.")
    offset = max(votes, key=lambda o: len(votes[o]))
    if len(votes) > 1:
        others = {o: len(v) for o, v in votes.items() if o != offset}
        if any(c >= len(votes[offset]) for c in others.values()):
            sys.exit(f"FATAL: offset is ambiguous. votes={ {o: len(v) for o, v in votes.items()} }")

    print(f"offset resolved to {offset:+d} on {len(votes[offset])} high-confidence "
          f"paragraphs: {sorted(votes[offset])}")

    for p in paras:
        p.discipline = p.ballot + offset

        if p.ballot == new_para:
            p.status = "new"
            p.notes.append(
                "Added by the amendment; there is no prior text. Subsequent paragraphs "
                "renumber to make room for it."
            )
            continue

        # Which provision does this text replace? Normally the same number; for the
        # 9/10 pair the two paragraphs trade contents.
        source_ballot = SWAP.get(p.ballot, p.ballot)
        e = disc(source_ballot + offset)
        if e is None:
            p.notes.append(f"No Discipline text found at {source_ballot + offset}.")
            continue

        p.article_old = e.get("article")
        p.section_old = e.get("section")
        p.division_old = e.get("division")
        p.text_old = (e.get("body") or "").strip()
        p.score = sim(p.text_new, p.text_old)

        if source_ballot != p.ballot:
            p.notes.append(
                f"Numbers trade contents here. The provision now at ¶{p.discipline} is "
                f"the one previously at ¶{source_ballot + offset}; what used to stand at "
                f"¶{p.discipline} moves to ¶{SWAP[p.ballot] + offset}. The comparison "
                "below follows the provision, not the number."
            )
        if p.elided:
            p.notes.append(
                "The ballot reproduces only the portions of this paragraph it changes, "
                "eliding the rest with an ellipsis. The text on the right is therefore "
                "partial; everything not shown is unchanged and stands as printed at "
                f"¶{p.discipline} of the 2024 Discipline, on the left."
            )
        elif p.score < REWRITE_FLOOR:
            # Suppressed for elided paragraphs: there the low figure reflects the
            # ballot omitting unchanged text, not the amendment rewriting it.
            p.notes.append(
                f"Rewritten rather than tweaked — only {p.score:.0%} of the wording "
                "survives. Read the two texts side by side rather than the diff."
            )

    # --- deleted paragraphs still get a page --------------------------------
    for n in deleted:
        e = disc(n + offset) or {}
        paras.append(
            Para(
                ballot=n,
                article_new="",
                text_new="",
                discipline=n + offset,
                article_old=e.get("article"),
                section_old=e.get("section"),
                division_old=e.get("division"),
                text_old=(e.get("body") or "").strip(),
                score=1.0,
                status="deleted",
                notes=[
                    "Present in the amendment's marked-up pass but absent from the "
                    "post-ratification text: this paragraph is struck."
                ],
            )
        )

    # --- independent check: Roman article numbers must line up --------------
    # Text similarity and article numbering are unrelated signals. At the correct
    # offset nearly every paragraph keeps its Article number; at a wrong offset the
    # sequence shears and almost none do. This is the stronger of the two checks,
    # because it does not degrade on the paragraphs the amendment rewrites hardest.
    checkable = [p for p in paras if p.status == "amended" and p.article_old]
    aligned = [p for p in checkable if p.article_old == p.article_new]
    misaligned = [p for p in checkable if p.article_old != p.article_new]
    expected_misaligned = set(SWAP) | {40}  # the 9/10 swap, and 40 after 38/39 are struck
    unexplained = [p.ballot for p in misaligned if p.ballot not in expected_misaligned]
    print(f"article alignment: {len(aligned)}/{len(checkable)} exact; "
          f"misaligned {sorted(p.ballot for p in misaligned)} "
          f"(expected {sorted(expected_misaligned)})")
    if unexplained:
        sys.exit(
            f"FATAL: article numbers shear at ¶¶ {unexplained} with no documented "
            f"cause. Either the offset is wrong or the amendment renumbers articles "
            f"in a way this script does not model. Resolve before publishing."
        )

    # --- text integrity: leaked furniture, and gaps in enumerated lists -----
    # The 2024 feedback on page-break truncation applies directly here: a list in
    # pdftotext output continues past running heads, so a naive slice silently
    # drops items. Verify the LAST item, not the first.
    for p in paras:
        if "Western NC Conference" in p.text_new or "Program and Reports" in p.text_new:
            sys.exit(f"FATAL: running head leaked into ¶{p.ballot} text.")
        nums = [int(n) for n in re.findall(r"(?:^|\n)\s*(\d{1,2})\.\s", p.text_new)]
        if nums and nums != list(range(1, max(nums) + 1)):
            missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
            if not p.elided:
                sys.exit(
                    f"FATAL: ¶{p.ballot} enumerated list is missing item(s) {missing} "
                    f"(found {nums}) with no ellipsis in the source. Likely a "
                    "page-break drop — check the source before publishing."
                )
            p.notes.append(
                f"Specifically, sub-item(s) {', '.join(str(m) for m in missing)} are "
                "not reproduced."
            )
        letters = re.findall(r"(?:^|\n)\s*([a-z])\)\s", p.text_new)
        if letters and letters != [chr(ord("a") + i) for i in range(len(letters))]:
            sys.exit(f"FATAL: ¶{p.ballot} lettered list is out of sequence: {letters}")

    paras.sort(key=lambda p: p.ballot)
    write_yaml(paras)
    write_mapping(paras, declared, new_para, deleted, offset, votes[offset])

    n_amended = sum(1 for p in paras if p.status == "amended")
    rewritten = [p.ballot for p in paras
                 if p.status == "amended" and not p.elided and p.score < REWRITE_FLOOR]
    print(f"wrote {len(paras)} paragraphs -> {OUT.relative_to(ROOT)}")
    print(f"  declared in AMEND list : {len(declared)} + new {new_para}")
    print(f"  amended {n_amended} · deleted {len(deleted)} {deleted} · new "
          f"{sum(1 for p in paras if p.status=='new')}")
    assert n_amended + len(deleted) == len(declared), (
        f"scope mismatch: {n_amended} amended + {len(deleted)} deleted != {len(declared)} declared"
    )
    print(f"  heavily rewritten ({len(rewritten)}): {rewritten}")


def y(s: str) -> str:
    """Block scalar, indented four spaces."""
    if not s:
        return '""'
    return "|-\n" + "\n".join("    " + ln for ln in s.split("\n"))


def write_yaml(paras: list[Para]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.yaml"):
        old.unlink()
    for p in paras:
        notes = "\n".join(f"  - {json.dumps(n)}" for n in p.notes) or "  []"
        OUT.joinpath(f"{p.ballot}.yaml").write_text(
            f"""# GENERATED by scripts/extract-amendments.py -- do not hand-edit the
# text fields. Editorial prose belongs in summary/whatChanged below, which the
# extractor preserves across runs only if you move it to editorial/{p.ballot}.yaml.
ballotNumber: {p.ballot}
disciplineNumber: {p.discipline}
status: {p.status}
articleOld: {json.dumps(p.article_old or "")}
articleNew: {json.dumps(p.article_new or "")}
sectionOld: {json.dumps(p.section_old or "")}
divisionOld: {json.dumps(p.division_old or "")}
sectionNew: {json.dumps(p.section_new or "")}
elided: {"true" if p.elided else "false"}
retainedWording: {p.score:.3f}
rewritten: {"true" if (p.score < REWRITE_FLOOR and p.status == "amended") else "false"}
textOld: {y(p.text_old or "")}
textNew: {y(p.text_new or "")}
notes:
{notes}
sources:
  - {SOURCE_ID}
""",
            encoding="utf-8",
        )


def write_mapping(paras, declared, new_para, deleted, offset, quorum) -> None:
    flagged = [p for p in paras
               if p.status == "amended" and not p.elided and p.score < REWRITE_FLOOR]
    rows = "\n".join(
        f"| {p.ballot} | {p.discipline} | "
        f"{p.article_old or '—'} → {p.article_new or '—'} | {p.status} | "
        f"{p.score:.0%}{' — rewritten' if p in flagged else (' — partial (elided)' if p.elided else '')} |"
        for p in paras
    )
    MAPPING.write_text(
        f"""# Paragraph mapping audit

Generated by `scripts/extract-amendments.py`. **A human signs this off before any
paragraph page is authored.**

## The offset

The ballot text uses the **pre-2019** constitution numbering. Article VI "Gender
Justice" was inserted at ¶6 by an amendment ratified in 2019
(`amendment_years: [2019]` in `bod-2024.json`), shifting every subsequent
paragraph up by one. Amendments II (¶4 Inclusiveness) and III (¶5 Racial Justice)
sit before the insertion and are *not* shifted — which is the control that
confirms the cause.

The ballot's own editorial note anticipates this: *"Numbering of paragraphs will
be subject to the final editing of The Book of Discipline 2020/2024."*

The extractor derives the offset — resolved here to **{offset:+d}** — by consensus
rather than assumption. Each ballot paragraph is scored against candidate
Discipline paragraphs at offsets 0/+1/+2, and only those matching at ≥{OFFSET_QUORUM:.0%}
get a vote. {len(quorum)} paragraphs cleared that bar and all voted the same way:
¶¶ {', '.join(str(n) for n in sorted(quorum))}. The offset is then applied
uniformly, because numbering is a structural fact about the document and cannot be
arbitrated paragraph-by-paragraph on text similarity — the paragraphs the amendment
rewrites hardest are exactly the ones where similarity is least informative.

## Rewritten, not tweaked

The **match** column below is *retained wording*, not mapping confidence. A low
figure means the amendment rewrote the paragraph, which is editorial signal worth
publishing, not a defect in the join.

## Scope declared by the ballot

`AMEND ¶¶ {', '.join(str(n) for n in declared)} and add new {new_para}`
— {len(declared)} amended + 1 new. Deleted (in the marked-up pass, absent from the
post-ratification text): **{', '.join(str(n) for n in deleted) or 'none'}**.

> The Graves draft of 2024-09-06 omits **48** from this list. The Western NC
> printing includes it, and ¶48 does appear in both passes of both documents.
> Treated as a typo in the Graves draft.

Heavily rewritten: {', '.join(f'¶{p.ballot}' for p in flagged) or '_none_'}.

## Full mapping

| Ballot ¶ | Discipline ¶ | Article | status | wording retained |
|---|---|---|---|---|
{rows}
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
