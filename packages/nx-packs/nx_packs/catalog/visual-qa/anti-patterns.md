# Anti-Patterns — the bugs this pack exists to kill

## Layout
- **Horizontal overflow** — a fixed-width element, un-shrunk flex child
  (`min-w-0` missing), or an unwrapped long string pushes the page wider than the
  viewport. The #1 responsive defect.
- **Clipped / off-screen controls** — a button or menu slides outside the
  viewport or is cut off by `overflow: hidden` on a parent.
- **Broken navbar** — the header wraps, overlaps, or the mobile menu is
  unreachable at phone widths.
- **Desktop-first CSS** — building for 1920px then patching with `max-*`
  overrides; inverts the cascade and breeds overflow.
- **Text overflow** — copy spills its card or truncates meaning; padding
  collapses at small widths.

## Shift & media
- **Unsized media** — `img`/`video`/`iframe` with no dimensions → layout shift
  (CLS) as they load.
- **Late webfont reflow** — text re-lays-out when the font swaps in.

## Accessibility
- **`outline: none`** with no visible focus replacement.
- **Color-only state**, low contrast in dark mode, unlabeled icon buttons.
- **Tap targets < 44px**, crammed together.

## Process
- **Testing one viewport** (usually the dev's desktop) and calling it responsive.
- **Screenshotting a mock** instead of the running app.
- **Blindly overwriting BackstopJS baselines** to make the diff pass — that
  approves the regression.
- **QA editing product source** — forks ownership; the fix belongs to the
  developer, QA verifies it.
- **Local-only gates** — thresholds that don't run in CI regress silently.
