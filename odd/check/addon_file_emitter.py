import dataclasses
import pathlib

from odd.addon import Addon
from odd.check.path_emitter import AddonPath
from odd.check import Check


def _validate_data_file_params(params):
    if not set(params) == {"addon", "path"}:
        raise ValueError("Invalid params")
    if not isinstance(params["addon"], Addon):
        raise TypeError("Expected `addon` to be an instance of `Addon`")
    if not isinstance(params["path"], pathlib.Path):
        raise TypeError("Expected `path` to be an instance of `pathlib.Path`")


@dataclasses.dataclass
class DataFile(AddonPath):
    ...


@dataclasses.dataclass
class DemoFile(AddonPath):
    ...


class AddonFileEmitter(Check):
    _handles = {"addon"}
    _emits = {"data_file", "demo_file"}

    def on_addon(self, addon):
        # TODO: Handle `init`, `init_xml`, `demo_xml`.
        for path in addon.data_files:
            yield DataFile(addon, path)
        for path in addon.demo_files:
            yield DemoFile(addon, path)
