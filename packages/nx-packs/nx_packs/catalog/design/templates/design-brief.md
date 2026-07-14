# Design brief & handoff spec

Fill before designing; deliver as the handoff to `frontend`.

## Brief
- **Screen/component:**
- **Job to be done / user goal:**
- **Audience & device priority:** (mobile-first? desktop app?)
- **Primary action (one):**
- **Content/copy source:** (coordinate with `copywriter`)
- **Style direction:** (from `ui-ux-pro-max`; e.g. minimal, bento, glassmorphism)
- **Reuse check:** existing component/token or 21st.dev catalog hit? ☐ yes ☐ no

## Tokens used (semantic names, not hexes)
| Role | Token | Light | Dark |
|------|-------|-------|------|
| background | `--background` | | |
| foreground | `--foreground` | | |
| primary | `--primary` | | |
| border/ring | `--border` / `--ring` | | |
| type scale | | | |
| spacing | | | |
| radius / shadow | | | |

## Layout & responsive
- Grid / max-width:
- Breakpoint behavior (what reflows):

## States (all required)
| State | Spec |
|-------|------|
| default | |
| hover | |
| focus | (visible ring — token `--ring`) |
| active | |
| disabled | |
| **loading / skeleton** | |
| **empty** | |
| **error** | |
| success | |

## Motion
- Transition: | Duration token: | Easing: | Reduced-motion path:

## Accessibility (evidence, not opinion)
| Check | Result | Evidence |
|-------|--------|----------|
| Contrast ≥ 4.5:1 text / 3:1 large+UI — **light** | | |
| Contrast — **dark** | | |
| Keyboard reachable + visible focus | | |
| Semantic + labelled; target ≥ 24px | | |
| `prefers-reduced-motion` honored | | |

## Performance
| Check | Result |
|-------|--------|
| Media has explicit dimensions (no CLS) | |
| LCP element is light / prioritized | |

**Handoff is done** only when a frontend engineer could build this without asking
a single question.
