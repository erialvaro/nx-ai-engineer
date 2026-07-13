# SEO anti-patterns (never do)

## Indexation
- **`noindex` on a page meant to rank** (often a leftover from staging). Blocks
  ranking entirely.
- **Conflicting/incorrect canonicals** — pointing many pages at one, cross-domain
  canonicals by accident, or canonical ≠ the indexable URL.
- **Blocking CSS/JS in `robots.txt`** — Google can't render/evaluate the page.
- Using `robots.txt` `Disallow` to "hide" a page while still linking it — it may
  still be indexed URL-only; use `noindex` instead.
- **Soft-404s** — returning `200` for missing content; and redirect chains/loops.
- **Crawl traps** — faceted/filter/sort/session params generating infinite URLs.

## Rendering
- **JS-only critical content** — content/metadata that only appears after client
  hydration. Googlebot may defer it; most AI crawlers won't see it at all.
- Cloaking — serving different content to bots than to users.

## Content
- Duplicate/boilerplate titles & meta descriptions across pages; missing or
  multiple `H1`s.
- **Thin/duplicate content**, keyword stuffing, doorway pages, auto-generated
  spam. Orphan pages with no internal links.
- Non-descriptive anchors ("click here"); images without meaningful `alt`.

## Structured data
- JSON-LD that **doesn't match visible content**, or marks up hidden/absent data
  (spammy structured data → manual action). Invalid/again-required types.

## Performance
- Unoptimized/unsized images (CLS + slow LCP); render-blocking resources; huge JS
  bundles; late-loading fonts without `font-display`; injecting ads/embeds that
  shift layout (CLS); intrusive interstitials.

## Internationalization
- Non-reciprocal or wrong-region `hreflang`; missing `x-default`; `noindex` on
  alternate locales; auto-redirect by IP without a crawlable default.

## AI discoverability
- Blocking all AI crawlers by default **without a decision** (loses AI-answer
  visibility) — or allowing them by accident when content is sensitive. Either way,
  make it a documented choice.
- Walls of unstructured prose with no headings/lists — hard for AI to extract and
  cite.
