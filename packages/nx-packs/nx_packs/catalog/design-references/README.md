# Design Reference Library

A curated library of **design-reference profiles** distilled from real, shipped
websites. Each profile captures a coherent visual identity — **palette (light +
dark), type pairing, layout concept, mood and vertical** — as structured data.

When you ask the `designer`/`frontend` agents to build a site, NX matches your
prompt to the closest reference by **deterministic tag overlap** and injects it
into the agent's Engineering Contract. The agent then generates UI *in the style
of* that reference — grounded in a concrete visual language — instead of inventing
tokens from nothing. The reference is a **starting point to adapt, never a clone**.

## What a reference contains

See `references/schema.json`. Every profile declares `id`, `name`, `source`,
`vertical`, `industry`, `mood`, `keywords`, a `palette` (light + dark token roles)
and a `typography` pairing (display + body, optional accent), plus `layout`,
`components` and `notes`.

## Seed library

| id | vertical | mood | palette anchor | type pairing |
|----|----------|------|----------------|--------------|
| `hs-motors` | car-dealership | bold, trustworthy | red on near-black | Clash Display + Satoshi |
| `espaco-ellen-souza` | beauty-salon | elegant, feminine | rose + gold on cream | Playfair Display + Jost |
| `luque-construcoes` | construction | industrial, strong | orange on near-black | Archivo + Inter |
| `atelie-simone` | stationery | playful, handmade | pinks on cream | Pacifico + Nunito |
| `odara-li` | beauty-salon | luxury, warm | gold on cream | Fraunces + Inter |
| `pousada-luz-do-sol` | hospitality | coastal, boutique | terracotta + teal on sand | Fraunces + Plus Jakarta Sans |
| `sweetags` | design-agency | bold, creative | neon-yellow + violet on cream | Avenir Next + Wix Madefor |
| `myfots` | fashion | minimal, timeless | sage + near-black (mono) | Roboto Mono + Helvetica Neue |
| `petala-beauty` | cosmetics | feminine, modern | rose on deep navy | Geist |
| `vicshop` | fashion | minimalist, sophisticated | terracotta on charcoal | Montserrat + Quicksand |
| `fwr-agencia` | digital-agency | bold, techy, dark | neon-green on near-black | Comfortaa + Inter |
| `liloca` | fashion | playful, feminine | green + pink + mint | Dancing Script + Montserrat |
| `tapetes-sao-jose` | home-decor | warm, artisanal | terracotta + olive on slate | Plus Jakarta Sans |
| `lp-max-suzuki` | car-dealership | modern, conversion | indigo + red (LP) | Poppins |
| `hostinger` | web-hosting | modern, trustworthy | Hostinger purple on white + violet dark | DM Sans |

## Usage

```bash
nxai pack add design-references          # install into .ai-project-assistant/packs
nxai design ref list                     # list the library
nxai design ref show espaco-ellen-souza  # full profile (tokens + type)
nxai design ref match "salão de beleza elegante"   # see what the prompt selects
```

Once installed, the reference is selected automatically whenever a `designer`/
`frontend` contract is built for a matching prompt — no extra flags.

## How matching works

Deterministic tag overlap (`vertical` ×3, `industry`/`mood`/`keywords` ×2), ties
broken by `id`. Transparent and reproducible — details in `matcher.md`.

## Extending

Add `references/<id>.json` (conforming to the schema) with honest `industry` /
`mood` / `keywords` in the languages your users type. No code change needed — the
matcher reads the directory. This pairs with the `design` pack (tokens, WCAG,
motion, states), which still enforces all quality gates on the generated output.
