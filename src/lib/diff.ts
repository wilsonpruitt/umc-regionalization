/**
 * Word-level diff, computed at build time from the two texts. Nothing here is
 * hand-authored, which is the point: the ballot's own strikethrough/underline
 * markup does not survive PDF text extraction, so reproducing it would mean
 * transcribing it by hand. Generating the diff from the 2024 Discipline text and
 * the post-ratification text is both cheaper and checkable.
 */

export type Token = { type: "same" | "ins" | "del"; text: string };

/** Split into words while keeping whitespace, so output re-flows as prose. */
function tokenize(s: string): string[] {
  return s.match(/\s+|[^\s]+/g) ?? [];
}

/** Compare ignoring case and edge punctuation — we want meaning, not typography. */
function key(tok: string): string {
  return tok.trim().toLowerCase().replace(/^[^\w¶]+|[^\w]+$/g, "");
}

/**
 * Longest common subsequence over word keys.
 *
 * Guarded: 31 is ~4,000 characters against ~1,500, and a full O(n·m) table on
 * pathological input would be the one slow thing in the build. Above the cap we
 * skip the diff and the page falls back to showing the two texts side by side,
 * which is what the heavily-rewritten paragraphs want anyway.
 */
const MAX_CELLS = 4_000_000;

export function diffWords(oldText: string, newText: string): Token[] | null {
  const a = tokenize(oldText);
  const b = tokenize(newText);
  if (a.length * b.length > MAX_CELLS) return null;

  const ak = a.map(key);
  const bk = b.map(key);

  // lcs[i][j] = length of LCS of a[i..] and b[j..]
  const lcs: Uint32Array[] = Array.from(
    { length: a.length + 1 },
    () => new Uint32Array(b.length + 1),
  );
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      lcs[i][j] =
        ak[i] === bk[j]
          ? lcs[i + 1][j + 1] + 1
          : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
    }
  }

  const out: Token[] = [];
  const push = (type: Token["type"], text: string) => {
    const last = out[out.length - 1];
    if (last && last.type === type) last.text += text;
    else out.push({ type, text });
  };

  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (ak[i] === bk[j]) {
      push("same", a[i]);
      i++;
      j++;
    } else if (lcs[i + 1][j] >= lcs[i][j + 1]) {
      push("del", a[i++]);
    } else {
      push("ins", b[j++]);
    }
  }
  while (i < a.length) push("del", a[i++]);
  while (j < b.length) push("ins", b[j++]);

  // Whitespace-only runs marked ins/del are noise; fold them into `same`.
  return out.map((t) =>
    t.type !== "same" && t.text.trim() === "" ? { type: "same", text: t.text } : t,
  );
}
