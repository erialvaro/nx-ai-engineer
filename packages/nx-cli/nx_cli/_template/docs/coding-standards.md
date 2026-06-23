# Coding Standards

> The golden rule: **match the surrounding code.** This file records project
> conventions that aren't obvious from a single file. If the project already
> has a style guide / linter config, that is authoritative — link it and keep
> this file to the deltas.

## Conventions
- Follow the existing formatter/linter (Prettier, Black, gofmt, etc.). Never
  hand-format against the configured tool.
- Match existing naming, file layout and import ordering.
- Keep functions small; one responsibility each.
- No dead code, no commented-out blocks left behind.

## Error handling & logging
- Handle errors at boundaries; fail closed on security-relevant paths.
- Preserve existing logging; never silence or remove logs.
- Never log secrets or PII.

## Tests
- New behavior ships with tests. Test behavior, not internals.
- Keep tests deterministic.

## Comments
- Explain *why*, not *what*. Match the file's existing comment density.

## Authoritative configs (link)
- Linter/formatter config:
- Pre-commit hooks:
- EditorConfig:
