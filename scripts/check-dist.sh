#!/usr/bin/env bash
# Pre-deploy gate. Run against dist/ after a CLEAN build.
# Same rationale as ~/denominations/scripts/check-dist.sh: Astro's content layer
# persists entries in node_modules/.astro/data-store.json, so a paragraph deleted
# from src/content/paragraphs/ keeps building and keeps deploying until that store
# is cleared. Always `pnpm run build:clean` first.

set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

[ -d dist ] || { echo "FAIL: no dist/ — run pnpm run build:clean first"; exit 1; }

# 1. Placeholder prose.
for marker in lorem ipsum TKTK TODO FIXME "placeholder"; do
  if grep -ril --include="*.html" "$marker" dist/ >/dev/null 2>&1; then
    echo "FAIL: placeholder marker '$marker' in dist/:"
    grep -ril --include="*.html" "$marker" dist/ | sed 's/^/    /'
    fail=1
  fi
done

# 2. Every emitted paragraph page must still have a source file.
for page in dist/p/*/; do
  [ -d "$page" ] || continue
  n=$(basename "$page")
  if ! grep -qs "^disciplineNumber: ${n}\$" src/content/paragraphs/*.yaml; then
    echo "FAIL: dist/p/${n}/ has no source file — stale content-layer entry."
    echo "      Fix: rm -rf node_modules/.astro dist && pnpm build"
    fail=1
  fi
done

# 3. The count must match the amendment's declared scope: 26 + 2 + 1.
n=$(find dist/p -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
if [ "$n" != "29" ]; then
  echo "FAIL: expected 29 paragraph pages, found ${n}."
  fail=1
fi

# 4. The provisional-text notice must survive on the sources page.
if ! grep -qs "post-ratification text here is the ballot text" dist/sources/index.html; then
  echo "FAIL: the provisional-text notice is missing from /sources."
  fail=1
fi

# 5. The site quotes copyrighted text under a fair-use rationale. The attribution
#    is the thing that makes that posture defensible, so it is gated, not trusted:
#    it must appear on EVERY page, and the rights page must exist.
missing=0
while IFS= read -r f; do
  grep -qs "United Methodist Publishing House" "$f" || { missing=$((missing+1)); echo "    ${f#dist/}"; }
done < <(find dist -name "*.html")
if [ "$missing" -gt 0 ]; then
  echo "FAIL: UMPH attribution missing from ${missing} page(s) (listed above)."
  fail=1
fi
if ! grep -qs "creativecommons.org/licenses/by-nc/4.0" dist/rights/index.html; then
  echo "FAIL: /rights is missing or does not state the licence."
  fail=1
fi

[ "$fail" -eq 0 ] && echo "OK: dist/ is clean — 29 paragraphs, notice intact."
exit "$fail"
