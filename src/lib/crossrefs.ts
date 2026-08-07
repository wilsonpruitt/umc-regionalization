/**
 * The ratified text cites other paragraphs — and it cites them in BALLOT
 * numbering, because that is the numbering it was drafted against. A reader who
 * follows one of those citations into the 2024 Book of Discipline lands on the
 * wrong paragraph every time.
 *
 * Five such references exist across the amendment. All five resolve to exactly
 * the right provision under the +1 offset, which is independent semantic
 * confirmation of the offset on top of the statistical and article-number
 * checks in MAPPING.md:
 *
 *   ¶31.5  → ¶32.5   regional conference adaptation powers
 *   ¶37    → ¶38     the list of the five U.S. jurisdictions
 *   ¶40    → ¶41     annual conference names and boundaries
 *   ¶16.17 → ¶17.17  what General Conference may declare non-adaptable
 *   ¶33    → ¶34     the annual conference as the basic body
 *
 * Rather than silently rewriting the citations — which would misquote a ratified
 * text — we leave them as they stand and annotate them.
 */

export const BALLOT_TO_DISCIPLINE_OFFSET = 1;

export type CrossRef = {
  /** As printed in the ratified text, e.g. "31.5" */
  cited: string;
  /** The same provision in 2024 Discipline numbering, e.g. "32.5" */
  resolved: string;
  /** Paragraph number to link to */
  target: number;
  /** What is actually at that paragraph */
  describes: string;
};

const DESCRIBES: Record<number, string> = {
  17: "the powers of General Conference",
  32: "the powers of a regional conference",
  34: "the annual conference as the basic body of the Church",
  38: "the five United States jurisdictions and their boundaries",
  41: "the names and boundaries of annual conferences and episcopal areas",
};

const REF = /¶\s?(\d+)(\.\d+)?/g;

/** Every paragraph cited by this text, de-duplicated, in order of appearance. */
export function crossRefs(text: string): CrossRef[] {
  const seen = new Set<string>();
  const out: CrossRef[] = [];

  for (const m of text.matchAll(REF)) {
    const n = Number(m[1]);
    const sub = m[2] ?? "";
    const target = n + BALLOT_TO_DISCIPLINE_OFFSET;
    const cited = `${n}${sub}`;
    if (seen.has(cited)) continue;
    seen.add(cited);
    out.push({
      cited,
      resolved: `${target}${sub}`,
      target,
      describes: DESCRIBES[target] ?? "another paragraph of the Constitution",
    });
  }
  return out;
}
