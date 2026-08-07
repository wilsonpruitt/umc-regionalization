/**
 * The editorial layer: what each paragraph governs, and what the amendment did
 * to it. Keyed by 2024 Book of Discipline paragraph number.
 *
 * This lives OUTSIDE src/content/paragraphs/ deliberately. The extractor clears
 * that directory on every run, so authored prose kept there would be destroyed
 * by a re-extract. Everything here survives; lib/paragraphs.ts merges it in.
 *
 * Written against the texts themselves, then checked against what the public
 * explainers claim — see GAPS.md for that comparison and what it found.
 *
 * Tone rules, inherited from ~/denominations/CONVENTIONS.md and binding here:
 * describe, don't promote; cite the instrument; where a provision is contested,
 * state the strongest version of both readings and adjudicate neither.
 */

export type Editorial = { summary: string; whatChanged: string };

export const EDITORIAL: Record<number, Editorial> = {
  10: {
    summary:
      "Regional conferences exist, and they cover the whole church rather than only the part of it outside the United States.",
    whatChanged:
      "Central conferences become regional conferences, and the words “outside the United States of America” come out. The old paragraph established a category for everywhere the United States was not; the new one establishes a category that includes it. The proviso that no conference may be organised on any ground other than geography moves here.",
  },
  11: {
    summary:
      "Jurisdictional conferences are now permitted rather than required, and are no longer defined as a United States institution.",
    whatChanged:
      "Two changes that are easy to miss, both in the first line. “There shall be jurisdictional conferences” becomes “There may be” — jurisdictions are now optional, and a region could organise without them. And “for the Church in the United States of America” becomes “for the work of the Church,” so jurisdictions are no longer confined to the United States by definition. In practice the five United States jurisdictions continue: nothing here abolishes them, and doing so would take a further amendment.",
  },
  14: {
    summary:
      "Added outright: each conference acts autonomously within its own powers, and legislation is not void merely for overlapping another conference’s.",
    whatChanged:
      "The only paragraph the amendment adds. It states that General, regional, jurisdictional and annual conferences each have autonomy of action within constitutional limits, and then supplies a savings rule: where one conference’s legislation overlaps another’s powers, the overlap alone does not invalidate it. Only legislation whose “purpose and substance are beyond the authority of the enacting body” fails. With four tiers of conference now holding overlapping competences, this is what keeps ordinary overlap from becoming a constitutional question.",
  },
  16: {
    summary:
      "How many delegates each annual conference sends — and, newly, who sets that ratio for jurisdictional conferences.",
    whatChanged:
      "General Conference still fixes representation in the General and regional conferences, on the same two-factor basis of clergy members and professing members. The new material is the second half: in a region that has jurisdictions, the regional conference rather than General Conference fixes the ratio for those jurisdictional conferences. It also provides that all General and regional conference delegates are members of their respective jurisdictional conferences.",
  },
  17: {
    summary:
      "What General Conference may legislate — including, newly, what it may place beyond a region’s reach.",
    whatChanged:
      "The ballot reproduces only the five sub-items it changes. Three are terminology. Two are not. ¶17.12 lets General Conference change the number and boundaries of regional conferences. And ¶17.17 is new: General Conference may legislate what is non-adaptable for regional conferences by a 60% majority vote. That threshold is the hinge of the whole plan — it settles who draws the line between what a region may change and what it may not, and at what margin. It is also the provision the public explainers almost never mention.",
  },
  24: {
    summary: "How many delegates a jurisdictional conference has.",
    whatChanged:
      "The uniform basis for jurisdictional representation passes from General Conference to “the regional conference where jurisdictions exist” — in practice the United States Regional Conference, once it exists. The floor of 100 delegates is unchanged.",
  },
  25: {
    summary: "All jurisdictional conferences have the same standing as one another.",
    whatChanged:
      "Unchanged in substance. The ratio of representation must now be the same across jurisdictions for the regional conference as well as for General Conference.",
  },
  26: {
    summary: "Who fixes the basis of representation in jurisdictional conferences.",
    whatChanged:
      "General Conference is replaced by the regional conference where jurisdictions exist. The requirement of equal clergy and lay delegates is untouched.",
  },
  27: {
    summary: "When and where a jurisdictional conference meets, and who decides.",
    whatChanged:
      "The timing decision moves from the Council of Bishops — a worldwide body — to the College of Bishops of the regional conference where jurisdictions exist. Scheduling United States jurisdictional conferences becomes a United States matter.",
  },
  28: {
    summary:
      "What a jurisdictional conference may do. It keeps the power to elect bishops.",
    whatChanged:
      "The ballot reproduces only items 4 to 6. Items 1 to 3 are unchanged, which is why jurisdictions keep the power to elect bishops — a point worth stating plainly, because the reproduced text alone does not show it. Of the three shown: annual conference boundaries falling below the fifty-clergy floor now need the consent of the regional conference rather than General Conference; jurisdictional rule-making is now subject to regional conferences as well as General Conference; and the committee on appeals now hears lay as well as clergy appeals.",
  },
  29: {
    summary:
      "Creates the regional conferences by name — including a United States regional conference, which did not previously exist.",
    whatChanged:
      "The substantive centre of the amendment. It establishes regional conferences for the worldwide church with powers “to be exercised equitably across the regional conferences,” then names them: one for the United States comprising all the territory of the five jurisdictions, and the existing central conferences, which become regional conferences. General Conference may change the number and boundaries afterwards. Note that the text fixes no total — it inherits whatever central conferences existed before the postponed 2020 General Conference, which is why published counts of “how many regions” disagree with one another.",
  },
  30: {
    summary: "How many delegates a regional conference has.",
    whatChanged:
      "Terminology only. General Conference still establishes the basis, and delegates are still clergy and lay in equal numbers.",
  },
  31: {
    summary: "Regional conferences meet in the year following General Conference.",
    whatChanged:
      "Terminology, plus the removal of a spent provision about the first meeting after the 1968 Uniting Conference.",
  },
  32: {
    summary:
      "What a regional conference may decide for itself. The adaptation powers, and what bounds them.",
    whatChanged:
      "The longest and most consequential paragraph in the amendment, expanded from about 1,500 characters to nearly 4,000, with seven powers. Item 5 is the one that matters: a region may adapt the general Discipline, and its sub-items name how far that reaches — a published regional Discipline covering clergy qualifications and educational requirements; standards for admitting lay members; a regional hymnal and ritual “including ecclesial acts of marriage and burial,” subject to the first and second Restrictive Rules; and adaptation of the investigative and trial process, with confidentiality and protections for accused and accusers guaranteed. Item 6 permits a regional judicial court for questions arising under the regional Discipline. Item 2 lets regions without jurisdictions elect bishops and fix their tenure. All of it runs “in accordance with ¶16.17” — bounded by whatever General Conference has declared non-adaptable by a 60% vote.",
  },
  33: {
    summary: "Who sits in an annual conference.",
    whatChanged:
      "Most of this change has nothing to do with regionalization: it adds two young people per district as lay members. The regionalization element is a single sentence letting annual conferences in regions outside the United States waive the four-year participation and two-year membership requirements for members under thirty.",
  },
  34: {
    summary:
      "The annual conference is the basic body of the church, and this is what it votes on.",
    whatChanged:
      "The list of bodies it elects delegates to is restated for the new structure — General Conference and its regional conference, plus a jurisdictional conference where its region has them. Its reserved rights are untouched: constitutional amendments, the character and conference relations of its clergy, and ordination.",
  },
  35: {
    summary: "How an annual conference elects its delegates, and how reserves cascade.",
    whatChanged:
      "Rewritten to run on three tiers rather than two. Delegates are elected to General Conference and to the regional conference, with the additional regional delegates serving as General Conference reserves as before. Where a region has jurisdictions, all General and regional delegates are also jurisdictional delegates, and reserve delegates carry over in order of election.",
  },
  36: {
    summary: "Who may be elected a clergy delegate, and who may vote for one.",
    whatChanged:
      "The list of conferences is restated for the new structure. The substantive change is that local pastors qualify with course of study or an M.Div. “or its equivalent in regional conferences outside of the USA” — an accommodation for regions whose theological education does not map onto United States degrees. This paragraph was also amended by Amendment IV on the same ballot, which set educational requirements for clergy voting for delegates; both passed.",
  },
  37: {
    summary: "Who may be elected a lay delegate.",
    whatChanged:
      "Terminology. The two-year membership and four-year participation requirements are unchanged.",
  },
  39: {
    summary:
      "Struck. The provision that formed the church outside the United States into central conferences.",
    whatChanged:
      "Struck outright. It authorised forming the work outside the United States into central conferences and let General Conference change their number and boundaries thereafter. Both functions move into ¶29, which establishes regional conferences and gives General Conference the same authority over their boundaries.",
  },
  40: {
    summary: "Struck. The provision governing changes to jurisdictional boundaries.",
    whatChanged:
      "Struck, but not abolished — its content moves into ¶17.12, which keeps the requirement that a majority of the annual conferences in each jurisdiction involved must consent before jurisdictional boundaries change.",
  },
  41: {
    summary:
      "Who determines the names and boundaries of annual conferences and episcopal areas.",
    whatChanged:
      "Simplified. The old paragraph named jurisdictional conferences for the United States and central conferences elsewhere; the new one says the regional conference, or the jurisdiction where a region has them. Its article number moves from IV to II because the two paragraphs before it are struck.",
  },
  47: {
    summary: "Who elects bishops, and when.",
    whatChanged:
      "Bishops are elected by the regional conference, or by the jurisdiction where a region has jurisdictions. The time and place of consecration passes from General Conference to each regional conference. The bar on electing bishops at extra sessions now attaches to regional conferences without jurisdictions.",
  },
  49: {
    summary:
      "The bishops of a region or jurisdiction form a College, which arranges episcopal supervision.",
    whatChanged: "Terminology only.",
  },
  50: {
    summary: "Where a bishop serves, and the conditions for transferring one.",
    whatChanged:
      "The transfer machinery between jurisdictions is unchanged in substance — consent of the bishop, a quadrennium served, approval by both jurisdictional committees on episcopacy. The surrounding language is restated for regions, and emergency assignment now runs between regional conferences. The drafting repeats “if a regional conference has jurisdictions” five times in the closing sentence; awkward, but not ambiguous.",
  },
  51: {
    summary:
      "How long a bishop serves — which is not the same in every region.",
    whatChanged:
      "Bishops elected by jurisdictions have life tenure. Bishops elected by a regional conference without jurisdictions serve whatever term that conference sets. The distinction is not new: the old paragraph already gave jurisdiction-elected bishops life tenure and let each central conference set its own. But it survives into a structure otherwise built on parity, and because the United States is the only region with jurisdictions, life tenure remains in practice a United States arrangement. The paragraph also drops the spent 1968 union provisions and moves the committee on episcopacy to the regional conference or jurisdiction.",
  },
  53: {
    summary: "Which bishops preside over which conferences.",
    whatChanged:
      "Bishops preside in their regional conference, and also in their jurisdictional conference where the region has jurisdictions.",
  },
  57: {
    summary: "What the Judicial Council may rule on.",
    whatChanged:
      "Two of the four sub-items are reproduced, both amended only to add regional conferences alongside jurisdictional ones. What the amendment does not address is how the Judicial Council relates to the regional judicial courts that ¶32.6 permits. It creates the courts and leaves the relationship unstated.",
  },
  62: {
    summary:
      "A regional or jurisdictional conference may propose amendments to the Constitution.",
    whatChanged:
      "Terminology, plus a transitional sentence requiring that ratification of this petition begin within thirty days of the close of the postponed 2020 General Conference.",
  },
};
