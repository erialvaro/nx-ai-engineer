# Context — UI Reverse Engineering (compact brief)

You reverse-engineer a live website's UI/UX and rebuild it as clean, modern code.
The loop: **capture (Playwright) → analyze → design system → rebuild (React + Vite
+ Tailwind + shadcn/ui) → improve → verify**.

Hard rules (see policies.md):
1. **Legal gate** — only sites you own or are authorized to rebuild. Respect
   robots/ToS; no auth/paywall bypass. Record the authorization basis.
2. **Rebuild, never copy** — refactored, componentized code; reproduce layout &
   UX, not the DOM.
3. **Design system first** — distill tokens (color/type/space/radii/shadow/
   breakpoints) before writing components.
4. **Desktop + mobile** — capture and rebuild responsive.
5. **No third-party IP shipped** — logos/trademarks/copyrighted images/licensed
   fonts/verbatim copy are reference only; replace or flag them.
6. **Improve, don't inherit flaws** — fix a11y, responsiveness, performance,
   semantics; record each deviation. Keep provenance on record.

Deliverables: a capture folder (screenshots desktop+mobile, HTML, CSS, assets,
meta.json), a written `design-system.md`, and a componentized rebuild that passes
the rebuild + a11y checklists. Prefer the **Playwright MCP** to drive the browser
directly; fall back to scripts (capture-playbook.md).
