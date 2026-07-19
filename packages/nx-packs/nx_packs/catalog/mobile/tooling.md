# Tooling (use it — don't hand-roll what exists)

- **Expo + React Native** — managed workflow, New Architecture, current SDK.
  `create-expo-app` / `npx expo` for scaffolding and running.
- **expo-router** — file-based, typed navigation (or **react-navigation** typed).
- **NativeWind** — Tailwind for React Native; the default styling/token layer
  (theme in `tailwind.config`, light + dark). Pairs with the design tokens a
  `design-references` profile provides.
- **React Native Reanimated** + **react-native-gesture-handler** — UI-thread
  animation and gestures.
- **TanStack Query** — server state, caching, offline.
- **expo-secure-store** — secrets/tokens (Keychain/Keystore).
- **expo-image** — sized, cached images.
- **react-hook-form** + **zod** — forms and validation.
- **EAS** — `eas build` / `eas update` / `eas submit` for build, OTA and store
  submission.
- **`mockup-app-skill`** — sketch the app's screens/flow (mockups) before wiring
  real data, when the skill is installed. Use it to align on layout/navigation
  early, then implement the real screens against the tokens.
- **design-references pack** — auto-attaches to the `mobile` agent; injects a
  palette/type/mood profile matched to the prompt. Adapt it into the mobile theme
  (NativeWind), light + dark — never clone.
- **Testing** — Jest + `@testing-library/react-native` for units;
  **Maestro**/Detox for E2E flows on a device/simulator.
