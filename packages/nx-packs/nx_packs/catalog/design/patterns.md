# Design patterns (do this)

## System
- **Token-first**: define the token before the component. If a component needs a
  value the system doesn't have, add the token deliberately — don't hardcode.
- **Compose, don't fork**: variants (size/tone/state) over near-duplicate components.
- **Reuse before create**: search the 21st.dev catalog / existing components first.

## Screens
- **One focal point** per screen; one primary action (everything else is secondary
  or tertiary).
- **Hero → proof → CTA** for marketing; **sidebar + content** for apps;
  **bento grid** for feature overviews; **card grid** for collections.
- Progressive disclosure: show what's needed, reveal the rest on intent.

## Components — always specify all states
`default · hover · focus · active · disabled · loading (skeleton) · empty · error · success`
- **Skeletons** that match the real layout (no spinner-on-blank-page).
- **Empty states** teach: an icon, one line of what's missing, and the action.
- **Errors** are specific, next to the cause, and recoverable.

## Forms
- One column; real labels above the field; helper text below; inline validation
  **on blur**, not on every keystroke. Errors say what to do, not just "invalid".
- Primary action on the right/end; destructive actions need confirmation.

## Feedback
- Optimistic UI where safe; otherwise a clear pending state on the control itself.
- Toasts for transient, non-blocking outcomes; inline for anything the user must fix.

## Dark mode
- Design it: deep-neutral background, off-white foreground, elevation via lighter
  surfaces (not heavier shadows). Re-verify all contrast pairs.

## Handoff
- Deliver a **spec** (tokens + states + behavior + motion), not a picture. The
  `frontend` agent should never have to guess a value.
