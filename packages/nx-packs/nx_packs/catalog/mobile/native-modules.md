# Native Modules & Permissions

## Prefer Expo modules

Use Expo's modules before any third-party native dependency: `expo-camera`,
`expo-location`, `expo-notifications`, `expo-image-picker`, `expo-av`,
`expo-file-system`, `expo-secure-store`, `expo-haptics`, `expo-sensors`. They work
in the managed workflow and via **config plugins** at build time.

## Permissions — in context, with rationale

- Request a permission **at the moment it's needed**, not on app launch, and only
  after explaining **why** (a rationale screen/sheet). iOS `Info.plist` usage
  strings and Android permissions are declared via the module's config plugin.
- **Degrade gracefully** when denied: the app keeps working with reduced function
  and offers a path to Settings (`Linking.openSettings()`). Never trap the user.
- Re-check permission status on focus (the user may change it in Settings).

## Notifications

- `expo-notifications` for local + push; register for a push token, store it
  server-side, handle foreground/background/response. Test on a **real device**
  (push doesn't work in the simulator).

## Config plugins & bare escape hatch

- Add native capabilities via **config plugins** (`app.config` `plugins: []`).
- If a dependency has no Expo module/plugin, use **prebuild** (continuous native
  generation) rather than a one-way eject — document the reason in an ADR.
