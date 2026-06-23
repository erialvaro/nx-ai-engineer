"""Example 5 — Bundle a Plugin (agents + tools + observers via setup(sdk)).

Run: python examples/05_create_plugin.py
"""
from _bootstrap import aies_home  # noqa: F401

import nx_sdk as sdk


class SecurityPackPlugin:
    name = "security-pack"

    def setup(self, sdk_mod):
        sdk_mod.register_agent("pentester", {
            "title": "Pentester", "keywords": ["pentest", "vulnerability"],
            "route_globs": ["**/security/**"], "read_only": False,
        })
        sdk_mod.register_tool("sast", lambda path: [f"finding in {path}"])
        sdk_mod.on("delivery.completed", self._on_delivery)
        self.delivered = []

    def _on_delivery(self, event):
        self.delivered.append(event.payload)


if __name__ == "__main__":
    plugin = SecurityPackPlugin()
    sdk.register_plugin("security-pack", plugin)  # setup() runs automatically

    print("agent registered:", "pentester" in sdk.registry("agents"))
    print("tool works:", sdk.get_tool("sast")("api/auth.py"))
    print("event handlers registered:", len(sdk.event_handlers()))
    sdk.reset()  # restore clean state (e.g. between tests)
    print("after reset, agents:", sdk.registry("agents"))
