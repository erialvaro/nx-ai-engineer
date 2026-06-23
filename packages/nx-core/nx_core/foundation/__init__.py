"""Foundation layer — shared primitives (paths, IO, git, config).

Logical home for the cross-cutting utilities; re-exports the package's top-level
modules so they can be reached as a cohesive layer.

New code should import from here:
    from nx_core.foundation import util, config
Equivalent top-level access also works:
    from nx_core import util
"""
from .. import config, util

__all__ = ["util", "config"]
