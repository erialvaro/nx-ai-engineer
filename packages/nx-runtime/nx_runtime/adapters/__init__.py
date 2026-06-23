"""Adapters — the boundary with AI models/CLIs. The core talks only to the
`AgentAdapter` protocol, never to a specific provider. DryRunAdapter is the safe
default. Populated in PR-2.
"""
