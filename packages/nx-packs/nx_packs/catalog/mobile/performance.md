# Performance

Mobile performance is a **release gate** — jank and slow startup read as a broken
app.

## Lists

- **Virtualize** every non-trivial list: `FlatList`/`SectionList`, or **FlashList**
  for large/complex rows. Never `.map()` a large array into views inside a
  `ScrollView`.
- Provide a **stable `keyExtractor`** (id, not index), `getItemLayout` when rows
  are fixed-height, `windowSize`/`initialNumToRender` tuned, and memoized row
  components (`React.memo`) with stable callbacks.

## Animation

- **React Native Reanimated** (worklets on the **UI thread**) or the **native
  driver** (`useNativeDriver: true`). **Never** animate layout props on the JS
  thread — animate `transform`/`opacity`. Honor `reduce-motion`.
- Gestures via `react-native-gesture-handler`.

## Images & assets

- **`expo-image`** with explicit dimensions, `contentFit`, and caching; use
  appropriately sized assets and `placeholder`/blurhash. Unsized images cause
  layout shift and memory spikes.

## Startup & memory

- **Hermes** engine on; keep the JS bundle lean (lazy-load heavy screens);
  minimize work before first paint; splash screen hidden only when ready.
- **No leaks**: clean up listeners, timers, and subscriptions in effect cleanups;
  cancel in-flight requests on unmount.
- Measure with the **dev/EAS profiler** and Flipper/React DevTools; watch frame
  drops and re-renders, not vibes.
