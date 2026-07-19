# Screen spec — <Screen name>

A buildable brief for one screen. Fill every section; "n/a" is a valid answer but
silence is not.

## Purpose
What the user accomplishes here, in one sentence.

## Route & navigation
- Path / route name + typed params:
- How it's reached (from where) and how it's left (back path):
- Deep link (scheme + path):

## Data
- Queries (source, key, cache/offline behavior):
- Mutations (optimistic? invalidation?):
- Loading strategy (skeleton / spinner / cached-first):

## States (required)
- **Loading** (skeleton):
- **Empty**:
- **Error** (message + retry):
- **Success / default**:
- **Offline**:

## Layout & tokens
- Sections/components (reuse existing?):
- Theme tokens used (light + dark):
- Reference profile applied (id) and how it was adapted:

## Interactions & animation
- Gestures / transitions (UI-thread / Reanimated):
- Reduce-motion behavior:

## Permissions
- Requested (when + rationale) and denied-path behavior:

## Accessibility
- Labels/roles, touch targets (>=44pt), focus order, safe-area, dynamic type:

## Done when
- Boots on iOS + Android, all states present, a11y + perf gates pass.
