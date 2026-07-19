# Mobile context (injected brief)

You are building a **React Native + Expo** app — a native iOS/Android experience,
not a website in a WebView. Ship screens the user can actually run on a device.

**Always:**
- **Expo managed workflow + New Architecture.** Stay in the managed workflow and
  use Expo modules; don't eject or reach for a bare native module without a
  documented reason. Target the current **Expo SDK**.
- **Typed navigation.** Use **expo-router** (file-based) or **react-navigation**
  with typed routes/params. Every screen is reachable, has a back path, and no
  dead ends. Deep links and the Android hardware back button both work.
- **Tokens first, light + dark.** Colors, type scale, spacing, radius come from a
  **single source of truth** (NativeWind config / a theme module) that honors the
  **OS color scheme**. No magic values in screens. (The `design-references` pack
  may inject a palette/type reference — adapt it, don't clone.)
- **Every state per screen.** default / **loading (skeleton)** / **empty** /
  **error** / success — never only the happy path. Handle offline.
- **Performance is native-grade.** Virtualized lists (**FlatList/FlashList**) with
  a stable `keyExtractor`; animations on the **UI thread** (**Reanimated** /
  native driver); **expo-image** (sized + cached); Hermes on. No layout animation
  on the JS thread, no unbounded `.map()` over large data.
- **Secure by default.** Tokens/secrets in **expo-secure-store** (Keychain/
  Keystore) — never AsyncStorage, never bundled in JS. Ask for permissions
  **in context**, with a rationale string, and degrade gracefully if denied.
- **Accessible & tactile.** Touch targets **>= 44x44pt**, accessibility
  labels/roles, `reduce-motion` respected, safe-area insets honored.
- **Ship through EAS.** Config via `app.config` + **EAS env**; builds/updates/
  store submission via **EAS build / update / submit**. OTA updates are for JS
  only — native changes need a new build.

**Prototype fast:** use the **`mockup-app-skill`** (when available) to sketch the
app's screens/flow before wiring real data. Reuse existing components/tokens
before hand-rolling UI.

If a task would introduce a WebView-as-app, an untyped route, a plaintext secret,
a non-virtualized long list, a JS-thread animation, or a missing state — **stop
and fix it first** (see `anti-patterns.md`).
