import { getCollection, type CollectionEntry } from "astro:content";

export type Para = CollectionEntry<"paragraphs">;

/**
 * The new 13 has no prior entry in the Discipline, so the extractor cannot read
 * a division or section off it. It takes Article VI in Section I. Conferences,
 * immediately after the article on charge conferences.
 */
const PLACEMENT: Record<number, { division: string; section: string }> = {
  13: { division: "DIVISION ONE—GENERAL", section: "Section I. Conferences" },
};

export function placement(p: Para) {
  const fallback = PLACEMENT[p.data.ballotNumber];
  return {
    division: p.data.divisionOld || fallback?.division || "",
    section: p.data.sectionOld || fallback?.section || "",
  };
}

/** Human label for the group a paragraph belongs to on the index. */
export function groupLabel(p: Para): string {
  const { division, section } = placement(p);
  if (section) return section;
  return division
    .replace(/^DIVISION \w+—/, "")
    .toLowerCase()
    .replace(/^\w/, (c) => c.toUpperCase());
}

export async function allParagraphs(): Promise<Para[]> {
  const all = await getCollection("paragraphs");
  return all.sort((a, b) => a.data.ballotNumber - b.data.ballotNumber);
}

export type Group = { label: string; renamedFrom?: string; paras: Para[] };

/**
 * Index order: grouped by section, groups in first-appearance order.
 *
 * Where the amendment supplies its own heading for a section, that heading wins
 * and the former name is shown alongside — renaming Section V from "Central
 * Conferences" to "Regional Conferences" is a substantial part of what this
 * amendment does, and an index labelled with the superseded name would hide it.
 */
export async function grouped(): Promise<Group[]> {
  const all = await allParagraphs();
  const map = new Map<string, Para[]>();
  for (const p of all) {
    const g = groupLabel(p);
    if (!map.has(g)) map.set(g, []);
    map.get(g)!.push(p);
  }
  return [...map.entries()].map(([label, paras]) => {
    const renamed = paras.find((p) => p.data.sectionNew)?.data.sectionNew;
    return renamed && renamed !== label
      ? { label: renamed, renamedFrom: label, paras }
      : { label, paras };
  });
}

export function statusLabel(p: Para): string {
  if (p.data.status === "new") return "New";
  if (p.data.status === "deleted") return "Struck";
  return p.data.elided ? "Amended in part" : "Amended";
}
