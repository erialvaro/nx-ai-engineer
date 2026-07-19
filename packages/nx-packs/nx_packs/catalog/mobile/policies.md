# Mobile — policies (non-negotiable)

- **Managed Expo + New Architecture.** Stay in the managed workflow on the current
  Expo SDK; ejecting or adding a bare native module requires a documented reason.
- **Native, not a WebView.** Build real native screens. Wrapping a website in a
  WebView and calling it an app is forbidden.
- **Typed, complete navigation.** Routes and params are typed; every screen is
  reachable with a back path; Android hardware back and deep links both work.
- **Secrets in secure storage.** Tokens/credentials live in `expo-secure-store`
  (Keychain/Keystore) — never AsyncStorage, never hard-coded or bundled in JS.
- **Tokens are the single source of truth.** One theme (NativeWind/theme module),
  **light AND dark**, honoring the OS setting; no magic values in screens.
- **Every state, every screen.** loading / empty / error / success + offline —
  the happy path alone is not done.
- **Performance is a gate.** Virtualized lists with stable keys; animations on the
  UI thread (Reanimated/native driver); sized+cached images; Hermes. No JS-thread
  layout animation, no unbounded lists.
- **Accessibility is a gate.** Touch targets >= 44x44pt, labels/roles, reduce-
  motion respected, safe-area honored.
- **Release through EAS.** Builds/updates/submissions go through EAS; OTA updates
  ship JS only — native changes require a new build. Never ship debug keys.
- **Permissions in context.** Request at point-of-use with a rationale; the app
  must still work (degraded) when a permission is denied.
