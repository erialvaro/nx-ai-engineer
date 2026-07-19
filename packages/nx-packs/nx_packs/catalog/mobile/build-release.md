# Build & Release (EAS)

Ship through **EAS** — build, update (OTA), and submit — never ad-hoc local
archives with debug keys.

## Build (`eas build`)

- Profiles in `eas.json`: `development` (dev client), `preview` (internal/QA),
  `production` (store). Distinct bundle ids/schemes per env where useful.
- Secrets/config via **EAS environment variables & secrets**, read in
  `app.config.ts` — never commit signing keys or API secrets.
- iOS credentials & Android keystore managed by EAS (let EAS hold them); keep a
  documented recovery path.

## Update (`eas update`) — OTA

- OTA ships **JavaScript/asset** changes only, mapped to a **runtime version**.
  **Native changes** (new native module, permission, SDK bump) require a **new
  build** — never OTA across a runtime-version boundary.
- Use release channels/branches aligned to build profiles.

## Submit (`eas submit`) & store readiness

- **iOS**: correct bundle id, version + build number, privacy nutrition labels,
  usage-description strings, screenshots, TestFlight before production.
- **Android**: applicationId, versionCode/versionName, target API level, data-
  safety form, adaptive icon, closed testing track first.
- Bump versions every release; keep a changelog; verify the production build on a
  **real device** before submitting.
