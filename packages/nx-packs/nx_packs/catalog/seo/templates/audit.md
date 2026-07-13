# SEO audit template

Fill this per page/template and site-wide. Mark PASS / FAIL / N/A with evidence.

## Page: `<url>`
| Check | Result | Evidence |
|-------|--------|----------|
| Indexable (meta robots, one self-canonical) | | |
| Not accidentally `noindex` | | |
| Unique title (~50–60) + meta description (~150–160) | | |
| One H1 + semantic headings + alt text | | |
| Primary content in server HTML (view-source) | | |
| Valid JSON-LD matches content (Rich Results) | | |
| Open Graph + Twitter card | | |
| Core Web Vitals (LCP/INP/CLS) | | |
| Correct status code / HTTPS / no redirect chain | | |

## Site-wide
| Check | Result | Evidence |
|-------|--------|----------|
| `robots.txt` valid; CSS/JS not blocked; sitemap referenced | | |
| XML sitemap valid; indexable URLs only; `lastmod` | | |
| Clean URL scheme + canonicalization strategy | | |
| `hreflang` reciprocal + `x-default` (if i18n) | | |
| 404 returns 404; key 301s mapped | | |

## AI / LLM discoverability
| Check | Result | Evidence |
|-------|--------|----------|
| `llms.txt` present + current | | |
| Answer-first, structured, factual content | | |
| Entities + `sameAs` + E-E-A-T (author/sources/dates) | | |
| Deliberate AI-crawler policy in `robots.txt` | | |

**Verdict:** ship only when there are **no FAILs** on indexability, rendering,
structured data, and Core Web Vitals.
