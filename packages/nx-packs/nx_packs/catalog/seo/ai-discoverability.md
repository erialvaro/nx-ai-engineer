# AI / LLM discoverability (GEO)

Answer engines — **Google AI Overviews**, ChatGPT search, Claude, Perplexity,
Bing Copilot — increasingly mediate discovery. **Generative Engine Optimization
(GEO)** makes your content easy for them to **fetch, parse, trust, and cite**.
It overlaps heavily with good classic SEO, plus a few AI-specific practices.

## Make content machine-extractable
- **Server-render** the substance. Many AI crawlers fetch raw HTML and do **not**
  execute JavaScript — JS-only content is invisible to them.
- **Answer-first**: lead with a direct, factual answer, then elaborate. Use clear
  `H2/H3` that mirror real questions; use **lists, tables, and FAQ** blocks that
  extract cleanly.
- Keep facts **self-contained** (don't require scrolling context); state units,
  dates, and definitions explicitly.

## Establish entity & trust (E-E-A-T)
- Consistent entity naming; `Organization`/`Person` schema with `sameAs` to
  authoritative profiles so engines resolve who you are.
- **E-E-A-T signals**: named authors with bios/credentials, cited sources,
  original data/experience, visible `datePublished`/`dateModified`.
- Consistent NAP and facts across the site and third-party profiles.

## `llms.txt`
- Publish **`/llms.txt`** — a curated, Markdown map of your most important pages
  (and optionally `/llms-full.txt` with expanded content) so LLM tools can find
  the canonical, high-value content quickly. Keep it current with the sitemap.

Example `llms.txt`:
```
# Acme
> One-line description of what Acme does.

## Docs
- [Getting started](https://acme.com/docs/start): install and first run
- [API reference](https://acme.com/docs/api): endpoints and auth

## Product
- [Pricing](https://acme.com/pricing): plans and limits
```

## AI-crawler policy (deliberate)
Decide **on purpose** whether to allow AI training/answer crawlers, and document
it in `robots.txt`:
```
# Allow AI answer engines to cite us (recommended for marketing/docs)
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
# (Set Disallow instead to opt out — e.g. for sensitive or paywalled content.)
```
Note: `Google-Extended` governs Gemini/Vertex use and does **not** affect normal
Google Search indexing; `GPTBot`/`ClaudeBot`/`PerplexityBot`/`CCBot` govern those
engines. Blocking them removes you from AI answers — make it a choice, not a default.

## Measure
- Track referral/brand mentions from AI engines where possible; monitor whether
  key questions surface your content in AI Overviews/answers; keep facts fresh.
