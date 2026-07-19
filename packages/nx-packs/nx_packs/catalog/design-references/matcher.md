# How the reference matcher works

The matcher is **deterministic tag overlap** — no embeddings, no model, no
network. It lives in `nx_packs.references` and is pure organization: it narrows
the library to the references whose declared context actually appears in the
prompt, then hands the ranked shortlist to the model. The aesthetic decision stays
with the model.

## Algorithm

1. **Tokenize the prompt** — lowercase, strip accents (`salão` → `salao`), split
   on non-alphanumerics into a set of tokens.
2. **Score each reference** by weighted tag overlap. A tag *term* scores only when
   **every** token of that term is present in the prompt (so the two-word term
   `beauty salon` needs both words, while a bare `beauty` keyword needs one):

   | Tag group  | Weight | Why |
   |------------|:------:|-----|
   | `vertical` |  3.0   | Names the kind of site — the strongest signal |
   | `industry` |  2.0   | Domain synonyms (EN + PT-BR) |
   | `mood`     |  2.0   | Aesthetic intent (`elegant`, `bold`, `coastal`) |
   | `keywords` |  2.0   | Vocabulary the user is likely to type |

3. **Rank** by score descending; ties break by `id` (stable, reproducible).
   References scoring zero are dropped. Empty result ⇒ no reference is injected
   and the model chooses.

## Why tags, not embeddings

It matches the platform doctrine — **packs organize data; the model reasons.**
Tag matching is transparent (you can see *why* a reference won), dependency-free,
and reproducible in tests. `mood` terms are what separate two references in the
same vertical: `salão de beleza elegante` → Espaço Ellen Souza, while `salão de
beleza de luxo` → Odara Li.

## Extending the library

Drop a new `references/<id>.json` (conforming to `references/schema.json`) into the
pack. Rich, honest `industry` / `mood` / `keywords` — in the languages your users
type — make the reference findable. No code change required; the matcher reads the
directory. Third parties can ship additional reference packs the same way.
