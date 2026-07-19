# Navigation

Use **expo-router** (file-based, recommended) or **react-navigation** with **typed**
routes and params. Navigation correctness is a release gate.

## Rules

- **Typed routes & params.** With expo-router use typed routes; with react-
  navigation declare a `ParamList` and type every `navigation`/`route`. No
  stringly-typed params.
- **Every screen reachable, with a back path.** No dead ends. A modal/detail can
  always be dismissed; a flow can always be exited.
- **Android hardware back** is handled everywhere (expo-router/react-navigation do
  this by default — don't break it with custom gesture handlers).
- **Deep links & universal links** resolve to the right screen; define the `scheme`
  and a linking config; test cold-start deep links.
- **Structure**: a root stack; tabs via a `(tabs)` group; modals as a presentation
  option; auth as a separate group gated by session state (redirect, don't render
  protected screens).

## Patterns

- **Auth gating**: a root `_layout` reads session and redirects unauthenticated
  users to `(auth)`; never mount protected routes for signed-out users.
- **Params carry ids, not objects**: pass an `id`, then fetch in the screen (keeps
  deep links and state restoration working).
- **Header & safe area**: use the navigator header or a screen header inside
  `SafeAreaView`/`useSafeAreaInsets`; never hard-code status-bar height.
