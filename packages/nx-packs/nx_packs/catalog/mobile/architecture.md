# Architecture — React Native + Expo

**Managed workflow, New Architecture, TypeScript.** Prefer Expo's managed workflow
on the current SDK with the New Architecture (Fabric/TurboModules) enabled. Eject
to a bare/prebuild workflow only with a documented reason (a native dependency
Expo can't provide via a config plugin).

## Project layout (expo-router)

```
app/                # routes (file-based); layouts in _layout.tsx
  (tabs)/           # grouped tab routes
  [id].tsx          # dynamic route
components/         # reusable UI (presentational)
features/           # feature modules (screen logic + hooks)
lib/                # api client, storage, utils
theme/              # tokens: colors (light/dark), spacing, type
hooks/              # shared hooks
app.config.ts       # dynamic Expo config (env-aware)
eas.json            # build/submit profiles
```

## Configuration

- **`app.config.ts`** (not static `app.json`) so config reacts to env — bundle id,
  scheme, icons, splash, plugins. Read secrets from **EAS env**, never commit them.
- **TypeScript strict**; path aliases via `tsconfig` + `babel-plugin-module-resolver`.
- **One API layer** in `lib/api` (typed client); screens never call `fetch` directly.

## Principles

- **Screens are thin**: they compose components and call hooks; business logic
  lives in `features/*/hooks` and `lib`. Presentational components take props, own
  no data.
- **Platform differences** via `Platform.select` or `*.ios.tsx` / `*.android.tsx`
  files — keep them small and explicit.
- **Design tokens are the single source of truth** (see the `design-references`
  pack for a starting palette/type); light + dark derive from the OS scheme.
