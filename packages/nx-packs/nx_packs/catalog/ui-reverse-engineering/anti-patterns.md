# Anti-patterns — UI Reverse Engineering (never do)

- **Literal HTML/CSS paste.** Shipping the scraped DOM (or a lightly-edited
  version) instead of refactored components. The DOM is reference, not source.
- **Pixel-cloning.** Copying exact px/hex everywhere instead of distilling a token
  scale. You end up with 40 shades of gray and no system.
- **Shipping third-party IP.** Reusing the source's logo, brand name, trademarked
  marks, copyrighted photos, licensed fonts, or verbatim copy in the rebuild.
- **Ignoring the legal gate.** Rebuilding a site you don't own or aren't
  authorized to, bypassing paywalls/auth, or ignoring robots.txt/ToS.
- **Crawling the whole site.** Hammering the origin with hundreds of requests.
  Capture the pages you need; respect rate limits.
- **Desktop-only capture.** Rebuilding responsive UI from a single viewport.
- **Inheriting the flaws.** Reproducing the source's a11y bugs, contrast failures,
  keyboard traps, missing alt, and bloated DOM as if they were requirements.
- **God-components.** One `Page.tsx` with everything, instead of role-named,
  reusable pieces.
- **Hardcoded content in JSX.** Baking copy/data into components instead of
  passing it as props/data (kills i18n and reuse).
- **No provenance.** A rebuild with no record of source URL, date, or the
  authorization basis.
- **Style dumps.** Pasting the extracted CSS into a global sheet instead of
  mapping it to Tailwind tokens / component styles.
