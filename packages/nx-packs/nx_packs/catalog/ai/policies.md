# Policies — AI / LLM Integration

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Treat model output as untrusted input — validate/sanitize before use.
- Never send secrets or unnecessary PII to a model; minimize the prompt.
- Guard against prompt injection from user/content sources.
- Bound cost and rate; set timeouts and fallbacks.
- Log prompts/responses without PII; allow opt-out.
