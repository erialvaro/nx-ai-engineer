# SEO architecture

SEO is decided by architecture more than by tags. Get these right up front.

## Rendering strategy
- **SSG/ISR** for stable content (marketing, docs, blog) — fastest, most crawlable.
- **SSR** for fresh/personalized-but-indexable pages.
- **CSR** only for authenticated app UI that must **not** be indexed.
- Rule: anything that must rank or be cited by AI has its content + metadata in the
  **server HTML**.

## URL & site structure
- Clean, lowercase, hyphenated, human-readable, hierarchical URLs
  (`/blog/topic/post`), stable over time.
- Flat depth: important pages within ~3 clicks; hub-and-spoke internal linking.
- One canonical URL per piece of content; params (tracking/sort/filter)
  canonicalize back to it.

## Redirects & lifecycle
- Moves → `301`; removed → `410` (or `404`); never chain redirects; keep a
  redirect map. Preserve URLs across redesigns/migrations.

## Internationalization
- `example.com/es/…` or locale subdomains; reciprocal `hreflang` + `x-default`;
  localized content and metadata; each locale independently indexable.

## Delivery
- HTTPS everywhere (HSTS); HTTP/2+; CDN + caching; compress; fast TTFB (< 800ms).
- Generate `robots.txt`, XML sitemap(s), and `llms.txt` from the **router's source
  of truth** so they never drift from the live routes.

## Integration with the platform
- The `seo` agent owns SEO-dedicated files (robots/sitemap/structured-data/
  llms.txt) and coordinates page `<head>` metadata with the **frontend** agent.
- The generated **cloud-agnostic** foundation (Next.js) supports `output: standalone`
  SSR/SSG — a good base for SEO; add per-route metadata, JSON-LD, sitemap and
  `robots.txt` on top.
