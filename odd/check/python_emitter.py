import dataclasses

import parso

from odd.addon import Addon
from odd.check import Check
from odd.check.path_emitter import AddonPath


@dataclasses.dataclass
class PythonModule(AddonPath):
    module: parso.python.tree.Module


class PythonEmitter(Check):
    _handles = {"addon_path"}
    _emits = {"python_module"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grammar_2 = parso.load_grammar(version="2.7")
        self._grammar_3 = parso.load_grammar(version="3.5")

    def _get_grammar(self, addon: Addon) -> parso.Grammar:
        return self._grammar_2 if addon.version < 11 else self._grammar_3

    def on_addon_path(self, addon_path):
        if addon_path.path.suffix != ".py":
            return
        with addon_path.path.open(mode="rb") as f:
            module = self._get_grammar(addon_path.addon).parse(f.read())
        yield PythonModule(addon_path.addon, addon_path.path, module)
