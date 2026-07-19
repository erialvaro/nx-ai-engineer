# Mobile Engineering Pack (React Native + Expo)

Domain knowledge for building **native iOS/Android apps** with **React Native +
Expo** — the standard the `mobile` agent executes against. Like every pack, it is
knowledge, not code: it organizes how any model builds a mobile app correctly.

## Scope

- **Architecture** — Expo managed workflow, New Architecture, project layout,
  `app.config`, environment/config, TypeScript.
- **Navigation** — expo-router (file-based) / react-navigation, typed routes &
  params, deep links, Android back, tabs/stacks/modals.
- **State & data** — server state (TanStack Query), offline-first, caching,
  secure storage, forms.
- **Native modules & permissions** — Expo modules, camera/location/notifications,
  in-context permission requests, config plugins.
- **Performance** — FlatList/FlashList, Reanimated on the UI thread, expo-image,
  Hermes, startup and memory.
- **Build & release** — EAS build / update (OTA) / submit, iOS & Android store
  requirements, versioning, secrets.
- **Accessibility** — touch targets, labels/roles, reduce-motion, safe areas.

## Tooling

React Native + Expo, **expo-router**, **NativeWind** (Tailwind for RN), **React
Native Reanimated**, **TanStack Query**, **expo-secure-store**, **expo-image**,
**EAS**. Prototype flows with the **`mockup-app-skill`** (when installed). Pairs
with **`design-references`** — palette/type/mood profiles are platform-agnostic
and feed the mobile theme.

## Usage

```bash
nxai pack add mobile          # install into .ai-project-assistant/packs
nxai contract --agent mobile "app de agendamento para um salão de beleza"
```

The pack auto-attaches to the **`mobile`** agent via `applies_to`; `nxai new`/the
analyzer route RN/Expo files (App entry, `app.json`/`app.config.*`, `eas.json`,
`metro.config.*`, `screens/`, `navigation/`, `*.native.*`) to it.
