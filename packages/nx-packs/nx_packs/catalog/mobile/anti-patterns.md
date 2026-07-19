# Anti-patterns (stop and fix)

- **WebView-as-app** — wrapping a website in a `WebView` and shipping it as the
  product. Build native screens.
- **Ejecting reflexively** — leaving the managed workflow for something a config
  plugin/prebuild would solve. Document the real reason or don't.
- **Untyped navigation** — stringly-typed routes/params, screens with no back
  path, breaking the Android hardware back button.
- **Plaintext secrets** — tokens in AsyncStorage, hard-coded API keys, secrets
  bundled in JS. Use `expo-secure-store` + EAS secrets.
- **Non-virtualized long lists** — `.map()` over large data inside a `ScrollView`;
  missing/`index` keys. Use FlatList/FlashList with a stable `keyExtractor`.
- **JS-thread animation** — animating layout props without the native driver/
  Reanimated, causing jank. Animate transform/opacity on the UI thread.
- **Unsized/uncached images** — raw `Image` with no dimensions; layout shift and
  memory spikes. Use `expo-image`, sized + cached.
- **Happy-path-only screens** — no loading/empty/error/offline states.
- **Permission on launch** — requesting camera/location/notifications at startup
  with no context, and breaking when denied.
- **OTA across native changes** — shipping a native change via `eas update`
  instead of a new build (runtime-version mismatch → crashes).
- **Ignoring safe areas / font scale** — hard-coded status-bar height; layouts
  that break under Dynamic Type.
- **Hard-coded style values** — colors/spacing inline in screens instead of theme
  tokens (light + dark).
