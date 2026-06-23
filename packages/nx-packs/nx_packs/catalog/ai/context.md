# Context — AI / LLM Integration

When the product calls an AI model, treat model output as untrusted, never send secrets/PII without need, and bound cost.

## Non-negotiables
- Treat model output as untrusted input — validate/sanitize before use.
- Never send secrets or unnecessary PII to a model; minimize the prompt.
- Guard against prompt injection from user/content sources.
- Bound cost and rate; set timeouts and fallbacks.
- Log prompts/responses without PII; allow opt-out.

## Always verify
- Model output validated before use
- No secrets/PII in prompts
- Prompt-injection mitigations present
- Cost/rate limits + timeouts set
- Logging excludes PII
