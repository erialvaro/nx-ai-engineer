# State & Data

## Server state

- **TanStack Query** (react-query) for all remote data: caching, retries,
  background refetch, pagination/infinite lists. Screens read from hooks
  (`useQuery`/`useMutation`), never ad-hoc `fetch` + `useState`.
- **Offline-first** where it matters: persist the query cache, show cached data
  immediately, reconcile on reconnect. Surface an offline banner; queue mutations.

## Client state

- Local UI state with `useState`/`useReducer`; cross-screen app state with a light
  store (Zustand) — avoid Redux boilerplate unless the app is large.
- **Never** put server data in a global store as the source of truth — that's the
  query cache's job.

## Storage

- **Secrets/tokens → `expo-secure-store`** (Keychain/Keystore). Never AsyncStorage
  for anything sensitive; never bundle secrets in JS.
- **Non-sensitive cache/prefs → AsyncStorage / MMKV**. Namespace keys; version and
  migrate persisted shapes.

## Forms & validation

- Controlled forms with **react-hook-form**; schema validation with **zod**.
- Validate on blur/submit, show inline field errors, disable submit while pending,
  and show a success confirmation. Keyboard: `KeyboardAvoidingView` + correct
  `keyboardType`/`autoComplete`/`textContentType` (enables iOS autofill).
