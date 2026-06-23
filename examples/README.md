# AIES Examples

Eight minimal, runnable examples. The Python ones add the framework to `sys.path`
themselves, so you can run them from anywhere:

```bash
python examples/02_create_engine.py
```

| # | File | Shows |
|---|------|-------|
| 1 | [01_create_agent.md](01_create_agent.md) | Create an agent (config + SDK) |
| 2 | [02_create_engine.py](02_create_engine.py) | Create an Engine (Dry→Test→Execute) |
| 3 | [03_create_workflow.py](03_create_workflow.py) | Create + register a Workflow |
| 4 | [04_create_adapter.py](04_create_adapter.py) | Create an Adapter (model-agnostic) |
| 5 | [05_create_plugin.py](05_create_plugin.py) | Bundle a Plugin |
| 6 | [06_integrate_project.md](06_integrate_project.md) | Integrate a new project |
| 7 | [07_run_pipeline.py](07_run_pipeline.py) | Run the full pipeline |
| 8 | [08_update_brain.py](08_update_brain.py) | Update the Project Brain |

See `packages/nx-cli/nx_cli/_template/docs/` for the full guides (SDK_GUIDE, ENGINE_GUIDE,
WORKFLOW_GUIDE, PLUGIN_GUIDE, PROJECT_BRAIN).
