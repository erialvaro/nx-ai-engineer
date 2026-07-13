# Structured data (schema.org / JSON-LD)

Structured data lets search **and AI engines** understand entities and produce
rich results / cited answers. Prefer **JSON-LD** in a `<script type="application/
ld+json">`, rendered server-side, **matching the visible content**.

## Site-wide (every page)
- **Organization** (name, url, `logo`, `sameAs` → social/authoritative profiles).
- **WebSite** with **`potentialAction` → SearchAction** (sitelinks search box).

## Per template
- **BreadcrumbList** — on any page below the top level (shows breadcrumbs in SERPs
  and clarifies hierarchy to AI).
- **Article / BlogPosting** — `headline`, `author` (Person, with `sameAs`),
  `datePublished`/`dateModified`, `image`, `publisher`.
- **Product** + **Offer** — `name`, `image`, `description`, `sku`, `brand`,
  `offers` (price, priceCurrency, availability), `aggregateRating`/`review` (only
  if genuinely shown).
- **FAQPage** — Q&A that is actually visible on the page (great for AI answers).
- **LocalBusiness** — NAP (name/address/phone), `openingHours`, `geo` for local.
- **HowTo**, **Event**, **Recipe**, **VideoObject**, **JobPosting** as applicable.

## Example — Article (JSON-LD)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How X Works",
  "author": { "@type": "Person", "name": "Jane Doe",
              "sameAs": "https://www.linkedin.com/in/janedoe" },
  "datePublished": "2026-01-10",
  "dateModified": "2026-02-01",
  "image": "https://example.com/x.png",
  "publisher": { "@type": "Organization", "name": "Acme",
                 "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png" } }
}
```

## Rules
- Generate JSON-LD from the **same data** that renders the page (no drift).
- Never mark up hidden, absent, or fabricated data (risk: manual action).
- Validate with the **Rich Results Test** + schema.org validator before merge.
- Keep `@id`/`sameAs` consistent across pages so engines resolve one entity.
