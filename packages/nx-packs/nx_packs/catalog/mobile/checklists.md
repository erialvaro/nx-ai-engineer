# Mobile — checklist

- [ ] App boots on **iOS and Android** (Expo Go / dev build) with no red screen
- [ ] Navigation typed; every screen reachable with a back path; deep links + Android back work
- [ ] Theme tokens are the single source of truth; **light + dark** honor the OS setting
- [ ] Every screen has loading / empty / error / success states; offline handled
- [ ] Long lists virtualized (FlatList/FlashList) with stable `keyExtractor`
- [ ] Animations run on the UI thread (Reanimated / native driver)
- [ ] Images via `expo-image`, sized and cached; no memory leaks (listeners/timers cleaned up)
- [ ] Secrets in `expo-secure-store`; no plaintext tokens; no secrets bundled in JS
- [ ] Touch targets >= 44x44pt; a11y labels/roles; reduce-motion respected; safe-area insets applied
- [ ] Permissions requested in context with rationale; graceful when denied
- [ ] Config via `app.config` + EAS env; build/update/submit via **EAS**
- [ ] (If reference injected) palette + type pairing adapted into the mobile theme — not cloned
