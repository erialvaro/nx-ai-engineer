# Design References context (injected brief)

You have a **library of design references** — visual identities distilled from
real, shipped websites. Each reference declares a **palette (light + dark)**, a
**type pairing**, a **layout concept**, a **mood** and the **vertical** it serves.

**How to use it:**
1. **Match the prompt to a reference.** NX pre-selects the best-fit reference by
   tag overlap (vertical / industry / mood / keywords) and injects it into your
   contract as `design_reference`. If one was injected, treat it as the visual
   **starting point**. If none matched, pick the closest by judgement or design
   from first principles.
2. **Adapt, don't clone.** Turn the reference palette into **project tokens**
   (CSS vars / Tailwind / shadcn `components.json`) — roles, not magic values —
   and derive the **dark** theme alongside light. Honor the type pairing (display
   + body) or document a justified substitute. The result must read as the
   client's **own brand**, never a pixel-copy of the source.
3. **Everything the `design` pack mandates still applies** — tokens as the single
   source of truth, WCAG-passing contrast in both themes, every state specified,
   motion with a system, no CLS. A reference sets the *style*; it never waives the
   *gates*.

**Matching is deterministic and transparent** (see `matcher.md`): it only narrows
the field to references whose declared context actually appears in the prompt. The
aesthetic decision — which to use and how to adapt it — is **yours**.

Inspect the library any time with `nxai design ref list` / `nxai design ref show
<id>` / `nxai design ref match "<prompt>"`.
