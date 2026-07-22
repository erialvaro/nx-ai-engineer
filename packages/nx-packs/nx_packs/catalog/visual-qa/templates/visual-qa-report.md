# Visual-QA Report — {{route_or_feature}}

- **App / URL:** {{base_url}}
- **Date:** {{date}}
- **Browsers:** Chromium / Firefox / WebKit
- **Result:** {{PASS | FAIL}} — {{n_passed}}/{{n_checks}} checks green

## Summary

| Gate                         | Result | Notes                          |
|------------------------------|:------:|--------------------------------|
| No horizontal overflow       |  ✅/❌  |                                |
| Nothing clipped / off-screen |  ✅/❌  |                                |
| Contrast (light + dark)      |  ✅/❌  |                                |
| Keyboard + visible focus     |  ✅/❌  |                                |
| Lighthouse >= 95 (all)       |  ✅/❌  | P __ / A __ / BP __ / SEO __   |
| CLS < 0.1                    |  ✅/❌  | CLS __ · LCP __                |
| Visual baselines (BackstopJS)|  ✅/❌  |                                |

## Findings (before → fix → after)

### 1. {{short title}}
- **Route / viewport:** {{route}} @ {{width}}×{{height}} ({{device}})
- **Defect:** {{what broke, with the measured value / selector}}
- **Before:** `{{path/to/before.png}}`
- **Fix (by {{responsive|frontend|mobile}}):** {{what changed}}
- **After:** `{{path/to/after.png}}`
- **Re-verified:** ✅

<!-- repeat per finding -->

## Device matrix coverage

| Route | 360×640 | 390×844 | 768×1024 | 1024×768 | 1366×768 | 1920×1080 |
|-------|:-------:|:-------:|:--------:|:--------:|:--------:|:---------:|
| {{/}} |   ✅    |   ✅    |    ✅    |    ✅    |    ✅    |    ✅     |

## Gate in CI
- [ ] Playwright device-matrix spec green in CI
- [ ] Lighthouse CI assertions (>= 0.95) green
- [ ] BackstopJS diff green (baselines current)
