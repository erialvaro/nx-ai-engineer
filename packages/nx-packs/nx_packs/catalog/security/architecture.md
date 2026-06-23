# Architecture — Application Security

Define trust boundaries and a lightweight threat model per feature. External input crosses a validation boundary; data access goes through a parameterized repository; authorization is centralized; secrets are injected from a vault; outbound calls pass an SSRF allow-list.
