# Accessibility (mobile)

Accessibility is a **gate**, not a nice-to-have — VoiceOver (iOS) and TalkBack
(Android) users must be able to complete every core flow.

- **Touch targets >= 44x44pt** (iOS HIG) / ~48dp (Android). Space tappables so
  they don't collide.
- **Labels & roles**: every interactive element has an `accessibilityLabel` and an
  `accessibilityRole` (`button`, `link`, `header`, `image`…). Group related nodes
  with `accessible`; set `accessibilityHint` where the action isn't obvious.
- **State**: expose `accessibilityState` (disabled/selected/checked/busy) and
  announce important changes (`AccessibilityInfo.announceForAccessibility`).
- **Contrast**: text and UI meet WCAG-equivalent contrast in **light and dark**.
- **Dynamic type**: respect the OS font-scale (`allowFontScaling`); layouts don't
  break at large text sizes.
- **Reduce motion**: check `AccessibilityInfo.isReduceMotionEnabled` and drop/soften
  non-essential animation.
- **Safe areas**: honor notches/home indicator via `SafeAreaView` /
  `useSafeAreaInsets`; nothing critical under the status bar or home indicator.
- **Focus order** is logical; modals trap focus and restore it on dismiss.
