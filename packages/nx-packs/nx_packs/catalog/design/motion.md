# Motion system (framer-motion)

Motion **explains change**: what appeared, what moved, what relates to what. If it
doesn't explain something, cut it.

## Install
```bash
npm i framer-motion
```

## The scale (tokens, not vibes)
| Duration | Use |
|----------|-----|
| **150ms** (fast) | hover, small state changes, tooltips |
| **250ms** (base) | most transitions: dropdowns, tabs, cards |
| **400ms** (slow) | page/section transitions, large surfaces |

| Easing | Use |
|--------|-----|
| `easeOut` | **entering** (fast start, gentle settle) |
| `easeIn` | **exiting** |
| `easeInOut` | movement between two on-screen states |
| spring (stiffness ~300, damping ~30) | playful/physical UI (drag, sheets) |

Enter is faster than exit is a myth — in practice: **enter with `easeOut`, exit
slightly faster with `easeIn`.**

## Patterns
```tsx
<motion.div
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -8 }}
  transition={{ duration: 0.25, ease: 'easeOut' }}
/>
```
- **Fade + small translate (4–12px)** beats big flourishes.
- `AnimatePresence` for mount/unmount; `layout` for shared-layout moves.
- Stagger lists subtly (`staggerChildren: 0.04`) — never a slow cascade.
- Animate **`transform` and `opacity`** only (GPU-friendly). Never animate
  `width/height/top/left` — that's layout thrash and CLS.

## Reduced motion (mandatory)
```tsx
const reduce = useReducedMotion();
<motion.div animate={reduce ? { opacity: 1 } : { opacity: 1, y: 0 }} />
```
Also respect it in CSS:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

## Rules
- Motion is **never blocking** — content must be usable immediately.
- No infinite/looping animation near content (attention theft, accessibility risk).
- Motion must not cause **layout shift** (CLS) — reserve space.
