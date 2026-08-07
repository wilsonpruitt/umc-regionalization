# umcregions.wrootlabs.com

A paragraph-by-paragraph reference to the constitutional amendment on
regionalization (Petition 21039) adopted by the 2020/2024 General Conference of
The United Methodist Church and certified as ratified on 5 November 2025.

The existing public explainers describe the change without showing the
instrument. This site shows the instrument: every paragraph the amendment
touches, the text before and after, and a generated word-level diff where the
paragraph was edited rather than replaced.

Astro 5, no runtime dependencies, static output. Same stack, tokens, and
editorial posture as [`~/denominations`](../denominations) — the two are sibling
reference sites and should stay visually identical.

## Working on it

```
pnpm install
pnpm run extract     # regenerate src/content/paragraphs/ from sources/
pnpm run dev
pnpm run check       # astro check — must be 0 errors
pnpm run predeploy   # clean build + dist gate
```

## The data is generated

`src/content/paragraphs/*.yaml` is written by `scripts/extract-amendments.py`
from the archived ballot PDF and the 2024 Book of Discipline. **Do not hand-edit
the text fields** — they are overwritten on every extract. Only `summary` and
`whatChanged` are editorial, and the extractor currently clears the directory on
each run, so move any authored prose out before re-extracting.

The extractor asserts rather than assumes. It will exit non-zero if the ballot's
declared scope stops matching what it parses, if Roman article numbers shear, if
a running head leaks into the prose, or if an enumerated list has a gap with no
ellipsis in the source. Each of those guards was added because it caught a real
defect.

## Read MAPPING.md before touching the numbering

The ballot papers and the 2024 Book of Discipline use **different paragraph
numbers** — the ballot runs one behind, because Article VI on gender justice was
inserted at ¶6 by an amendment ratified in 2019 and shifted everything after it.
`MAPPING.md` records the full old-to-new table, how the offset was derived, and
the three paragraphs whose article numbers legitimately do not line up.

This site uses **Discipline numbers** in URLs and headings, and shows the ballot
number alongside on every paragraph page.

## Sourcing and tone

Inherited from `~/denominations/CONVENTIONS.md`:

- **Describe, don't promote.** Regionalization is contested. Where a provision is
  disputed, state the strongest version of the objection *and* the rationale, and
  adjudicate neither.
- **Cite the instrument**, not the vibe — "¶32.5(a), as amended by Petition
  21039".
- **Coverage honesty.** A missing summary renders as a stated gap, not as
  silence. The provisional status of the text is on `/sources` and gated in
  `check-dist.sh`.
- The post-ratification text here is the **ballot text**. No official reprinting
  of the amended Constitution has been located. If one appears, correct against
  it and drop the provisional notice.

## Still to do

- Editorial `summary` and `whatChanged` for the 29 paragraphs. Currently every
  index row reads "summary not yet written," which is honest but not yet useful.
- Vercel project on the Labs team, DNS-only record at Cloudflare.

## Feeding church-documents

`scripts/emit-church-documents.py` writes the corpus into `~/church-documents` as
`umc-constitutional-amendments-2024`, from the same generated YAML the site
renders, so the two cannot drift. Re-run it after any re-extract.

It deliberately does **not** patch `bod-2024.json`. That file is a faithful parse
of the printed 2020/2024 edition, which genuinely still reads the pre-amendment
way, and being able to cite the printed book is worth keeping. Instead the
manifest entry for `bod-2024` is flagged superseded in part, and consumers overlay
the amendment document. `bod-2024` ¶¶10–62 are stale; ¶¶1–9 are unaffected.
