import dataclasses
import pathlib

from odd.addon import Addon
from odd.artifact import Artifact
from odd.check import Check
from odd.utils import list_files


def _validate_path_params(params):
    if not set(params) == {"addon", "path"}:
        raise ValueError("Invalid params")
    if not isinstance(params["addon"], Addon):
        raise TypeError("Expected `addon` to be an instance of `Addon`")
    if not isinstance(params["path"], pathlib.Path):
        raise TypeError("Expected `path` to be an instance of `pathlib.Path`")


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
