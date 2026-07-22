# Device Matrix

Every key route is verified across **all** of these. Mobile-first: start at the
smallest width and work up. Widths are CSS pixels (the Playwright viewport).

## Raw viewports (the non-negotiable six)

| Label            | Width × Height | Represents                         |
|------------------|:--------------:|------------------------------------|
| Small phone      | 360 × 640      | Budget Android, smallest realistic |
| Modern phone     | 390 × 844      | iPhone 12–16, most phones          |
| Tablet portrait  | 768 × 1024     | iPad portrait                      |
| Tablet landscape | 1024 × 768     | iPad landscape / small laptop      |
| Laptop           | 1366 × 768     | Most common laptop screen          |
| Desktop          | 1920 × 1080    | Full desktop                       |

## Named devices (Playwright `devices[...]`, real DPR + UA)

- **iPhone SE** — smallest modern iOS, 375×667 @2x (the classic breakpoint trap)
- **iPhone 15 Pro / iPhone 16 Pro** — 393×852 @3x
- **Pixel 9** — 412×915 @3.5x (Android reference)
- **Galaxy S24** — 360×780 @3x (narrow Android)
- **iPad (gen)** — 768×1024 @2x portrait, plus landscape

## Browser engines

Run the matrix on **Chromium**, **Firefox** and **WebKit** (WebKit ≈ Safari/iOS —
where most iOS-only bugs hide). At minimum, Chromium for the full matrix + WebKit
for the phone widths.

## Emulators (optional, for real-device fidelity)

When emulation isn't enough (native gestures, real Safari quirks, foldables):

- **Android Studio emulator** — Pixels, tablets, foldables.
- **Genymotion** — lighter Android emulation.
- Playwright device mode covers the vast majority of React/web cases without an
  emulator; reach for these only when a real engine/DPR difference is suspected.

## Orientation

Test **portrait and landscape** for phone and tablet widths — landscape phones and
tablet-landscape are where headers and modals most often break.
