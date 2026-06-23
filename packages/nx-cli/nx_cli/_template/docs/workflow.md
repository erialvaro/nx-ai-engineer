# The Mandatory Workflow

**NEVER implement immediately.** Every development request must pass through
this pipeline. No stage may be skipped.

```
1. Audit            Discover the real architecture (no assumptions).
2. Discovery        Find reusable components & existing patterns.
3. Impact analysis  What breaks? What's the blast radius?
4. Risk             Security, data, compatibility, tenant/PII.
5. Planning         Decompose into scoped subtasks.
6. Subtasks         One owner each, no scope overlap.
7. Agents           Select the responsible agents.
8. Order            Dependency-correct execution order.
9. Implement        Incrementally, in worktree lanes.
10. Tests           Add coverage; run the suite.
11. Review          Consolidated diff review.
12. Consolidate     Integrate lanes; resolve conflicts.
13. Document        Update docs / changelog / ADRs.
14. Final report    Summary, impact, risks, next steps.
```

## How the tooling maps to the pipeline
| Stage | Command |
|-------|---------|
| 1 Audit | `python tools/orchestrator.py audit` |
| 2–8 Plan | `python tools/orchestrator.py plan "<goal>"` |
| 9 Implement | `python tools/orchestrator.py worktree --plan <task-id>` then agents work |
| 10 Tests | project's own test command |
| 11 Review | `python tools/orchestrator.py review` |
| 12 Consolidate | Delivery agent + git |
| 13 Document | Docs agent |
| 14 Report | summarize the task file + review report |

## Rule of thumb
The orchestrator produces **plans, scaffolding and reports** — never product
code. Humans/AI agents implement; the framework keeps them safe, scoped and
coordinated.
