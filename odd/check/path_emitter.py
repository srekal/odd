import dataclasses
import pathlib

from odd.addon import Addon
from odd.artifact import Artifact
from odd.check import Check
from odd.utils import list_files


@dataclasses.dataclass
class AddonPath(Artifact):
    addon: Addon
    path: pathlib.Path


class AddonPathEmitter(Check):
    _handles = {"addon"}
    _emits = {"addon_path"}

    def on_addon(self, addon):
        for path in list_files(addon.path, list_dirs=True):
            yield AddonPath(addon, path)
