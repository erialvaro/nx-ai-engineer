# Content architecture & workflow

How copy fits the platform and ships consistently.

## Roles
- **`copywriter`** owns marketing/content copy: landing/hero, blog/articles,
  product copy, newsletters, taglines (`content/`, `copy/`, `blog/`, `marketing/`,
  `*.mdx`).
- **`docs`** owns technical documentation (READMEs, guides, ADRs) — different job,
  different voice.
- **`seo`** owns technical SEO (robots/sitemap/structured data/CWV); the copywriter
  supplies the words and metadata. They coordinate on the `<head>`.
- **`frontend`** owns the components that render the copy.

## The brief (source of truth)
Every piece starts from a brief (`templates/brief.md`): audience, awareness stage,
goal/CTA, primary keyword + intent, voice/tone, proof points, format/length,
language. No brief → no draft.

## Content model
- Prefer **structured content** (front-matter: title, description, slug, author,
  date, keyword) in Markdown/MDX or the CMS, so metadata and copy live together
  and feed the sitemap + SEO consistently.
- One canonical piece per topic/intent (avoid cannibalizing your own keywords).

## Voice consistency
- Maintain a per-brand **style sheet** (terms, capitalization, do/don't words, CTA
  phrasing, PT-BR/EN rules) so everything sounds like one person.

## Fit with the foundation
- On a `nxai new` (Next.js) project, blog/marketing content is SSG/ISR — fast and
  crawlable. The copywriter writes the content + metadata; the `seo` agent wires
  JSON-LD, sitemap, and `llms.txt`; the `frontend` agent renders it.

## Definition of done
Human-sounding, technically accurate, one clear CTA, and SEO-ready (intent, title,
meta, internal links) — validated against both packs' checklists.
